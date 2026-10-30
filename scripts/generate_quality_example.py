"""Run the real CLI on TEST ONLY full-text structural fixtures; never a real research pass."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.v3_factory import bundle
from educational_research.cli import main

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--abstract-count", type=int, default=0)
    p.add_argument("--presentation", choices=["roadmap", "evidence-pack"], default="roadmap")
    p.add_argument("--output", default="outputs/quality-v043-synthetic")
    a = p.parse_args()
    root = Path(a.output)
    root.mkdir(parents=True, exist_ok=True)
    from educational_research.core.protocol import provisional
    from educational_research.config import Config

    inputs = root / "evidence" / "inputs" if a.presentation == "roadmap" else root
    inputs.mkdir(parents=True, exist_ok=True)
    protocol = provisional(Config(topic="library learning", target_references=a.count))
    protocol.problem = "TEST ONLY: A routine account and an observed learning outcome answer different questions, yet a study can confuse their evidential roles."
    protocol_path = inputs / "synthetic-protocol.json"
    protocol_path.write_text(protocol.model_dump_json(indent=2))
    sources, synthesis, observations, _ = bundle(inputs / "synthetic-corpus", a.count)
    if a.abstract_count:
        if not 0 <= a.abstract_count <= a.count:
            p.error("abstract-count must be between zero and count")
        from tests.test_v043_evidence import abstract_work

        for source in sources[-a.abstract_count :]:
            abstract_work(source, inputs / "synthetic-abstracts", 95)
    paths = {
        "sources": inputs / "synthetic-sources.json",
        "synthesis": inputs / "synthetic-synthesis.json",
        "discovery-records": inputs / "synthetic-observations.json",
    }
    for key, records in [
        ("sources", [s.model_dump() for s in sources]),
        ("synthesis", synthesis.model_dump()),
        ("discovery-records", [o.model_dump() for o in observations]),
    ]:
        paths[key].write_text(json.dumps(records, ensure_ascii=False, indent=2))
    args = [
        "--topic",
        "library learning",
        "--rq",
        "How should reported routines and observed outcomes be distinguished?",
        "--target-references",
        str(a.count),
        "--presentation",
        a.presentation,
        "--offline",
        "--protocol",
        str(protocol_path),
        "--output-dir",
        str(root),
    ]
    for flag, path in paths.items():
        args += ["--" + flag, str(path)]
    raise SystemExit(main(args))
