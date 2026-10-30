"""One quantity contract governs selection, close-reading acceptance and reader disclosure."""

from pydantic import Field
from ..models_base import Record
from .reading import reading_issues, reading_audit
from .evidence_depth import primary_depth_audit
from .gates import independent_key
from .score import select_diverse


class SourceSelection(Record):
    primary_evidence_shortfalls: dict[str, int] = Field(default_factory=dict)
    requested_user_N: int | None
    requested_semantics: str
    selection_target_N: int
    deep_review_requirement_N: int
    originating_user_intent: str | None
    quantity_origin: str
    explanation: str
    verified_relevant_selected_K: int
    qualified_deep_read_K: int
    selected_shortfall: int
    shortfall: int
    quotation_count: int
    selected_source_ids: list[str]
    candidate_source_ids: list[str] = Field(default_factory=list)


def select_sources(ranked, config):
    eligible = []
    candidates = []
    seen = set()
    for source in ranked:
        key = independent_key(source)
        issues = (
            reading_issues(source, reader_ready=True, require_depth=False)
            if config.presentation == "roadmap"
            else []
        )
        if key in seen:
            issues.append("Another selected record represents the same independent work")
        if issues:
            candidates.append({"source": source.public_record(), "reasons": issues})
        else:
            eligible.append(source)
            seen.add(key)
    selected = (
        select_diverse(eligible, config.quota) if config.selection_semantics == "exact" else eligible
    )
    chosen = {s.id for s in selected}
    candidates += [
        {"source": s.public_record(), "reasons": ["Deferred by exact source-count request"]}
        for s in eligible
        if s.id not in chosen
    ]
    qualified_ids = {
        r["source_id"]
        for r in reading_audit(selected, reader_ready=config.presentation == "roadmap")
        if r["qualified"]
    }
    qualified = {independent_key(s) for s in selected if s.id in qualified_ids}
    verified = sum(s.identity in {"VERIFIED", "SYNTHETIC"} for s in selected)
    selection = SourceSelection(
        **config.quantity_contract,
        primary_evidence_shortfalls={
            s.id: primary_depth_audit(s.reading, s.quotes)["shortfall"]
            for s in selected
            if config.presentation == "roadmap" and primary_depth_audit(s.reading, s.quotes)["shortfall"]
        },
        verified_relevant_selected_K=verified,
        qualified_deep_read_K=len(qualified),
        selected_shortfall=max(0, config.quota - verified),
        shortfall=max(0, config.deep_review_requirement - len(qualified)),
        quotation_count=sum(len(s.quotes) for s in selected),
        selected_source_ids=[s.id for s in selected],
        candidate_source_ids=[r["source"]["id"] for r in candidates],
    )
    return selected, candidates, selection
