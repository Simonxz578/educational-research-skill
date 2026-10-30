"""Native deliverable validation and receipt hashes; scientific quality is recomputed separately."""

import csv
import json
import re
from pathlib import Path
from .reading import sha256_file
from .layout import audit_dir, reader_pdf, presentation

MATRIX_GROUPS = {
    "identity": ["id", "title", "authors", "year", "doi", "url", "identity"],
    "objective_context": ["objective", "education_level", "country", "participants", "design"],
    "content": ["summary", "theory", "limitations"],
    "source_author": ["source_argument"],
    "excerpts": ["quotes", "segments"],
    "relevance": ["relevance_score", "relevance_explanation"],
    "target_author": ["target_argument"],
    "comparison": ["comparison_ids", "relationship"],
    "argument": ["role", "claim_ids", "evidence_ids", "warrant_ids"],
    "strength": ["evidence_strength", "evidence_kind", "access", "warnings"],
    "journal_metrics": [
        "journal_metric_name",
        "journal_metric_value",
        "journal_metric_year",
        "journal_metric_source",
        "journal_quartile",
        "journal_quartile_source",
    ],
    "article_metrics": ["article_citations", "count_source", "check_date", "fwci_if_verified"],
    "priority": [
        "study_quality_score",
        "journal_influence_score",
        "article_impact_score",
        "argument_value_score",
        "total_priority_score",
        "metric_missingness",
        "available_weight",
        "why_included",
    ],
    "verification": ["checked_at", "providers", "publication_status"],
    "legal_access": ["segments", "reading"],
}
REQUIRED = [
    "Evidence_Matrix.json",
    "Evidence_Matrix.csv",
    "Full_Text_Reading_Audit.json",
    "Full_Text_Reading_Audit.csv",
    "Evidence_Ledger.json",
    "Argument_Graph.json",
    "Closest_Study_Novelty_Comparison.json",
    "Closest_Study_Novelty_Comparison.csv",
    "Theoretical_Conceptual_Framework.json",
    "Framework.mmd",
    "Framework_Diagram.json",
    "Framework.svg",
    "Theory_RQ_Evidence_Method_Alignment.csv",
    "verified_references.csl.json",
    "unresolved_references.json",
    "search_protocol.json",
    "search_log.json",
    "Discovery_Observations.json",
    "Research_Quality_Gates.json",
    "QA_Report.md",
    "Execution_Receipt.json",
    "Editorial_Audit.json",
    "Framework_Audit.json",
    "Study_Design_Audit.json",
    "audit.json",
    "Educational_Research_Essentials.pdf",
]


def required_files(folder, kind=None):
    kind = kind or presentation(folder)
    if kind == "roadmap":
        paths = [n for n in REQUIRED if n != "Educational_Research_Essentials.pdf"] + [
            "../Research_Roadmap.pdf",
            "Reader_View.json",
            "Source_Selection.json",
            "Candidates.json",
            "Argument_Alignment.json",
            "Full_Text_Access.json",
            "Full_Text_Access_Handoff.md",
        ]
        receipt = Path(folder) / "Execution_Receipt.json"
        if receipt.exists() and json.loads(receipt.read_text()).get("include_audit_pdf"):
            paths.append("Educational_Research_Essentials.pdf")
        return paths
    return REQUIRED


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0]) if rows else ["source_id", "status"]
    with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                    for k, v in row.items()
                    if k in fields
                }
            )


