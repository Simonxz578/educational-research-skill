"""Run the reproducible research-pack pipeline, retaining honest shortfalls."""

import csv
import json
import logging
from pathlib import Path
from .models import Source
from .search import eric, crossref, openalex, semantic_scholar, google_scholar_workflow as scholar
from .utils.cache import Client, FetchError
from .ingest.extract import load
from .core.screen import deduplicate, screen
from .core.score import rank, score
from .core.selection import select_sources
from .core.quality import warnings, validate_compact, audit_draft
from .core.graph import Synthesis, construct, validate_graph
from .core.gaps import evaluate
from .citations.format import csl
from .citations.audit import audit as citation_audit
from .core.discovery import DiscoveryObservation, load_observations
from .core.protocol import SearchProtocol, provisional
from .core.pack import finalise


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def metric_columns(source):
    journal = next(
        (m for m in source.metrics if m.name in {"JIF", "SJR", "CiteScore", "h5-index"}), None
    )
    article = next((m for m in source.metrics if m.name == "article_citations"), None)
    fwci = next((m for m in source.metrics if m.name == "FWCI"), None)
    return {
        "journal_metric_name": journal.name if journal else "JIF: NOT VERIFIED",
        "journal_metric_value": journal.value if journal else None,
        "journal_metric_year": journal.year if journal else None,
        "journal_metric_source": journal.source if journal else None,
        "journal_quartile": journal.quartile if journal else None,
        "journal_quartile_source": journal.source if journal and journal.quartile else None,
        "article_citations": article.value if article else None,
        "count_source": article.source if article else None,
        "check_date": article.checked_at if article else None,
        "fwci_if_verified": fwci.model_dump() if fwci else None,
    }


