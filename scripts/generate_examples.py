"""Build TEST ONLY synthetic load examples; no real references or DOIs."""

import argparse
import json
from pathlib import Path
import sys

# This example generator intentionally uses checkout-only synthetic test factories.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from educational_research.config import Config
from educational_research.pipeline import run
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
    result = run(
        Config(
            topic="library learning",
            target_words=args.count * 100,
            target_references=args.count,
            offline=True,
        ),
        output,
        fixture,
        synthesis if args.count >= 3 else None,
    )
    print(json.dumps({"pages": result["pdf"]["pages"], "passed": result["passed"], "count": args.count}))
