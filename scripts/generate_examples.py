"""Build TEST ONLY synthetic load examples; no real references or DOIs."""

import argparse
import json
from pathlib import Path
import sys

# This example generator intentionally uses checkout-only synthetic test factories.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from educational_research.cli import main
from tests.factories import source

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--output", default="outputs/synthetic")
    args = p.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    fixture = output / "synthetic-input.json"
    fixture.write_text(json.dumps([source(i).model_dump() for i in range(1, args.count + 1)], indent=2))
    synthesis = Path(__file__).resolve().parents[1] / "examples/synthesis.synthetic.json"
    arguments = [
        "--presentation",
        "evidence-pack",
        "--topic",
        "library learning",
        "--target-words",
        str(args.count * 100),
        "--target-references",
        str(args.count),
        "--offline",
        "--sources",
        str(fixture),
        "--output-dir",
        str(output),
    ]
    if args.count >= 3:
        arguments += ["--synthesis", str(synthesis)]
    status = main(arguments)
    result = json.loads((output / "audit.json").read_text())
    print(
        json.dumps(
            {
                "pages": result["pdf"]["pages"],
                "layout_passed": result["layout_passed"],
                "research_status": result["research_quality"]["overall_status"],
                "count": args.count,
            }
        )
    )
    raise SystemExit(status)
