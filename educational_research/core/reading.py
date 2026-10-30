"""Auditable close-reading records; structural checks never certify comprehension."""

import hashlib
import re
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from pydantic import Field
from ..models_base import Record
from .evidence_types import EvidenceRights


class DocumentProvenance(Record):
    rights: EvidenceRights | None = None
    processing_permission: Literal["allowed", "local_only", "not_checked", "forbidden"] = "not_checked"
    permission_evidence: str = ""
    source_url: str
    local_path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    version: str
    legal_basis: str
    licence: str
    acquired_at: str


class ReadingEvidence(Record):
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=1)
    evidence_id: str
    content_type: Literal[
        "claim",
        "method",
        "result",
        "limitation",
        "counterpoint",
        "definition",
        "mechanism",
        "reasoning",
        "boundary",
    ]
    paraphrase: str
    exact_span: str = ""
    context: str = ""
    author_warrant: str = ""
    researcher_inference: str = ""
    qualification: str = ""
    locator: str
    status: Literal["checked_against_text", "not_checked"] = "not_checked"
    finding_kind: Literal[
        "observed", "tested", "reported", "interpretation", "potential", "not_applicable"
    ]


class FullTextReading(Record):
    quote_policy: Literal["short_excerpts_permitted", "no_reproduction", "not_checked"] = "not_checked"
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
    if path.suffix.lower() in {".html", ".htm", ".xml"}:
        from ..fulltext.documents import extract

        return extract(path.read_bytes())[0]
    if path.suffix.lower() == ".pdf":
        import fitz

        with fitz.open(path) as pdf:
            return " ".join(page.get_text() for page in pdf)
    return path.read_text(encoding="utf-8")


def evidence_registry(sources):
    registry = {
        f"{s.id}:{seg.id}": {"source_id": s.id, "locator": seg.locator, "url": seg.url}
        for s in sources
        for seg in s.segments
        if not (s.abstract_evidence and s.reading is None)
    }
    for s in sources:
        if s.abstract_evidence:
            registry[f"{s.id}:published_abstract"] = {
                "source_id": s.id,
                "locator": "Published abstract",
                "url": s.abstract_evidence.source_url,
                "scope": "ABSTRACT_ONLY",
            }
    return registry


def reader_scope(source):
    if not reading_issues(source, reader_ready=True, require_depth=False):
        return "FULL_TEXT"
    from ..fulltext.abstracts import abstract_issues

    if not abstract_issues(source):
        return "ABSTRACT_ONLY"
    return "METADATA_ONLY"


