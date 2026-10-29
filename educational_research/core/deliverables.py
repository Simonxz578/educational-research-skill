"""Native deliverable validation and receipt hashes; scientific quality is recomputed separately."""

import csv
import json
from pathlib import Path
from .reading import sha256_file

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
    folder = Path(folder)
    errors = []
    for name in REQUIRED:
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
        import fitz

        with fitz.open(folder / "Educational_Research_Essentials.pdf") as pdf:
            text = "\n".join(p.get_text() for p in pdf)
            for row in rows:
                if row["id"] not in text:
                    errors.append(f"Matrix source absent from PDF: {row['id']}")
            links = [link.get("uri", "") for p in pdf for link in p.get_links() if link.get("uri")]
            for row in rows:
                if row["doi"] and "https://doi.org/" + row["doi"] not in links:
                    errors.append(f"Missing DOI hyperlink: {row['id']}")
        if pdf_audit:
            errors += pdf_audit["errors"]
        if (folder / "Visual_Review.json").exists():
            visual = json.loads((folder / "Visual_Review.json").read_text())
            if visual["pdf_sha256"] != sha256_file(folder / "Educational_Research_Essentials.pdf"):
                errors.append("Visual review belongs to a different PDF version")
            for image in visual["images"]:
                image_path = Path(image["path"])
                if not image_path.is_file() or sha256_file(image_path) != image["sha256"]:
                    errors.append("Reviewed preview image missing or modified")
        if verify_receipt:
            receipt = json.loads((folder / "Execution_Receipt.json").read_text())
            if (
                receipt.get("entrypoint")
                not in {"educational_research.cli", "educational_research.pipeline.run"}
                or receipt.get("renderer") != "educational_research.render.essentials_pdf"
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
        "checked_groups": list(MATRIX_GROUPS),
        "native_cli": bool(locals().get("receipt", {}).get("entrypoint") == "educational_research.cli"),
    }


def seal_receipt(folder, receipt):
    folder = Path(folder)
    # Receipt cannot hash itself. Every other delivered file is sealed after final gates/QA.
    receipt["artifact_hashes"] = {
        name: sha256_file(folder / name)
        for name in REQUIRED
        + (["Visual_Review.json"] if (folder / "Visual_Review.json").exists() else [])
        if name != "Execution_Receipt.json" and (folder / name).is_file()
    }
    (folder / "Execution_Receipt.json").write_text(json.dumps(receipt, indent=2))
