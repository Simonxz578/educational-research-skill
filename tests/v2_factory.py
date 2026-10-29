"""TEST ONLY generated openly licensed corpus; never actual scholarly research."""

import json
from pathlib import Path
from educational_research.models import Source
from educational_research.core.graph import Synthesis
from educational_research.core.discovery import DiscoveryObservation, utc_now
from educational_research.core.reading import sha256_file
from .factories import source


def bundle(folder, count=10):
    prepared_at = utc_now()
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for n in range(1, count + 1):
        row = source(n).model_dump()
        pieces = {
            "claim": f"TEST ONLY source {n}. The synthetic authors distinguish reported study routines from observed learning outcomes; their central proposition concerns measurement boundaries, not an empirical effectiveness claim.",
            "method": f"TEST ONLY source {n}. This fictional worked example uses a survey of reported routines and separate hypothetical task observations, solely to illustrate differences between evidence types. No real participants or data exist.",
            "result": f"TEST ONLY source {n}. The illustrative finding is that a reported routine cannot establish an observed outcome. All examples are invented and labelled synthetic; no statistical effect or population result is asserted.",
            "limitation": f"TEST ONLY source {n}. These synthetic illustrations have no generalisability. Recall, selection and measurement differences would need investigation in actual research, and no causal interpretation is justified.",
            "counterpoint": f"TEST ONLY source {n}. A rival explanation concerns contextual opportunity rather than learners’ reported routines. This negative case is retained to show how disagreement constrains a proposed framework.",
        }
        path = folder / f"TEST_ONLY_{n:03}.txt"
        path.write_text(
            row["segments"][0]["text"]
            + "\n\n"
            + "\n\n".join(k.upper() + "\n" + v for k, v in pieces.items())
        )
        row["segments"] += [
            {
                "id": k,
                "text": v,
                "url": f"https://example.test/full/{n}",
                "locator": f"Synthetic section: {k}",
                "licence": "CC0 TEST ONLY",
            }
            for k, v in pieces.items()
        ]
        row["reading"] = {
            "source_id": row["id"],
            "access_status": "USER_SUPPLIED_FULL_TEXT",
            "document": {
                "source_url": f"https://example.test/full/{n}",
                "local_path": str(path.resolve()),
                "sha256": sha256_file(path),
                "version": "TEST ONLY synthetic whole work",
                "legal_basis": "Generated synthetic CC0 fixture",
                "licence": "CC0",
                "acquired_at": utc_now(),
            },
            "read_at": utc_now(),
            "reader": "TEST ONLY structural fixture (not actual agent close reading)",
            "coverage": "whole_work",
            "scope_description": "All five synthetic sections, no real study",
            "scholarly_kind": "empirical",
            "central_thesis": row["source_argument"],
            "question": row["objective"],
            "population": row["participants"],
            "stage": row["education_level"],
            "setting": row["country"],
            "design": row["design"],
            "constructs": ["reported study routines", "observed learning outcomes"],
            "analytic_approach": "TEST ONLY compare evidence kinds",
            "findings": "TEST ONLY distinctions, not empirical findings",
            "limitations": row["limitations"],
            "relevance_to_rq": "TEST ONLY library learning routines versus observed outcomes",
            "relevance_rationale": "TEST ONLY direct construct and measurement correspondence",
            "highly_relevant": True,
            "inference_limits": "No causal or real-world inference; synthetic fixture",
            "evidence": [
                {
                    "evidence_id": row["id"] + ":" + k,
                    "content_type": k,
                    "paraphrase": "TEST ONLY: " + v.split(". ", 1)[1],
                    "locator": f"Synthetic section: {k}",
                    "status": "checked_against_text",
                    "finding_kind": "reported" if k == "result" else "interpretation",
                }
                for k, v in pieces.items()
            ],
            "opposing_source_ids": ["S003"] if n == 1 and count >= 3 else [],
            "own_implication": row["target_argument"],
        }
        records.append(Source.model_validate(row))
    claims = []
    for n, pair in enumerate([["S001", "S002"], ["S003", "S004"], ["S005", "S006"]], 1):
        claims.append(
            {
                "id": f"C{n:03}",
                "text": f"TEST ONLY claim {n}: distinguish perceptions, outcomes and contextual explanations.",
                "source_ids": pair,
                "evidence_ids": [s + ":claim" for s in pair] + [s + ":result" for s in pair],
                "author_positions": {
                    s: "TEST ONLY source-author position distinguishes measurement and inference"
                    for s in pair
                },
                "comparison": "TEST ONLY: common distinction, different hypothetical contexts; no false consensus",
                "warrant": "TEST ONLY: evidence types warrant different conclusions",
                "warrant_id": f"W{n:03}",
                "objection": "TEST ONLY: selection or opportunity can explain reported differences",
                "objection_id": f"O{n:03}",
                "qualification": "Synthetic only; no observed causal effects",
                "confidence": "structural demonstration",
                "own_inference": "TEST ONLY: measure reports and outcomes separately",
                "scope": "Synthetic library-learning example",
                "theory_ids": ["L1"],
                "rq_ids": ["RQ1"],
                "section": "thematic review",
                "paragraph_plan": [
                    "Analytical claim",
                    "Source A evidence",
                    "Source B comparison",
                    "Rival explanation",
                    "Qualified own inference",
                ],
                "transition_warrant": "TEST ONLY: inference boundaries justify separate measures",
                "relative_strength": "TEST ONLY, not empirical evidence",
            }
        )
    framework = {
        "phenomenon": "TEST ONLY library learning",
        "outcomes": ["Observed learning outcomes"],
        "rq_definitions": {"RQ1": "TEST ONLY: how should routines and outcomes be distinguished?"},
        "candidates": [
            {
                "id": lid,
                "name": name,
                "source_ids": ids,
                "evidence_ids": [i + ":claim" for i in ids],
                "explanatory_power": "TEST ONLY: explains an evidence boundary",
                "epistemology": "TEST ONLY: compatible interpretative comparison",
                "scope_conditions": "Synthetic comparison; no causal identification",
                "method_fit": "Separate reports and observations",
                "operationalisation": "Use separate measures and critical coding",
                "selected": selected,
                "selection_reason": "TEST ONLY primary measurement lens"
                if selected
                else "TEST ONLY alternative requires contextual data",
                "used_in": ["measurement", "analysis"] if selected else [],
            }
            for lid, name, ids, selected in [
                ("L1", "TEST ONLY evidence-boundary lens", ["S001", "S002"], True),
                ("L2", "TEST ONLY contextual-opportunity lens", ["S003", "S004"], False),
            ]
        ],
        "constructs": [
            {
                "id": cid,
                "name": name,
                "definition": definition,
                "source_ids": ["S001", "S002"],
                "evidence_ids": ["S001:claim", "S002:method"],
                "boundaries": "TEST ONLY: reports are not observations",
                "distinct_from": ["confidence"] if cid == "K1" else ["reported study routines"],
                "rq_ids": ["RQ1"],
                "claim_ids": ["C001"],
                "operationalisation": measure,
                "analysis_use": analysis,
                "expected_pattern": "TEST ONLY: measures can diverge",
                "disconfirming_pattern": "TEST ONLY: convergent independent evidence changes interpretation",
                "lens_ids": ["L1"],
            }
            for cid, name, definition, measure, analysis in [
                (
                    "K1",
                    "reported study routines",
                    "Accounts of repeated activity; a perceived practice, not measured attainment",
                    "Proposed routine interview code",
                    "Compare routine accounts across cases",
                ),
                (
                    "K2",
                    "observed learning outcomes",
                    "Performance documented independently of a routine account",
                    "Proposed task observation code",
                    "Compare observed performance with accounts",
                ),
            ]
        ],
        "relationships": [
            {
                "id": "R1",
                "source": "K1",
                "target": "K2",
                "mechanism": "TEST ONLY: hypothesised association to investigate",
                "status": "hypothesised",
                "relation_type": "proposed_mechanism",
                "evidence_ids": ["S001:claim", "S002:result"],
                "conditions": "TEST ONLY opportunity and measurement conditions",
                "rival_mechanism": "Selection and contextual opportunities",
                "negative_case": "Routine accounts without corresponding observed change",
            }
        ],
        "uses": [
            {
                "location": "analysis plan",
                "stage": "analysis",
                "construct_id": "K1",
                "label": "reported study routines",
            }
        ],
        "theory_failure": "TEST ONLY: perception alone cannot explain observed performance",
        "modest_contribution": "TEST ONLY distinguish related constructs and rival pathways",
        "scope_limits": "Synthetic example; not an empirical model",
        "revision_triggers": [
            "TEST ONLY independent outcome evidence contradicts the proposed interpretation"
        ],
    }
    novelty = {
        "tentative_contribution": "TEST ONLY preserve distinct measurement and explanation boundaries",
        "gap_kind": "researcher_inferred",
        "comparisons": [
            {
                "source_id": s.id,
                "rq": s.objective,
                "population": s.participants,
                "stage": s.education_level,
                "geography": s.country,
                "design": s.design,
                "sample": "TEST ONLY no real sample",
                "constructs": ["reported study routines", "observed learning outcomes"],
                "theoretical_lens": "TEST ONLY evidence boundary",
                "findings": s.reading.findings,
                "limitations": s.limitations,
                "overlap": "TEST ONLY addresses adjacent measures",
                "remaining_difference": "TEST ONLY conceptual boundary rather than a new country or method label",
                "confidence": "TEST ONLY",
                "evidence_ids": [s.id + ":claim", s.id + ":limitation"],
                "already_answers": False,
            }
            for s in records[:5]
        ],
        "strongest_rival_id": "S001",
        "sceptical_case": "TEST ONLY existing conceptual distinctions may already answer the question",
        "surviving_contribution": "TEST ONLY only a bounded measurement refinement could remain",
        "conceptual_consequence": "TEST ONLY prevents conflating perceptions and outcomes",
        "search_boundary": "TEST ONLY generated corpus; no real search or novelty",
        "confidence_bounds": "TEST ONLY structural test; no scientific originality claim",
        "method_fit": "Separate measures and negative cases",
        "basis": ["measurement"],
        "proposed_verdict": "GAP_NARROW_BUT_DEFENSIBLE",
    }
    syn = Synthesis.model_validate(
        {
            "thesis": "TEST ONLY: distinguish related constructs under explicit inference boundaries",
            "claims": claims,
            "framework": framework,
            "novelty": novelty,
            "edges": [
                {
                    "source": "S003",
                    "target": "S001",
                    "kind": "contradicts",
                    "rationale": "TEST ONLY retain a rival contextual explanation",
                    "evidence_ids": ["S003:counterpoint", "S001:result"],
                }
            ],
        }
    )
    eric_data = {
        "response": {"numFound": count, "docs": [{"id": s.id, "title": s.title} for s in records]}
    }
    eric_file = folder / "TEST_ONLY_eric.json"
    eric_file.write_text(json.dumps(eric_data))
    scholar_file = folder / "TEST_ONLY_scholar.json"
    scholar_file.write_text(json.dumps([{"title": s.title, "url": s.url} for s in records]))
    observations = [
        DiscoveryObservation(
            provider="ERIC",
            query="TEST ONLY library learning",
            executed_at=utc_now(),
            results=eric_data["response"]["docs"],
            returned_count=count,
            artifact_path=str(eric_file.resolve()),
            artifact_sha256=sha256_file(eric_file),
            observation_kind="api_response",
            observer="TEST ONLY fixture",
            synthetic=True,
        ),
        DiscoveryObservation(
            provider="Google Scholar",
            query="TEST ONLY library learning",
            executed_at=utc_now(),
            results=[{"title": s.title, "url": s.url} for s in records],
            returned_count=count,
            artifact_path=str(scholar_file.resolve()),
            artifact_sha256=sha256_file(scholar_file),
            observation_kind="user_export",
            observer="TEST ONLY fixture",
            synthetic=True,
        ),
    ]
    logs = [
        {
            "provider": o.provider,
            "status": "ERIC_SEARCHED" if o.provider == "ERIC" else "SCHOLAR_OBSERVATION_IMPORTED",
            "query": o.query,
            "ids": [r.get("id") for r in o.results],
        }
        for o in observations
    ]
    logs.insert(
        0, {"provider": "protocol", "status": "PROSPECTIVE_PROTOCOL", "prepared_at": prepared_at}
    )
    return records, syn, observations, logs
