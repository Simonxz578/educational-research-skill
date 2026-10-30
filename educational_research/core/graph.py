"""Typed evidence graph with referential integrity and cycle detection."""

from typing import Literal
from pydantic import Field, model_validator
from ..models_base import Record
from .framework import Framework
from .design import StudyDesign
from .novelty import NoveltyChallenge
from .editorial import EditorialReview


class Claim(Record):
    evidence_scope: Literal["FULL_TEXT", "PRELIMINARY_ABSTRACT"] = "FULL_TEXT"
    id: str
    text: str
    source_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    warrant: str = "not specified"
    warrant_id: str = ""
    objection: str = "Rival interpretation requires review"
    objection_id: str = ""
    qualification: str = "Provisional; evaluate evidence access and inference limits"
    confidence: str = "provisional"
    comparison: str = ""
    author_positions: dict[str, str] = Field(default_factory=dict)
    opposing_evidence_ids: list[str] = Field(default_factory=list)
    own_inference: str = ""
    scope: str = ""
    theory_ids: list[str] = Field(default_factory=list)
    rq_ids: list[str] = Field(default_factory=list)
    section: str = ""
    paragraph_plan: list[str] = Field(default_factory=list)
    transition_warrant: str = ""
    relative_strength: str = ""
    depends_on: list[str] = Field(default_factory=list)


class Edge(Record):
    source: str
    target: str
    kind: Literal[
        "supports",
        "contradicts",
        "qualifies",
        "depends_on",
        "extends",
        "different_context",
        "method_incompatible",
        "same_construct_different_measure",
    ]
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)


class Synthesis(Record):
    schema_version: str = "2.0"
    framework: Framework | None = None
    study_design: StudyDesign | None = None
    novelty: NoveltyChallenge | None = None
    editorial_review: EditorialReview | None = None
    thesis: str = "Not yet warranted: complete critical extraction and closest-work comparison"
    claims: list[Claim] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)
    gaps: list[dict] = Field(default_factory=list)
    definitions: dict[str, str] = Field(default_factory=dict)
    alignment: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique(self):
        if len({c.id for c in self.claims}) != len(self.claims):
            raise ValueError("Duplicate claim IDs")
        return self


def validate_graph(synthesis, sources):
    source_ids = {s.id for s in sources}
    from .reading import evidence_registry

    evidence_ids = set(evidence_registry(sources))
    claims = {c.id: c for c in synthesis.claims}
    for claim in synthesis.claims:
        if not set(claim.source_ids) <= source_ids or not set(claim.evidence_ids) <= evidence_ids:
            raise ValueError(f"{claim.id}: unknown source/evidence IDs")
        if any(e.split(":", 1)[0] not in claim.source_ids for e in claim.evidence_ids):
            raise ValueError("Evidence does not belong to the claim’s attributed sources")
        if not set(claim.depends_on) <= claims.keys():
            raise ValueError("Unknown claim dependency")
        if len(claim.text.split()) > 120:
            raise ValueError("Default pack claim exceeds 120 words")

    def walk(node, trail):
        if node in trail:
            raise ValueError("Argument dependencies contain a cycle")
        for dep in claims[node].depends_on:
            walk(dep, trail | {node})

    for key in claims:
        walk(key, set())
    for edge in synthesis.edges:
        if (
            edge.source not in source_ids | claims.keys()
            or edge.target not in source_ids | claims.keys()
        ):
            raise ValueError("Unknown edge endpoint")
    for ids in synthesis.alignment.values():
        if not set(ids) <= claims.keys():
            raise ValueError("Alignment references unknown claims")
    return synthesis


def construct(sources):
    """Preserve extracted target arguments; do not manufacture a cross-paper consensus."""
    claims = []
    for s in sources:
        if s.target_argument != "not constructed":
            ex = s.extractions["target_argument"]
            n = len(claims) + 1
            claims.append(
                Claim(
                    id=f"C{n:03}",
                    text=s.target_argument,
                    source_ids=[s.id],
                    evidence_ids=[f"{s.id}:{i}" for i in ex.segment_ids],
                    warrant="Researcher interpretation; compare rival explanations",
                    warrant_id=f"W{n:03}",
                    objection_id=f"O{n:03}",
                )
            )
            if len(claims) == 7:
                break
    return Synthesis(claims=claims)