def validate_delivery(folder, pdf_audit=None, verify_receipt=True):
    csv.field_size_limit(64_000_000)
    folder = audit_dir(folder)
    kind = presentation(folder)
    errors = []
    for name in required_files(folder):
        if not (folder / name).is_file():
            errors.append(f"Missing native deliverable: {name}")
    try:
        rows = json.loads((folder / "Evidence_Matrix.json").read_text())
        graph = json.loads((folder / "Argument_Graph.json").read_text())
        refs = json.loads((folder / "verified_references.csl.json").read_text())
        with (folder / "Evidence_Matrix.csv").open(encoding="utf-8-sig", newline="") as f:
            csv_reader = csv.DictReader(f)
            columns = csv_reader.fieldnames or []
            csv_rows = list(csv_reader)
        for group, fields in MATRIX_GROUPS.items():
            if not set(fields) <= set(columns) or any(not set(fields) <= row.keys() for row in rows):
                errors.append(f"Incomplete matrix group: {group}")
        ids = {row["id"] for row in rows}
        if len(ids) != len(rows) or {r["id"] for r in csv_rows} != ids:
            errors.append("Matrix CSV/JSON IDs mismatch")
        if {r["id"] for r in refs} != {
            r["id"] for r in rows if r["identity"] in {"VERIFIED", "SYNTHETIC"}
        }:
            errors.append("Verified bibliography does not match matrix")
        for c in graph["claims"]:
            if not set(c["source_ids"]) <= ids:
                errors.append("Unknown argument source")
        for name in ["Literature_Argument_Matrix.json", "argument_graph.json", "evidence_ledger.json"]:
            canonical = {
                "Literature_Argument_Matrix.json": "Evidence_Matrix.json",
                "argument_graph.json": "Argument_Graph.json",
                "evidence_ledger.json": "Evidence_Ledger.json",
            }[name]
            if json.loads((folder / name).read_text()) != json.loads((folder / canonical).read_text()):
                errors.append(f"Legacy/native alias mismatch: {name}")
        if kind == "roadmap":
            from .reader import ReaderView, SECTIONS
            from .reading import FullTextReading
            from .evidence_depth import primary_depth_audit
            from ..models import Quote
            from ..models import restore_public_source
            from .verification import verbatim_audit

            view = ReaderView.model_validate_json((folder / "Reader_View.json").read_text())
            selection = json.loads((folder / "Source_Selection.json").read_text())
            if view.sections != SECTIONS:
                errors.append("Reader must expose the five approved sections in order")
            if (
                set(view.selected_source_ids) != ids
                or {p.source_id for p in view.papers} != ids
                or len(view.papers) != len(ids)
            ):
                errors.append("Reader/matrix selected-source count or IDs mismatch")
            readings = json.loads((folder / "Full_Text_Reading_Audit.json").read_text())
            deep_count = sum(r["qualified"] for r in readings)
            if (
                selection["verified_relevant_selected_K"] != len(ids)
                or selection["qualified_deep_read_K"] != deep_count
            ):
                errors.append(
                    "Selected/deep-reading counters disagree with the qualifying reader corpus"
                )
            if selection["deep_review_requirement_N"] < max(10, selection["selection_target_N"]):
                errors.append("Requested source target was silently lowered for deep-review acceptance")
            if selection["shortfall"] != max(
                0, selection["deep_review_requirement_N"] - deep_count
            ) or selection["selected_shortfall"] != max(0, selection["selection_target_N"] - len(ids)):
                errors.append("Source shortfall counters disagree with requested and qualified counts")
            if (
                view.source_selection != selection
                or selection["selected_source_ids"] != view.selected_source_ids
            ):
                errors.append("Quantity contract differs between reader and evidence layers")
            if (
                selection["requested_semantics"] == "exact"
                and len(ids) > selection["selection_target_N"]
            ):
                errors.append("Exact source count was exceeded")
            if selection["quotation_count"] != sum(len(p.original_microquotes) for p in view.papers):
                errors.append("Reader quotation count disagrees with native selection counters")
            by_source = {r["id"]: r for r in rows}
            for paper in view.papers:
                row = by_source[paper.source_id]
                restored = restore_public_source(row)
                if paper.evidence_status == "ABSTRACT_ONLY":
                    from ..fulltext.abstracts import abstract_issues, abstract_explanation

                    errors += [f"{paper.source_id}: " + issue for issue in abstract_issues(restored)]
                    a = restored.abstract_evidence
                    if (
                        a is None
                        or paper.source_author_position.text != abstract_explanation(a)
                        or paper.our_inference.text != a.interpretation
                        or paper.verified_original_words != 0
                        or paper.inspection_gate != "NOT_APPLICABLE_TO_ABSTRACT / NOT_FULL_TEXT_VERIFIED"
                    ):
                        errors.append(
                            f"{paper.source_id}: abstract-only scope, wording or counters were promoted/changed"
                        )
                    allowed = [a.quotation] if a and a.quotation else []
                    if [q.text for q in paper.original_microquotes] != allowed:
                        errors.append(
                            f"{paper.source_id}: abstract quote does not match permitted original"
                        )
                    if paper.source_reasoning_and_results:
                        errors.append(
                            f"{paper.source_id}: unverified full-text findings were added to an abstract"
                        )
                    continue
                depth = primary_depth_audit(
                    FullTextReading.model_validate(row["reading"]),
                    [Quote.model_validate(q) for q in row["quotes"]],
                )
                inspected = verbatim_audit(restored)
                if paper.verified_original_words != inspected["verified_original_words"]:
                    errors.append(
                        f"{paper.source_id}: author-word count differs from actual original-span verification"
                    )
                originals = [
                    layer.text for layer in paper.layers if layer.kind == "VERBATIM_PRIMARY_TEXT"
                ]
                if originals != [span["exact_text"] for span in inspected["spans"]]:
                    errors.append(
                        f"{paper.source_id}: verbatim layer contains non-source text or omits checked spans"
                    )
                explanations = [
                    layer.text for layer in paper.layers if layer.kind == "SOURCE_ANCHORED_EXPLANATION"
                ]
                if explanations != [
                    paper.source_author_position.text,
                    *[st.text for st in paper.source_reasoning_and_results],
                    paper.source_limitations.text,
                ]:
                    errors.append(
                        f"{paper.source_id}: explanation was conflated with another evidence layer"
                    )
                if (
                    paper.primary_evidence_words,
                    paper.primary_evidence_shortfall,
                    paper.primary_evidence_issues,
                ) != (
                    inspected["verified_original_words"],
                    inspected["original_word_shortfall"],
                    inspected["issues"] + depth["issues"],
                ):
                    errors.append(
                        f"{paper.source_id}: primary-evidence depth counters differ from the rendered source paraphrases"
                    )
                anchors = {e["evidence_id"]: e for e in row["reading"]["evidence"]}
                locations = {f"{row['id']}:{s['id']}": s["locator"] for s in row["segments"]}
                for statement in [
                    paper.source_author_position,
                    *paper.source_reasoning_and_results,
                    paper.source_limitations,
                    paper.our_inference,
                ]:
                    for eid, loc in zip(statement.evidence_ids, statement.locators):
                        anchor = anchors.get(eid)
                        expected = (
                            anchor.get("researcher_inference")
                            if statement is paper.our_inference and anchor
                            else anchor.get("paraphrase")
                            if anchor
                            else None
                        )
                        if not anchor or statement.text != expected or loc != locations.get(eid):
                            errors.append(
                                f"{paper.source_id}: reader wording/locator differs from the source-grounded extraction"
                            )
                allowed = {(q["text"], f"{row['id']}:{q['segment_id']}") for q in row["quotes"]}
                if any(
                    (q.text, q.evidence_id) not in allowed or q.locator != locations.get(q.evidence_id)
                    for q in paper.original_microquotes
                ):
                    errors.append(
                        f"{paper.source_id}: reader quotation differs from verified source record"
                    )
                if paper.quotation_units > paper.quotation_budget:
                    errors.append(f"{paper.source_id}: per-work reader quotation budget exceeded")
                for statement in [
                    paper.source_author_position,
                    *paper.source_reasoning_and_results,
                    paper.source_limitations,
                    paper.our_inference,
                ]:
                    if not statement.evidence_ids or not statement.locators:
                        errors.append(f"{paper.source_id}: reader claim lacks evidence/locator")
        import fitz

        with fitz.open(reader_pdf(folder)) as pdf:
            text = "\n".join(p.get_text() for p in pdf)
            for row in rows:
                if row["id"] not in text:
                    errors.append(f"Matrix source absent from PDF: {row['id']}")
            if kind == "roadmap":
                for source_id in ids:
                    pattern = r"(?m)^\d{2,4}[^\[]+\[" + re.escape(source_id) + r"\]"
                    if len(re.findall(pattern, text)) != 1:
                        errors.append(f"Reader source block missing or repeated: {source_id}")
                reference_text = text.split("APA 7 REFERENCES", 1)[-1]
                if any(
                    not re.search(r"(?m)^" + re.escape(source_id) + r"$", reference_text)
                    for source_id in ids
                ):
                    errors.append("Reader bibliography omits a selected work")
                compact_text = re.sub(r"\s+", " ", text)
                from .visible import count_display

                visible_results = {}
                for paper in view.papers:
                    marker = "[" + paper.source_id + "]"
                    start = compact_text.index(marker)
                    ends = [
                        compact_text.find("[" + other.source_id + "]", start + len(marker))
                        for other in view.papers
                    ]
                    ends = [end for end in ends if end > start]
                    block = (
                        compact_text[start : min(ends)]
                        if ends
                        else compact_text[start:].split("III. ARGUMENT", 1)[0]
                    )
                    inspected = count_display(
                        restore_public_source(by_source[paper.source_id]), paper.display_excerpts, block
                    )
                    visible_results[paper.source_id] = inspected
                    errors += [paper.source_id + ": " + i for i in inspected["issues"]]
                    if (paper.original_words_shown, paper.display_status) != (
                        inspected["shown"],
                        inspected["status"],
                    ):
                        errors.append(
                            paper.source_id
                            + ": displayed original-word counters differ from finished PDF"
                        )
            links = [link.get("uri", "") for p in pdf for link in p.get_links() if link.get("uri")]
            for row in rows:
                if row["doi"] and "https://doi.org/" + row["doi"] not in links:
                    errors.append(f"Missing DOI hyperlink: {row['id']}")
        if kind == "roadmap" and (folder / "Educational_Research_Essentials.pdf").exists():
            from ..render.inspect import inspect

            errors += inspect(
                folder / "Educational_Research_Essentials.pdf", presentation="evidence-pack"
            )["errors"]
        if pdf_audit:
            errors += pdf_audit["errors"]
        if (folder / "Visual_Review.json").exists():
            visual = json.loads((folder / "Visual_Review.json").read_text())
            if visual["pdf_sha256"] != sha256_file(reader_pdf(folder)):
                errors.append("Visual review belongs to a different PDF version")
            for image in visual["images"]:
                image_path = Path(image["path"])
                if not image_path.is_file() or sha256_file(image_path) != image["sha256"]:
                    errors.append("Reviewed preview image missing or modified")
        if verify_receipt:
            receipt = json.loads((folder / "Execution_Receipt.json").read_text())
            if receipt.get("entrypoint") not in {
                "educational_research.cli",
                "educational_research.pipeline.run",
            } or receipt.get("renderer") != (
                "educational_research.render.roadmap"
                if kind == "roadmap"
                else "educational_research.render.essentials_pdf"
            ):
                errors.append(
                    "Native CLI/renderer receipt missing; handwritten shortcuts are not accepted"
                )
            for name, digest in receipt.get("artifact_hashes", {}).items():
                path = folder / name
                if not path.is_file() or sha256_file(path) != digest:
                    errors.append(f"Deliverable changed after native validation: {name}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid deliverable structure: {type(exc).__name__}: {exc}")
    return {
        "errors": sorted(set(errors)),
        "visible_original_words": locals().get("visible_results", {}),
        "display_shortfalls": [
            sid for sid, r in locals().get("visible_results", {}).items() if r["status"] != "PASS"
        ],
        "checked_groups": list(MATRIX_GROUPS),
        "native_cli": bool(locals().get("receipt", {}).get("entrypoint") == "educational_research.cli"),
    }


def seal_receipt(folder, receipt):
    folder = Path(folder)
    # Receipt cannot hash itself. Every other delivered file is sealed after final gates/QA.
    receipt["artifact_hashes"] = {
        name: sha256_file(folder / name)
        for name in required_files(folder)
        + (["Visual_Review.json"] if (folder / "Visual_Review.json").exists() else [])
        if name != "Execution_Receipt.json" and (folder / name).is_file()
    }
    (folder / "Execution_Receipt.json").write_text(json.dumps(receipt, indent=2))
