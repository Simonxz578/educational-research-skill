"""One quantity contract governs selection, close-reading acceptance and reader disclosure."""

from pydantic import Field
from ..models_base import Record
from .reading import reading_issues, reading_audit, reader_scope
from .gates import independent_key
from .verification import verbatim_audit
from ..fulltext.abstracts import abstract_issues
from .score import select_diverse


class SourceSelection(Record):
    included_N: int = 0
    full_text_verified_K: int = 0
    abstract_only_A: int = 0
    full_text_provisional_P: int = 0
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
            if (
                config.presentation == "roadmap"
                and not abstract_issues(source)
                and key not in seen
                and not (
                    source.assessments.get("relevance") and source.assessments["relevance"].value < 50
                )
            ):
                eligible.append(source)
                seen.add(key)
            else:
                candidates.append({"source": source.public_record(), "reasons": issues})
        else:
            eligible.append(source)
            seen.add(key)
    essential = [s for s in eligible if s.role.casefold() in {"essential", "landmark", "foundational"}]
    selected = (
        (
            essential[: config.quota]
            + select_diverse(
                [s for s in eligible if s not in essential], max(0, config.quota - len(essential))
            )
        )
        if config.selection_semantics == "exact" and essential
        else select_diverse(eligible, config.quota)
        if config.selection_semantics == "exact"
        else eligible
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
            s.id: verbatim_audit(s)["original_word_shortfall"]
            for s in selected
            if config.presentation == "roadmap"
            and reader_scope(s) == "FULL_TEXT"
            and verbatim_audit(s)["original_word_shortfall"]
        },
        included_N=len(selected),
        full_text_verified_K=len(qualified),
        abstract_only_A=sum(
            bool(reading_issues(s, reader_ready=True, require_depth=False)) and not abstract_issues(s)
            for s in selected
        )
        if config.presentation == "roadmap"
        else 0,
        verified_relevant_selected_K=verified,
        qualified_deep_read_K=len(qualified),
        selected_shortfall=max(0, config.quota - verified),
        shortfall=max(0, config.deep_review_requirement - len(qualified)),
        quotation_count=sum(
            bool(s.abstract_evidence.quotation) if reader_scope(s) == "ABSTRACT_ONLY" else len(s.quotes)
            for s in selected
        ),
        selected_source_ids=[s.id for s in selected],
        candidate_source_ids=[r["source"]["id"] for r in candidates],
    )
    selection.full_text_provisional_P = (
        len(selected) - selection.full_text_verified_K - selection.abstract_only_A
        if config.presentation == "roadmap"
        else 0
    )
    return selected, candidates, selection
