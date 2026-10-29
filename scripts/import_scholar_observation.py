"""Package a genuine user export into a dated, hashed observation; performs no Scholar search."""

import argparse
import csv
import json
from pathlib import Path
from educational_research.core.discovery import DiscoveryObservation
from educational_research.core.reading import sha256_file


def build(artifact, query, executed_at, observer, filters=None):
    artifact = Path(artifact)
    if artifact.suffix.lower() == ".json":
        rows = json.loads(artifact.read_text())
    else:
        with artifact.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    results = [
        {
            "title": r["title"],
            "url": r["url"],
            **({"cited_by": r["cited_by"]} if r.get("cited_by") else {}),
        }
        for r in rows
    ]
    record = DiscoveryObservation(
        provider="Google Scholar",
        query=query,
        executed_at=executed_at,
        filters=filters or {},
        results=results,
        returned_count=len(results),
        artifact_path=str(artifact.resolve()),
        artifact_sha256=sha256_file(artifact),
        observation_kind="user_export",
        observer=observer,
    )
    if record.issues():
        raise ValueError("; ".join(record.issues()))
    return record


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "artifact", help="Actual CSV/JSON export with title,url fields; not a query-plan file"
    )
    p.add_argument("--query", required=True)
    p.add_argument("--executed-at", required=True, help="Actual observed ISO timestamp with timezone")
    p.add_argument("--observer", required=True)
    p.add_argument("--filters-json", default="{}")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    try:
        record = build(a.artifact, a.query, a.executed_at, a.observer, json.loads(a.filters_json))
        Path(a.output).write_text(json.dumps([record.model_dump()], ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as exc:
        p.error(str(exc))
