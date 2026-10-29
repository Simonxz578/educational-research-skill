"""Anchored editorial judgements are reviewable, never acceptance probabilities."""

import re
from typing import Literal
from pydantic import Field
from ..models_base import Record

DIMENSIONS = [
    "source_accuracy",
    "critical_synthesis",
    "bounded_novelty",
    "theory_fit",
    "method_fit",
    "inference",
    "education_context",
    "clarity_citations",
]
ANCHORS = {
    0: "absent or fabricated",
    1: "superficial or unsubstantiated",
    2: "partially evidenced",
    3: "strong with qualifications",
    4: "rigorous, coherent and traceable with credible counterarguments",
}


class EditorialScore(Record):
    score: int = Field(ge=0, le=4)
    rationale: str
    evidence_ids: list[str]
    remaining_judgement: str


class EditorialReview(Record):
    reviewer: str
    reviewer_kind: Literal["human", "agent"]
    reviewed_at: str
    scores: dict[str, EditorialScore]


def editorial_audit(
    review, gates, framework_audit, design_audit, evidence_ids, text="", synthetic=False
):
    flags = []
    for line, value in enumerate(text.splitlines(), 1):
        if re.search(r"not only.+but also|groundbreaking|revolutionary|first.ever", value, re.I):
            flags.append({"line": line, "kind": "RHETORICAL_OR_NOVELTY_REVIEW", "text": value[:180]})
    scores = {}
    if review:
        for dimension in DIMENSIONS:
            value = review.scores.get(dimension)
            valid = (
                value
                and value.rationale
                and value.evidence_ids
                and set(value.evidence_ids) <= set(evidence_ids)
            )
            scores[dimension] = (
                value.model_dump()
                if valid
                else {
                    "score": 0,
                    "rationale": "Missing or unresolved review evidence",
                    "remaining_judgement": "Review required",
                }
            )
    else:
        checks = {
            "source_accuracy": gates["G2"]["status"] == "PASS",
            "critical_synthesis": gates["G3"]["status"] == "PASS",
            "bounded_novelty": gates["G4"]["status"] == "PASS",
            "theory_fit": framework_audit["status"] == "PASS",
            "method_fit": design_audit["status"] in {"PASS", "NOT_APPLICABLE"},
        }
        scores = {
            d: {
                "score": 2 if checks.get(d, False) else 0,
                "rationale": "Automatic structural indication only; no editorial assessment supplied",
                "remaining_judgement": "Agent/expert judgement required",
            }
            for d in DIMENSIONS
        }
    critical = {"source_accuracy", "bounded_novelty", "theory_fit", "method_fit"}
    ready = bool(review) and all(v["status"] in {"PASS", "NOT_APPLICABLE"} for v in gates.values())
    ready &= all(scores[d]["score"] >= 3 for d in critical) and not synthetic
    return {
        "label": "EDITORIALLY_READY_FOR_EXPERT_REVIEW" if ready else "NOT_EDITORIALLY_READY",
        "assessment_kind": review.reviewer_kind if review else "AUTOMATIC_PROVISIONAL",
        "reviewer": review.reviewer if review else None,
        "scores": scores,
        "anchors": ANCHORS,
        "flags": flags,
        "notice": "Readiness is for expert review, not journal acceptance, peer review or a probability",
    }
