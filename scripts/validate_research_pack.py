"""Independent output validation; rejects stale essay packs and broken evidence IDs."""

import argparse
import json
from pathlib import Path
from educational_research.render.inspect import inspect
from educational_research.core.quality import CAPS


def validate(folder):
    folder = Path(folder)
    errors = []
    pdfs = sorted(p.name for p in folder.glob("*.pdf"))
    if pdfs != ["Educational_Research_Essentials.pdf"]:
        errors.append("Default output must contain exactly one essentials PDF")
    matrix = json.loads((folder / "Literature_Argument_Matrix.json").read_text())
    graph = json.loads((folder / "argument_graph.json").read_text())
    refs = json.loads((folder / "verified_references.csl.json").read_text())
    ids = {s["id"] for s in matrix}
    for s in matrix:
        for field, limit in CAPS.items():
            if len(s[field].split()) > limit:
                errors.append(f"{s['id']} overlong {field}")
        if not set(s["comparison_ids"]) <= ids:
            errors.append("Missing comparative source")
    for claim in graph["claims"]:
        if not set(claim["source_ids"]) <= ids:
            errors.append("Unknown argument source ID")
    if {r["id"] for r in refs} != {
        s["id"] for s in matrix if s["identity"] in {"VERIFIED", "SYNTHETIC"}
    }:
        errors.append("Bibliography/matrix mismatch")
    errors += inspect(folder / "Educational_Research_Essentials.pdf")["errors"]
    return errors


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("folder")
    args = p.parse_args()
    issues = validate(args.folder)
    print(json.dumps({"passed": not issues, "errors": issues}, indent=2))
    raise SystemExit(bool(issues))
