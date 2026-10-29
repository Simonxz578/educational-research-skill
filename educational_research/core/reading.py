"""Auditable close-reading records; structural checks never certify comprehension."""

import hashlib
import re
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from pydantic import Field
from ..models_base import Record


class DocumentProvenance(Record):
    source_url: str
    local_path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    version: str
    legal_basis: str
    licence: str
    acquired_at: str


class ReadingEvidence(Record):
    evidence_id: str
    content_type: Literal["claim", "method", "result", "limitation", "counterpoint"]
    paraphrase: str
    locator: str
    status: Literal["checked_against_text", "not_checked"] = "not_checked"
    finding_kind: Literal[
        "observed", "tested", "reported", "interpretation", "potential", "not_applicable"
    ]


class FullTextReading(Record):
    source_id: str
    access_status: Literal[
        "FULL_TEXT_READ_BY_AGENT",
        "USER_SUPPLIED_FULL_TEXT",
        "ABSTRACT_ONLY",
        "METADATA_ONLY",
        "UNVERIFIED",
    ]
    document: DocumentProvenance
    read_at: str
    reader: str
    coverage: Literal["whole_work", "relevant_chapter", "substantive_sections", "fragment"]
    scope_description: str
    scholarly_kind: Literal["empirical", "theoretical", "review", "policy"]
    central_thesis: str
    question: str
    population: str
    stage: str
    setting: str
    design: str
    constructs: list[str]
    analytic_approach: str
    findings: str
    limitations: str
    relevance_to_rq: str
    relevance_rationale: str
    highly_relevant: bool
    inference_limits: str
    evidence: list[ReadingEvidence] = Field(min_length=1)
    not_applicable: dict[str, str] = Field(default_factory=dict)
    overlaps: list[str] = Field(default_factory=list)
    opposing_source_ids: list[str] = Field(default_factory=list)
    own_implication: str


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=128)
def document_text(path, digest):
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        import fitz

        with fitz.open(path) as pdf:
            return " ".join(page.get_text() for page in pdf)
    return path.read_text(encoding="utf-8")


def evidence_registry(sources):
    return {
        f"{s.id}:{seg.id}": {"source_id": s.id, "locator": seg.locator, "url": seg.url}
        for s in sources
        for seg in s.segments
    }


def reading_issues(source, check_files=True):
    r = source.reading
    issues = []
    if not r:
        return ["No first-class full-text reading record"]
    if r.source_id != source.id:
        issues.append("Reading record belongs to another source")
    if r.access_status not in {"FULL_TEXT_READ_BY_AGENT", "USER_SUPPLIED_FULL_TEXT"}:
        issues.append("Reading access is not full text")
    if source.access not in {
        "FULL_TEXT_VERIFIED",
        "USER_SUPPLIED",
        "FULL_TEXT_READ_BY_AGENT",
        "USER_SUPPLIED_FULL_TEXT",
    }:
        issues.append("Source access contradicts the reading record")
    if source.identity not in {"VERIFIED", "SYNTHETIC"}:
        issues.append("Citation identity unresolved")
    if not r.highly_relevant or not r.relevance_to_rq or not r.relevance_rationale:
        issues.append("Exact RQ relevance not reviewed")
    if r.coverage not in {"whole_work", "relevant_chapter"}:
        issues.append("Fragment/selected sections do not establish deep full-text reading")
    if r.coverage == "relevant_chapter" and r.scholarly_kind != "theoretical":
        issues.append("Chapter scope must be justified for theoretical works")
    required = {"claim", "limitation"} | (
        {"method", "result"} if r.scholarly_kind in {"empirical", "review"} else set()
    )
    kinds = {e.content_type for e in r.evidence if e.status == "checked_against_text"}
    if not required <= kinds or len(r.evidence) < 2:
        issues.append("Missing substantive claim/method/result/limitation coverage")
    registry = evidence_registry([source])
    for e in r.evidence:
        linked = registry.get(e.evidence_id)
        if (
            not linked
            or e.locator != linked["locator"]
            or e.locator.lower() in {"location unknown", "abstract", "eric abstract"}
        ):
            issues.append(f"Unresolved or non-substantive locator: {e.evidence_id}")
        if e.status != "checked_against_text" or not e.paraphrase.strip():
            issues.append(f"Evidence not checked: {e.evidence_id}")
    if len({e.evidence_id for e in r.evidence}) != len(r.evidence):
        issues.append("Repeated passage IDs cannot stand in for content coverage")
    if not all(
        str(getattr(r, f)).strip()
        for f in (
            "reader",
            "read_at",
            "central_thesis",
            "question",
            "scope_description",
            "analytic_approach",
            "findings",
            "limitations",
            "inference_limits",
            "own_implication",
        )
    ):
        issues.append("Incomplete close-reading dimensions")
    if not all(
        str(getattr(r.document, f)).strip()
        for f in ("source_url", "version", "legal_basis", "licence", "acquired_at")
    ):
        issues.append("Missing legal access/version provenance")
    for date in [r.read_at, r.document.acquired_at]:
        try:
            parsed = datetime.fromisoformat(date.replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed > datetime.now(timezone.utc):
                issues.append("Reading dates must be recorded past timestamps with timezone")
        except ValueError:
            issues.append("Invalid reading/access timestamp")
    if r.central_thesis != source.source_argument:
        issues.append("Reading thesis and source-author argument disagree")
    if source.quote_budget > 20 and not source.permissive_licence_url:
        issues.append("Substantive v2 quotation budget exceeds 20 without rights provenance")
    if check_files:
        path = Path(r.document.local_path)
        if not path.is_file() or sha256_file(path) != r.document.sha256:
            issues.append("Full-text artifact missing or digest mismatch")
        else:
            try:
                actual = re.sub(r"\s+", " ", document_text(str(path.resolve()), r.document.sha256))
                segments = {f"{source.id}:{s.id}": s for s in source.segments}
                for entry in r.evidence:
                    seg = segments.get(entry.evidence_id)
                    # Public ledgers intentionally omit protected text; only the original
                    # native input can support this exact-span content check.
                    if seg and seg.text and re.sub(r"\s+", " ", seg.text).strip() not in actual:
                        issues.append(f"{entry.evidence_id}: passage absent from attached full text")
                for quote in source.quotes:
                    wording = quote.text if hasattr(quote, "text") else quote["text"]
                    if re.sub(r"\s+", " ", wording).strip() not in actual:
                        issues.append("Quote absent from attached full text")
            except (OSError, UnicodeError, RuntimeError, ValueError):
                issues.append(
                    "Full-text artifact cannot be inspected as native text; OCR requires review"
                )
    return sorted(set(issues))


def reading_audit(sources):
    return [
        {
            "source_id": s.id,
            "qualified": not reading_issues(s),
            "issues": reading_issues(s),
            "reading": s.reading.model_dump() if s.reading else None,
            "interpretive_validity": "REQUIRES_AGENT_OR_EXPERT_REVIEW",
        }
        for s in sources
    ]
