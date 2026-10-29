"""Record an actual human/agent preview review without upgrading scientific gate status."""

import argparse
import json
from pathlib import Path
from educational_research.core.discovery import utc_now
from educational_research.core.reading import sha256_file
from educational_research.core.deliverables import seal_receipt


def record(folder, images, reviewer, verdict, notes):
    folder = Path(folder)
    manifest = {
        "reviewer": reviewer,
        "reviewed_at": utc_now(),
        "verdict": verdict,
        "notes": notes,
        "pdf_sha256": sha256_file(folder / "Educational_Research_Essentials.pdf"),
        "images": [{"path": str(Path(i).resolve()), "sha256": sha256_file(i)} for i in images],
        "trust_boundary": "Recorded reviewer attestation, not an automated visual judgement",
    }
    if not images or not notes.strip():
        raise ValueError("Record the actual inspected images and specific review notes")
    (folder / "Visual_Review.json").write_text(json.dumps(manifest, indent=2))
    report = folder / "QA_Report.md"
    with report.open("a") as stream:
        stream.write(
            "\n\nVisual review: "
            + verdict
            + "; "
            + reviewer
            + "; "
            + notes
            + "\nInspected: "
            + ", ".join(str(i) for i in images)
            + "\n"
        )
    audit_path = folder / "audit.json"
    audit = json.loads(audit_path.read_text())
    audit["pdf"]["visual_review"] = "RECORDED_" + verdict.upper()
    audit_path.write_text(json.dumps(audit, indent=2))
    receipt = json.loads((folder / "Execution_Receipt.json").read_text())
    receipt["commands_executed"].append(
        {
            "command": "Python call: scripts.record_visual_review.record",
            "executed_at": utc_now(),
            "result": manifest,
        }
    )
    seal_receipt(folder, receipt)
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("folder")
    p.add_argument("--images", nargs="+", required=True)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--verdict", choices=["passed", "needs_revision"], required=True)
    p.add_argument("--notes", required=True)
    args = p.parse_args()
    record(args.folder, args.images, args.reviewer, args.verdict, args.notes)
