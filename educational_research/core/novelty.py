"""Competitive novelty challenge against the closest content, not search absence."""

from typing import Literal
from pydantic import Field
from ..models_base import Record
from .reading import evidence_registry


class ClosestStudy(Record):
    source_id: str
    rq: str
    population: str
    stage: str
    geography: str
    design: str
    sample: str
    constructs: list[str]
    theoretical_lens: str
    findings: str
    limitations: str
    overlap: str
    remaining_difference: str
    confidence: str
    evidence_ids: list[str]
    already_answers: bool = False


class NoveltyChallenge(Record):
    revised_question: str = ""
    tentative_contribution: str
    gap_kind: Literal["author_claimed", "researcher_inferred", "empirically_checked"]
    comparisons: list[ClosestStudy] = Field(default_factory=list)
    strongest_rival_id: str
    sceptical_case: str
    surviving_contribution: str
    conceptual_consequence: str
    search_boundary: str
    confidence_bounds: str
    method_fit: str
    basis: list[
        Literal[
            "mechanism",
            "theoretical_integration",
            "measurement",
            "contradictory_evidence",
            "geography_only",
            "population_only",
            "terminology_only",
            "mixed_methods_only",
        ]
    ]
    proposed_verdict: Literal[
        "GAP_SUPPORTED", "GAP_NARROW_BUT_DEFENSIBLE", "GAP_NOT_SUPPORTED", "INSUFFICIENT_EVIDENCE"
    ]


def challenge(novelty, sources, discovery_complete=False):
    if novelty is None:
        return {
            "verdict": "INSUFFICIENT_EVIDENCE",
            "status": "FAIL",
            "issues": ["No closest-study novelty challenge"],
            "comparisons": [],
            "boundary": "Bounded to searched sources and contexts",
        }
    n, issues = novelty, []
    known, registry = {s.id for s in sources}, evidence_registry(sources)
    ids = [c.source_id for c in n.comparisons]
    target = min(5, len(sources))
    if len(set(ids)) < max(3, target):
        issues.append(f"Closest-study coverage shortfall: {len(set(ids))}/{max(3, target)}")
    if n.strongest_rival_id not in ids:
        issues.append("Strongest rival was not compared")
    for c in n.comparisons:
        if c.source_id not in known or not c.evidence_ids or not set(c.evidence_ids) <= registry.keys():
            issues.append(f"{c.source_id}: unresolved closest-work evidence")
        elif any(registry[e]["source_id"] != c.source_id for e in c.evidence_ids):
            issues.append(f"{c.source_id}: misattributed closest-work evidence")
        if not all(
            [
                c.rq,
                c.population,
                c.stage,
                c.geography,
                c.design,
                c.sample,
                c.constructs,
                c.theoretical_lens,
                c.findings,
                c.limitations,
                c.overlap,
                c.remaining_difference,
            ]
        ):
            issues.append(f"{c.source_id}: missing comparison dimensions")
    cosmetic = {"geography_only", "population_only", "terminology_only", "mixed_methods_only"}
    answered = any(c.already_answers for c in n.comparisons)
    unsupported = answered and not (n.surviving_contribution and n.conceptual_consequence)
    unsupported |= bool(n.basis) and set(n.basis) <= cosmetic
    unsupported |= n.proposed_verdict == "GAP_NOT_SUPPORTED"
    if unsupported:
        verdict = "GAP_NOT_SUPPORTED"
        issues.append(
            "NOVELTY_NOT_SUPPORTED: closest work dissolves the proposed contribution or only cosmetic differences remain"
        )
    elif issues or not discovery_complete or not n.search_boundary or not n.confidence_bounds:
        verdict = "INSUFFICIENT_EVIDENCE"
    elif answered:
        verdict = "GAP_NARROW_BUT_DEFENSIBLE"
    else:
        verdict = n.proposed_verdict
    return {
        "verdict": verdict,
        "status": "PASS" if verdict in {"GAP_SUPPORTED", "GAP_NARROW_BUT_DEFENSIBLE"} else "FAIL",
        "issues": issues,
        "comparisons": [c.model_dump() for c in n.comparisons],
        "strongest_rival_id": n.strongest_rival_id,
        "sceptical_case": n.sceptical_case,
        "surviving_contribution": n.surviving_contribution
        if verdict in {"GAP_SUPPORTED", "GAP_NARROW_BUT_DEFENSIBLE"}
        else "",
        "revised_question": n.revised_question,
        "boundary": "Bounded to searched sources and contexts; " + n.search_boundary,
        "gap_kind": n.gap_kind,
        "interpretive_status": "REQUIRES_EXPERT_REVIEW",
    }