def reading_issues(source, check_files=True, reader_ready=False, require_depth=True):
    from .verification import canonical

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
    kinds = {e.content_type for e in r.evidence if e.status == "checked_against_text"}
    required_roles = [{"claim", "definition"}, {"limitation", "boundary", "counterpoint"}]
    if r.scholarly_kind in {"empirical", "review"}:
        required_roles += [{"method", "mechanism"}, {"result", "reasoning"}]
    if not all(kinds & role for role in required_roles) or len(r.evidence) < 2:
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
    if (
        reader_ready
        and source.assessments.get("relevance")
        and source.assessments["relevance"].value < 50
    ):
        issues.append("Low assessed relevance contradicts a highly relevant selected-work claim")
    if reader_ready:
        if r.document.rights is None:
            reusable = bool(re.search(r"CC[ -]?(?:BY|0)|creativecommons", r.document.licence, re.I))
            r.document.rights = EvidenceRights(
                access="allowed" if r.document.legal_basis else "not_checked",
                access_basis=r.document.legal_basis,
                processing="allowed" if r.document.processing_permission == "allowed" else "not_checked",
                processing_basis=r.document.permission_evidence,
                private_retention="allowed" if reusable else "not_checked",
                retention_basis=r.document.licence if reusable else "",
                public_quotation="allowed"
                if r.quote_policy == "short_excerpts_permitted"
                else "denied"
                if r.quote_policy == "no_reproduction"
                else "not_checked",
                quotation_basis="Recorded source quotation review: " + r.quote_policy,
                licence_url=source.permissive_licence_url or "",
            )
        if any(
            getattr(r.document.rights, k) != "allowed"
            for k in ["access", "processing", "private_retention"]
        ):
            issues.append(
                "Separate source access, processing and private-retention rights must be resolved"
            )
            return sorted(set(issues))
        if source.quotes and r.document.rights.public_quotation != "allowed":
            issues.append("Public quotation rights are separate from private inspection")
        if source.quote_budget > 20:
            rights = r.document.rights
            licence_matches = (
                bool(re.search(r"CC[ -]?(?:BY|0)|creativecommons", r.document.licence, re.I))
                and bool(source.permissive_licence_url)
                and rights.public_quotation == "allowed"
                and bool(rights.quotation_basis)
            )
            explicit = (
                rights.public_word_allowance is not None
                and rights.public_word_allowance >= source.quote_budget
                and bool(rights.quotation_basis)
            )
            if not (licence_matches or explicit):
                issues.append("Extended public reproduction lacks verified licence/permission scope")
        if not source.synthetic and source.acquisition is None:
            issues.append(
                "Non-synthetic roadmap work requires validated acquisition or an explicitly permitted local document validation"
            )
        if require_depth:
            from .evidence_depth import primary_depth_audit
            from .verification import verbatim_audit

            issues += primary_depth_audit(r, source.quotes)["issues"]
            issues += verbatim_audit(source)["issues"]
        from ..fulltext.acquire import acquisition_issues

        issues += acquisition_issues(source.acquisition, r)
        if r.document.processing_permission != "allowed" or not r.document.permission_evidence:
            issues.append(
                "Automated/hosted processing permission and its evidence must be recorded; access alone is insufficient"
            )
        anchor_types = {e.content_type for e in r.evidence if e.status == "checked_against_text"}
        roles = [
            {"claim", "definition"},
            {"method", "mechanism"},
            {"result", "reasoning"},
            {"limitation", "boundary", "counterpoint"},
        ]
        if len(r.evidence) < 4 or not all(anchor_types & role for role in roles):
            issues.append("Roadmap requires four distinct substantive evidence roles")
        spans = []
        for entry in r.evidence:
            seg = next(
                (seg for seg in source.segments if f"{source.id}:{seg.id}" == entry.evidence_id), None
            )
            if not (
                entry.exact_span
                and entry.context
                and entry.author_warrant
                and entry.researcher_inference
                and entry.qualification
            ):
                issues.append(
                    f"{entry.evidence_id}: missing private exact span/context/warrant/distinct inference"
                )
            elif seg and seg.text and canonical(entry.exact_span) not in canonical(seg.text):
                issues.append(f"{entry.evidence_id}: anchor is not an exact source span")
            if (
                entry.exact_span.strip()
                and " ".join(entry.paraphrase.split()).casefold()
                == " ".join(entry.exact_span.split()).casefold()
            ):
                issues.append(
                    f"{entry.evidence_id}: verbatim anchor cannot be passed off as a paraphrase"
                )
            spans.append(" ".join(entry.exact_span.split()).casefold())
        if (
            len(set(spans)) < 4
            or len({" ".join(e.paraphrase.split()).casefold() for e in r.evidence}) < 4
        ):
            issues.append("Repeated sentences cannot masquerade as four independent evidence anchors")
        if r.quote_policy == "not_checked":
            issues.append("Reader quotation permissions have not been checked")
        elif r.quote_policy == "no_reproduction" and source.quotes:
            issues.append("Quote reproduction contradicts the source permissions")
        elif r.quote_policy == "short_excerpts_permitted" and not 1 <= len(source.quotes) <= 2:
            issues.append(
                "Roadmap requires one or two verified original micro-excerpts per quotable work"
            )
        checked_ids = {e.evidence_id for e in r.evidence}
        if any(f"{source.id}:{q.segment_id}" not in checked_ids for q in source.quotes):
            issues.append("Reader excerpt is not attached to a checked substantive anchor")
        from .evidence_depth import quotation_usage

        if quotation_usage(source) > source.quote_budget:
            issues.append(
                "Cumulative reader reproduction, including repeated fragments in paraphrases, exceeds the per-work budget"
            )
    if check_files:
        path = Path(r.document.local_path)
        if not path.is_file() or sha256_file(path) != r.document.sha256:
            issues.append("Full-text artifact missing or digest mismatch")
        else:
            try:
                actual = canonical(document_text(str(path.resolve()), r.document.sha256))
                segments = {f"{source.id}:{s.id}": s for s in source.segments}
                for entry in r.evidence:
                    seg = segments.get(entry.evidence_id)
                    if reader_ready and entry.exact_span and canonical(entry.exact_span) not in actual:
                        issues.append(
                            f"{entry.evidence_id}: exact anchor absent from attached full text"
                        )
                    # Public ledgers intentionally omit protected text; only the original
                    # native input can support this exact-span content check.
                    if seg and seg.text and canonical(seg.text) not in actual:
                        issues.append(f"{entry.evidence_id}: passage absent from attached full text")
                for quote in source.quotes:
                    wording = quote.text if hasattr(quote, "text") else quote["text"]
                    if canonical(wording) not in actual:
                        issues.append("Quote absent from attached full text")
            except (OSError, UnicodeError, RuntimeError, ValueError):
                issues.append(
                    "Full-text artifact cannot be inspected as native text; OCR requires review"
                )
    return sorted(set(issues))


def reading_audit(sources, reader_ready=False, synthesis=None):
    from .verification import verbatim_audit
    from .evidence_depth import (
        primary_depth_audit,
        cross_source_boilerplate,
        quotation_usage,
        reader_extra_texts,
    )

    duplicates = cross_source_boilerplate(sources) if reader_ready else {}

    def inspection(source):
        if reader_scope(source) == "ABSTRACT_ONLY":
            from .evidence_depth import english_words

            return {
                "kind": "VERBATIM_PRIMARY_TEXT",
                "scope": "ABSTRACT_ONLY",
                "verified_original_words": 0,
                "abstract_original_words": len(english_words(source.abstract_evidence.text)),
                "original_word_shortfall": None,
                "gate_status": "NOT_APPLICABLE_TO_ABSTRACT / NOT_FULL_TEXT_VERIFIED",
                "issues": [],
            }
        return verbatim_audit(source)

    rows = [
        {
            "source_id": s.id,
            "qualified": not reading_issues(s, reader_ready=reader_ready) and s.id not in duplicates,
            "issues": reading_issues(s, reader_ready=reader_ready)
            + (
                ["Duplicated source boilerplate: " + ", ".join(duplicates[s.id])]
                if s.id in duplicates
                else []
            ),
            "primary_evidence_depth": primary_depth_audit(s.reading, s.quotes) if reader_ready else None,
            "verbatim_primary_text": inspection(s) if reader_ready else None,
            "reading": s.public_record().get("reading"),
            "interpretive_validity": "REQUIRES_AGENT_OR_EXPERT_REVIEW",
        }
        for s in sources
    ]
    if reader_ready and synthesis is not None:
        for source, row in zip(sources, rows):
            used = quotation_usage(source, reader_extra_texts(source, synthesis))
            row["reader_quotation_units"] = used
            if used > source.quote_budget:
                row["qualified"] = False
                row["issues"].append(
                    "Cumulative reader quotation budget exceeded across source, argument and framework prose"
                )
    return rows