def run(
    config,
    output_dir,
    sources_path=None,
    synthesis_path=None,
    draft_path=None,
    scholar_csv=None,
    providers=("eric", "google-scholar", "crossref", "openalex"),
    include_draft=False,
    client=None,
    protocol_path=None,
    discovery_records=None,
    execution_context=None,
):
    root_output = Path(output_dir)
    root_output.mkdir(parents=True, exist_ok=True)
    output = root_output / "evidence" if config.presentation == "roadmap" else root_output
    output.mkdir(parents=True, exist_ok=True)
    if config.presentation == "roadmap":
        output.chmod(0o700)
    previous_review = output / "Visual_Review.json"
    if previous_review.exists():
        from .core.reading import sha256_file

        previous_review.rename(
            output / ("Visual_Review.previous." + sha256_file(previous_review)[:12] + ".json")
        )
    # Avoid stale essay files from a previous explicit drafting run contaminating a default run.
    if not include_draft and config.mode != "draft" and (output / "Draft_Manuscript.md").exists():
        raise ValueError("Output directory contains an earlier draft; choose a fresh output directory")
    logs, sources = [], load(sources_path) if sources_path else []
    protocol = (
        SearchProtocol.model_validate_json(Path(protocol_path).read_text())
        if protocol_path
        else provisional(config)
    )
    if protocol.quantity_intent and protocol.quantity_intent != config.quantity_contract:
        protocol.amendments.append(
            {
                "previous_quantity_intent": protocol.quantity_intent,
                "quantity_change": config.quantity_contract,
                "reason": "Current explicit quantity request governs this run; original intent is retained in protocol history",
            }
        )
    protocol.quantity_intent = config.quantity_contract
    dump(output / "search_protocol.json", protocol.model_dump())
    logs.append(
        {"provider": "protocol", "status": "PROSPECTIVE_PROTOCOL", "prepared_at": protocol.prepared_at}
    )
    observations = load_observations(discovery_records) if discovery_records else []
    for observation in observations:
        if not observation.issues():
            logs.append(
                {
                    "provider": observation.provider,
                    "status": "ERIC_SEARCHED"
                    if observation.provider == "ERIC"
                    else "SCHOLAR_OBSERVATION_IMPORTED",
                    "query": observation.query,
                    "date": observation.executed_at,
                    "filters": observation.filters,
                    "ids": [r.get("id") for r in observation.results],
                    "observed": len(observation.results),
                    "artifact_sha256": observation.artifact_sha256,
                    "provenance": "imported archived observation; not a new live request",
                }
            )
        else:
            logs.append(
                {
                    "provider": observation.provider,
                    "status": "INVALID_OBSERVATION",
                    "issues": observation.issues(),
                }
            )
    if scholar_csv:
        imported, entries = scholar.import_csv(scholar_csv)
        sources.extend(imported)
        logs.extend(entries)
    own_client = client is None
    client = client or Client(output / ".cache", offline=config.offline)
    if config.offline:
        logs.append({"provider": "all", "status": "OFFLINE", "date": config.search_date, "observed": 0})
    else:
        if "eric" in providers:
            queries = [
                eric.query(
                    config.topic,
                    config.descriptors,
                    config.peer_reviewed,
                    config.year_from,
                    config.year_to,
                    config.education_level,
                    config.geography,
                )
            ]
            # Theory-first plus newest-evidence expansions, bounded by the stated quota.
            queries += [
                eric.query(
                    f"({config.topic}) AND (theory OR framework)",
                    config.descriptors,
                    config.peer_reviewed,
                    config.year_from,
                    config.year_to,
                    config.education_level,
                    config.geography,
                ),
                eric.query(
                    config.topic,
                    config.descriptors,
                    config.peer_reviewed,
                    max(
                        config.year_from or 0,
                        min(config.year_to or int(config.search_date[:4]), int(config.search_date[:4]))
                        - 3,
                    ),
                    config.year_to,
                    config.education_level,
                    config.geography,
                ),
            ]
            queries += [
                eric.query(
                    f"({config.topic}) AND (review OR critical OR null)",
                    config.descriptors,
                    config.peer_reviewed,
                    config.year_from,
                    config.year_to,
                    config.education_level,
                    config.geography,
                ),
                eric.query(
                    config.topic,
                    config.descriptors,
                    False,
                    config.year_from,
                    config.year_to,
                    config.education_level,
                    config.geography,
                ),
            ]
            retrieved = 0
            observed_ids = set()
            for index, q in enumerate(queries):
                if retrieved >= config.candidate_budget or (
                    index >= 3 and len(observed_ids) >= config.candidate_target
                ):
                    break
                remaining = config.candidate_budget - retrieved
                batch = min(
                    remaining,
                    max(5, config.candidate_target // 3)
                    if index < 3
                    else max(10, config.candidate_target - len(observed_ids)),
                )
                logs.append(
                    {
                        "provider": "ERIC",
                        "status": "SEARCH_BREADTH_DECISION",
                        "query": q,
                        "distinct_candidates_before": len(observed_ids),
                        "candidate_target": config.candidate_target,
                        "budget_remaining": remaining,
                        "requested_rows": batch,
                        "reason": "Initial general/theory/recent coverage"
                        if index < 3
                        else "Broaden after deduplication/candidate shortfall",
                    }
                )
                try:
                    records, entries = eric.search(client, q, batch)
                    sources.extend(records)
                    retrieved += len(records)
                    observed_ids.update(s.eric_id for s in records if s.eric_id)
                    logs.extend(entries)
                    observations.extend(
                        DiscoveryObservation.model_validate(e["observation"])
                        for e in entries
                        if e.get("observation")
                    )
                    if not records:
                        logs.append({"provider": "ERIC", "status": "SEARCH_EXPANSION_EMPTY", "query": q})
                except FetchError as exc:
                    logs.append(
                        {
                            "provider": "ERIC",
                            "status": "ERIC_UNAVAILABLE",
                            "query": q,
                            "date": config.search_date,
                            "error": str(exc),
                            "observed": 0,
                        }
                    )
            logs.append(
                {
                    "provider": "ERIC",
                    "status": "SEARCH_BREADTH_COMPLETE",
                    "retrieved_candidates": retrieved,
                    "distinct_eric_ids": len(observed_ids),
                    "candidate_target": config.candidate_target,
                    "budget": config.candidate_budget,
                    "coverage_shortfall": max(0, config.candidate_target - len(observed_ids)),
                }
            )
        if "crossref" in providers:
            for s in sources:
                try:
                    before = len(s.provenance)
                    crossref.enrich(client, s)
                    if len(s.provenance) == before:
                        continue
                    logs.append(
                        {
                            "provider": "Crossref",
                            "status": "METADATA_ENRICHED",
                            "id": s.id,
                            "date": config.search_date,
                            "identity": s.identity,
                        }
                    )
                except (FetchError, ValueError) as exc:
                    s.warnings.append("Crossref verification unavailable")
                    logs.append(
                        {"provider": "Crossref", "status": "FAILED", "id": s.id, "error": str(exc)}
                    )
        for provider, adapter in [("openalex", openalex), ("semantic-scholar", semantic_scholar)]:
            if provider in providers:
                for s in sources:
                    try:
                        before = len(s.metrics)
                        adapter.enrich(client, s)
                        if len(s.metrics) > before:
                            logs.append(
                                {
                                    "provider": provider,
                                    "status": "METADATA_ENRICHED",
                                    "id": s.id,
                                    "date": config.search_date,
                                }
                            )
                    except (FetchError, ValueError):
                        s.warnings.append(f"{provider}: article metrics unavailable")
    # Always write a manual plan; a planned query is never a searched result.
    scholar_plan = scholar.plan(config.topic, config.year_from)
    logs.append(
        {"provider": "Google Scholar", "status": "SCHOLAR_MANUAL_PLAN_ONLY", "date": config.search_date}
    )
    if not any(o.provider == "Google Scholar" and not o.issues() for o in observations):
        logs.append(
            {
                "provider": "Google Scholar",
                "status": "GOOGLE_SCHOLAR_NOT_CHECKED",
                "date": config.search_date,
                "observed": 0,
            }
        )
    (output / "scholar_search_plan.md").write_text(
        "# Scholar manual discovery plan\n\n"
        "GOOGLE_SCHOLAR_NOT_CHECKED unless a separate dated observation/export log is present.\n"
        "Open queries interactively; follow Cited by, Related articles, All versions and publication filters.\n\n"
        + "\n".join(f"- [{q['query']}]({q['url']})" for q in scholar_plan),
        encoding="utf-8",
    )
    # Revalidate after enrichment; mutations cannot bypass model invariants.
    sources = [Source.model_validate(s.model_dump()) for s in sources]
    found = len(sources)
    unique, duplicates = deduplicate(sources)
    eligible, rejected = screen(unique, config.topic)
    ranked = rank(eligible, config.topic)
    from .fulltext.acquire import Acquirer, write_access_outputs
    from .fulltext.abstracts import acquire_abstract

    acquisition_limit = config.full_text_limit or config.candidate_budget
    if config.full_text_mode != "off" and not config.offline:
        acquirer = Acquirer(output / "full_text", metadata_client=client)
        try:
            attempted = 0
            for source in ranked:
                if source.synthetic:
                    continue
                if attempted >= acquisition_limit:
                    break
                acquirer.acquire(source, max_routes=config.full_text_max_routes)
                acquire_abstract(source, output / "abstracts", metadata_client=client, acquirer=acquirer)
                attempted += 1
        finally:
            acquirer.close()
    elif config.full_text_mode != "off":
        local_reader = Acquirer(output / "full_text")
        try:
            for source in ranked[:acquisition_limit]:
                local_locations = [loc for loc in source.full_text_locations if loc.route == "user"]
                if local_locations and not source.acquisition:
                    local_reader.acquire(source, local_locations, max_routes=config.full_text_max_routes)
        finally:
            local_reader.close()
    for source in ranked:
        acquire_abstract(source, output / "abstracts")
    write_access_outputs(output, ranked, [s.id for s in ranked[acquisition_limit:]])
    included, candidates, selection = select_sources(ranked, config)
    dump(output / "Candidates.json", candidates)
    dump(output / "Source_Selection.json", selection.model_dump())
    deferred = [
        {"id": s.id, "reason": "Deferred after quota/diversity selection"}
        for s in ranked
        if s not in included
    ]
    excluded = duplicates + rejected + deferred
    if synthesis_path:
        synthesis = Synthesis.model_validate_json(Path(synthesis_path).read_text(encoding="utf-8"))
    else:
        synthesis = construct(included)
    from .core.reading import reading_audit
    from .core.gates import independent_key

    inspected = reading_audit(
        included,
        reader_ready=config.presentation == "roadmap" or config.strict_quality_gates,
        synthesis=synthesis,
    )
    qualified_ids = {row["source_id"] for row in inspected if row["qualified"]}
    selection.qualified_deep_read_K = len(
        {independent_key(source) for source in included if source.id in qualified_ids}
    )
    selection.shortfall = max(0, config.deep_review_requirement - selection.qualified_deep_read_K)
    selection.full_text_verified_K = selection.qualified_deep_read_K
    selection.full_text_provisional_P = (
        len(included) - selection.full_text_verified_K - selection.abstract_only_A
        if config.presentation == "roadmap"
        else 0
    )
    dump(output / "Source_Selection.json", selection.model_dump())
    graph_errors = []
    try:
        validate_graph(synthesis, included)
    except ValueError as exc:
        graph_errors.append(str(exc))
    included_ids = {s.id for s in included}
    for source in included:
        if not set(source.comparison_ids) <= included_ids:
            graph_errors.append(
                f"{source.id}: comparative sources absent from selected pack; increase reference target or review selection"
            )
    gaps = evaluate(synthesis.gaps, included, logs)
    compact_errors = validate_compact(included)
    if compact_errors:
        raise ValueError("; ".join(compact_errors))
    draft_text = Path(draft_path).read_text(encoding="utf-8") if draft_path else ""
    audit = {
        "found": found,
        "deduplicated": len(unique),
        "screened": len(unique),
        "excluded": len(excluded),
        "included": len(included),
        "full_text_verified": selection.full_text_verified_K,
        "user_supplied": sum(s.access == "USER_SUPPLIED" for s in included),
        "abstract_only": selection.abstract_only_A,
        "verified_quotes": sum(len(s.quotes) for s in included),
        "unresolved_references": [s.id for s in included if s.identity not in {"VERIFIED", "SYNTHETIC"}],
        "reference_target": config.quota,
        "source_selection": selection.model_dump(),
        "presentation": config.presentation,
        "reference_shortfall": max(
            0, config.quota - sum(s.identity in {"VERIFIED", "SYNTHETIC"} for s in included)
        ),
        "counterarguments": sum(
            s.role in {"counterargument", "counterexample", "contradiction", "null evidence"}
            for s in included
        ),
        "claim_coverage": {
            c.id: {
                "sources": len(c.source_ids),
                "evidence": len(c.evidence_ids),
                "needs_comparison": len(c.source_ids) < 2,
            }
            for c in synthesis.claims
        },
        "claims_requiring_review": [{"source": s.id, "warnings": warnings(s)} for s in included],
        "citation_audit": citation_audit(draft_text, included)
        if draft_text
        else {"scope": "Research pack bibliography, all matrix sources listed"},
        "synthetic": any(s.synthetic for s in included),
        "search_expansions": [e.get("query") for e in logs if e.get("query")],
        "scientific_review": "Agent/human critical reading required; exact span checks are not authenticity verification",
    }
    matrix = [{**s.public_record(), **score(s, config.topic), **metric_columns(s)} for s in included]
    dump(output / "Literature_Argument_Matrix.json", matrix)
    if matrix:
        with (output / "Literature_Argument_Matrix.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as stream:
            writer = csv.DictWriter(stream, fieldnames=list(matrix[0]))
            writer.writeheader()
            for row in matrix:
                writer.writerow(
                    {
                        k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                        for k, v in row.items()
                    }
                )
    else:
        (output / "Literature_Argument_Matrix.csv").write_text("id,title,identity\n")
    verified = [s for s in included if s.identity in {"VERIFIED", "SYNTHETIC"}]
    dump(output / "verified_references.csl.json", [csl(s) for s in verified])
    dump(
        output / "unresolved_references.json", [s.public_record() for s in included if s not in verified]
    )
    dump(
        output / "evidence_ledger.json",
        [
            {
                "source_id": s.id,
                "access": s.access,
                "segments": [
                    {**seg.model_dump(exclude={"text"}), "evidence_id": f"{s.id}:{seg.id}"}
                    for seg in s.segments
                ],
                "quotes": [q.model_dump() for q in s.quotes],
                "extractions": {k: v.model_dump() for k, v in s.extractions.items()},
            }
            for s in included
        ],
    )
    dump(output / "argument_graph.json", synthesis.model_dump())
    dump(output / "gap_evidence.json", gaps)
    dump(output / "search_log.json", logs)
    dump(output / "http_log.json", client.log)
    dump(output / "exclusions.json", excluded)
    dump(
        output / "journal_article_metrics.json",
        [
            {"id": s.id, "metrics": [m.model_dump() for m in s.metrics], **metric_columns(s)}
            for s in included
        ],
    )
    dump(output / "source_provenance.json", [{"id": s.id, "provenance": s.provenance} for s in included])
    dump(output / "revision_map.json", audit_draft(draft_text, included) if draft_text else [])
    # Explicit draft mode produces only a source-grounded structural scaffold; no invented empirical prose.
    if include_draft or config.mode == "draft":
        (output / "Draft_Manuscript.md").write_text(
            "# Draft scaffold - explicit opt-in\n\n"
            "Evidence-led planning scaffold; author must supply empirical material and write/review prose.\n\n"
            + "\n\n".join(
                f"## {c.id}\n{c.text}\n\nEvidence: {', '.join(c.evidence_ids)}\nBoundary: {c.qualification}"
                for c in synthesis.claims
            ),
            encoding="utf-8",
        )
    audit = finalise(
        output,
        config,
        included,
        synthesis,
        logs,
        observations,
        audit,
        graph_errors,
        draft_text,
        execution_context or {},
        protocol,
        selection,
    )
    if config.presentation == "roadmap":
        (root_output / "README.md").write_text(
            "# Research roadmap\n\n"
            + f"Selected {len(included)} of {config.quota} target; deep-reviewed {selection.qualified_deep_read_K} of {config.deep_review_requirement} required; "
            + f"{selection.full_text_verified_K} full-text verified; {selection.abstract_only_A} abstract only; {selection.quotation_count} verified micro-excerpts. "
            + audit["research_quality"]["label"]
            + ". Open Research_Roadmap.pdf. Complete editable evidence, candidates, provenance and QA are in evidence/.\n",
            encoding="utf-8",
        )
    if own_client:
        client.close()
    logging.info(
        "Included %s; verified target shortfall %s", len(included), audit["reference_shortfall"]
    )
    return audit
