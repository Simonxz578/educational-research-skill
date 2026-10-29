"""Discovery receipts preserve actual observations, never promote query plans."""

import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from pydantic import Field
from ..models_base import Record
from .reading import sha256_file


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class DiscoveryObservation(Record):
    provider: Literal["ERIC", "Google Scholar"]
    query: str
    executed_at: str
    filters: dict = Field(default_factory=dict)
    results: list[dict]
    returned_count: int = Field(ge=0)
    artifact_path: str
    artifact_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    observation_kind: Literal["api_response", "browser_observation", "user_export"]
    observer: str
    synthetic: bool = False

    def issues(self):
        result = []
        try:
            date = datetime.fromisoformat(self.executed_at.replace("Z", "+00:00"))
            if date.tzinfo is None or date > datetime.now(timezone.utc):
                result.append("Observation requires an actual past UTC-aware timestamp")
        except ValueError:
            result.append("Invalid execution timestamp")
        path = Path(self.artifact_path)
        if not path.is_file() or sha256_file(path) != self.artifact_sha256:
            result.append("Observation artifact missing or digest mismatch")
        if not self.query.strip() or not self.observer.strip():
            result.append("Missing exact query/observer")
        if self.returned_count < len(self.results) or not self.results:
            result.append("No observed results, or inconsistent count")
        if self.provider == "Google Scholar":
            for row in self.results:
                if not row.get("title") or not row.get("url"):
                    result.append("Scholar result lacks title/link")
            if self.observation_kind == "api_response":
                result.append("No permitted Scholar bulk API exists")
        elif self.observation_kind != "api_response" or any(not r.get("id") for r in self.results):
            result.append("ERIC receipt requires actual API record IDs")
        if path.is_file() and not result and self.observation_kind == "api_response":
            try:
                data = json.loads(path.read_text())
                response = data["response"]
                if [r.get("id") for r in self.results] != [
                    r.get("id") for r in response["docs"]
                ] or self.returned_count != response["numFound"]:
                    result.append("ERIC observations disagree with the preserved response")
            except (ValueError, KeyError, TypeError):
                result.append("ERIC artifact is not a documented response")
        if path.is_file() and self.observation_kind == "user_export":
            try:
                if path.suffix.lower() == ".json":
                    exported = json.loads(path.read_text())
                else:
                    with path.open(encoding="utf-8-sig", newline="") as stream:
                        exported = list(csv.DictReader(stream))
                observed = {(r["title"], r["url"]) for r in exported}
                if not {(r["title"], r["url"]) for r in self.results} <= observed:
                    result.append("Imported results disagree with preserved export")
            except (ValueError, KeyError, TypeError, OSError, UnicodeError):
                result.append("Export artifact must contain inspectable title/link records")
        return result


def load_observations(path):
    return [DiscoveryObservation.model_validate(r) for r in json.loads(Path(path).read_text())]


def discovery_status(logs, observations):
    qualifying = [o for o in observations if not o.issues()]
    eric = [o for o in qualifying if o.provider == "ERIC"]
    scholar = [o for o in qualifying if o.provider == "Google Scholar"]
    # Observations must agree with exact execution logs, not just exist in a bundle.
    eric = [
        o
        for o in eric
        if any(
            e.get("status") == "ERIC_SEARCHED"
            and e.get("query") == o.query
            and e.get("ids") == [r["id"] for r in o.results]
            for e in logs
        )
    ]
    scholar = [
        o
        for o in scholar
        if any(
            e.get("status") == "SCHOLAR_OBSERVATION_IMPORTED" and e.get("query") == o.query for e in logs
        )
    ]
    errors = [f"{o.provider}: {issue}" for o in observations for issue in o.issues()]
    protocol_logs = [e for e in logs if e.get("status") == "PROSPECTIVE_PROTOCOL"]
    prospective = False
    if protocol_logs:
        try:
            prepared = datetime.fromisoformat(protocol_logs[0]["prepared_at"].replace("Z", "+00:00"))
            prospective = prepared.tzinfo is not None and all(
                prepared <= datetime.fromisoformat(o.executed_at.replace("Z", "+00:00"))
                for o in eric + scholar
            )
        except (ValueError, KeyError, TypeError):
            prospective = False
    if not prospective:
        errors.append(
            "Missing prospective protocol predating the observed searches; resume with the original --protocol"
        )
    status = "PASS" if eric and scholar and prospective else "PARTIAL" if eric or scholar else "BLOCKED"
    return {
        "status": status,
        "eric_executions": len(eric),
        "scholar_observations": len(scholar),
        "issues": errors
        + ([] if eric else ["No verifiable ERIC execution"])
        + ([] if scholar else ["GOOGLE_SCHOLAR_NOT_CHECKED: plan/legacy CSV alone is insufficient"]),
        "trust_boundary": "Artifact integrity and recorded provenance, not independent authentication of a human observation",
    }
