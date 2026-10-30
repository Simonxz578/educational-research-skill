"""Validate native receipt, complete matrix, page QA and recomputed substantive gates."""

import argparse
import json
from pathlib import Path
from educational_research.render.inspect import inspect
from educational_research.core.deliverables import validate_delivery
from educational_research.core.quality import CAPS
from educational_research.core.gates import evaluate_gates
from educational_research.core.discovery import load_observations
from educational_research.models import Source, Segment, Author, Quote, Assessment
from educational_research.core.reading import FullTextReading
from educational_research.core.access import FullTextAcquisition
from educational_research.models import restore_public_source
from educational_research.core.graph import Synthesis
from educational_research.config import Config
from educational_research.core.layout import audit_dir, reader_pdf, presentation


def validate(folder, strict=False):
    root = Path(folder)
    folder = audit_dir(root)
    errors = []
    if sorted(p.name for p in root.glob("*.pdf")) != (
        ["Research_Roadmap.pdf"]
        if presentation(folder) == "roadmap"
        else ["Educational_Research_Essentials.pdf"]
    ):
        errors.append("Default output must contain exactly one essentials PDF")
    pdf = inspect(reader_pdf(folder), presentation=presentation(folder))
    errors += validate_delivery(folder, pdf)["errors"]
    try:
        matrix = json.loads((folder / "Evidence_Matrix.json").read_text())
        graph = Synthesis.model_validate_json((folder / "Argument_Graph.json").read_text())
        ids = {s["id"] for s in matrix}
        sources = []
        for row in matrix:
            for field, limit in CAPS.items():
                if len(row[field].split()) > limit:
                    errors.append(f"{row['id']} overlong {field}")
            if not set(row["comparison_ids"]) <= ids:
                errors.append("Missing comparative source")
            # Public records omit protected source text. Rehydrate only typed, metadata-level
            # fields for gate recomputation; do not pretend to reverify quotes from absent text.
            data = {k: v for k, v in row.items() if k in Source.model_fields}
            data["authors"] = [Author.model_validate(a) for a in row["authors"]]
            data["quotes"] = [Quote.model_validate(q) for q in row["quotes"]]
            data["assessments"] = {
                k: Assessment.model_validate(v) for k, v in row["assessments"].items()
            }
            data["segments"] = [Segment.model_validate({**s, "text": ""}) for s in row["segments"]]
            data["reading"] = (
                FullTextReading.model_validate(row["reading"]) if row.get("reading") else None
            )
            data["acquisition"] = (
                FullTextAcquisition.model_validate(row["acquisition"])
                if row.get("acquisition")
                else None
            )
            sources.append(restore_public_source(row))
        receipt = json.loads((folder / "Execution_Receipt.json").read_text())
        argv = receipt.get("argv", [])
        from educational_research.cli import parser

        options = vars(parser().parse_args(argv))
        config = Config(
            **{k: v for k, v in options.items() if k in Config.model_fields and v is not None}
        )
        logs = json.loads((folder / "search_log.json").read_text())
        observations = load_observations(folder / "Discovery_Observations.json")
        recomputed = evaluate_gates(
            config, sources, graph, logs, observations, validate_delivery(folder, pdf)
        )
        reported = json.loads((folder / "Research_Quality_Gates.json").read_text())
        for key in recomputed["gates"]:
            if (
                reported["gates"][key]["status"] == "PASS"
                and recomputed["gates"][key]["status"] != "PASS"
            ):
                errors.append(f"{key}: reported PASS not supported by independent recomputation")
        if reported["overall_status"] == "PASS" and recomputed["overall_status"] != "PASS":
            errors.append("Unsupported overall research acceptance")
        if strict and recomputed["overall_status"] != "PASS":
            errors.append("Strict substantive quality acceptance not achieved")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid research pack: {exc}")
    return sorted(set(errors))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("folder")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args()
    issues = validate(args.folder, args.strict)
    print(json.dumps({"structurally_valid": not issues, "errors": issues}, indent=2))
    raise SystemExit(bool(issues))
