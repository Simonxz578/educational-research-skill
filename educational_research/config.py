"""Run contract: manuscript length controls discovery quota only."""

from datetime import datetime
from math import ceil
from typing import Literal
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field

Mode = Literal["discover", "search", "synthesise", "gap", "outline", "audit", "revise", "full", "draft"]


def today():
    return datetime.now(ZoneInfo("UTC")).date().isoformat()


class Config(BaseModel):
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
    def quota(self):
        return self.target_references or ceil(self.target_words / 100)

    @property
    def candidate_target(self):
        return min(2 * self.quota, self.quota + 30)
