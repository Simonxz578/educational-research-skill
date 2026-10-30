"""Run contract: manuscript length controls discovery quota only."""

from datetime import datetime
from math import ceil
from typing import Literal
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field

Mode = Literal[
    "discover", "search", "synthesise", "gap", "outline", "audit", "revise", "full", "draft", "framework"
]


def today():
    return datetime.now(ZoneInfo("UTC")).date().isoformat()


class Config(BaseModel):
    full_text_mode: Literal["auto", "off", "revalidate"] = "auto"
    full_text_limit: int | None = Field(default=None, ge=1)
    full_text_max_routes: int = Field(default=8, ge=1, le=20)
    presentation: Literal["roadmap", "evidence-pack"] = "roadmap"
    include_audit_pdf: bool = False
    source_semantics: Literal["exact", "at_least"] | None = None
    user_quantity_intent: str | None = None
    search_candidate_budget: int | None = Field(default=None, ge=1)
    quality_level: Literal["exploratory", "substantive"] | None = None
    min_reviewed_fulltexts: int = Field(default=10, ge=1)
    require_verifiable_scholar: bool = False
    strict_quality_gates: bool = False
    empirical_proposal: bool = False
    topic: str = "Manuscript evidence audit"
    target_words: int = Field(default=1000, gt=0)
    target_references: int | None = Field(default=None, gt=0)
    mode: Mode = "full"
    language: str = "en-GB"
    offline: bool = False
    rq: str | None = None
    context: str = "not specified; scope provisional"
    methodology: str = "not specified; proposed methods require review"
    discipline: str = "education"
    framework: str = "not fixed"
    author_thesis: str = "Provisional; construct after source comparison"
    geography: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    peer_reviewed: bool = False
    descriptors: list[str] = Field(default_factory=list)
    education_level: str | None = None
    inclusion: str = (
        "Direct conceptual/contextual relevance; identifiable work; evidence access disclosed"
    )
    exclusion: str = "Duplicate works; unresolved identity; out-of-scope content; retracted findings"
    search_date: str = Field(default_factory=today)

    @property
    def substantive(self):
        # Explicit exploratory settings never relax strict substantive mode acceptance.
        return self.mode not in {"discover", "search"} or self.quality_level == "substantive"

    @property
    def quota(self):
        return (
            self.target_references
            if self.target_references is not None
            else max(10, ceil(self.target_words / 100))
        )

    @property
    def selection_semantics(self):
        return self.source_semantics or ("exact" if self.target_references is not None else "at_least")

    @property
    def deep_review_requirement(self):
        return max(10, self.quota, self.min_reviewed_fulltexts)

    @property
    def quantity_contract(self):
        return {
            "requested_user_N": self.target_references,
            "requested_semantics": self.selection_semantics,
            "selection_target_N": self.quota,
            "deep_review_requirement_N": self.deep_review_requirement,
            "originating_user_intent": self.user_quantity_intent,
            "quantity_origin": "explicit_source_count"
            if self.target_references is not None
            else "word_count_heuristic_with_floor_10",
            "explanation": "Explicit source count takes precedence; ten is a floor, not a selection ceiling",
        }

    @property
    def candidate_budget(self):
        return self.search_candidate_budget or max(40, self.quota * 4)

    @property
    def candidate_target(self):
        return min(self.candidate_budget, self.quota + max(10, ceil(self.quota / 2)))
