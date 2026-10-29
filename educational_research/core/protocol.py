"""Prospective scoped protocol, immutable on resume unless explicitly amended."""

from pydantic import Field
from ..models_base import Record
from .discovery import utc_now


class SearchProtocol(Record):
    schema_version: str = "2.0"
    prepared_at: str = Field(default_factory=utc_now)
    problem: str
    candidate_rqs: list[str] = Field(min_length=1, max_length=3)
    focal_rq: str
    competing_explanations: list[str]
    population: str = "provisional"
    stage: str = "provisional"
    setting: str = "provisional"
    geography: str = "provisional"
    period: str = "provisional"
    constructs: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    intervention: str = "not specified"
    eligible_study_types: list[str] = Field(
        default_factory=lambda: ["empirical", "theoretical", "review", "critical/null evidence"]
    )
    language: str = "en-GB"
    inclusion: str
    exclusion: str
    scope_justification: str
    keyword_clusters: dict[str, list[str]]
    descriptors: list[str]
    citation_chaining: str
    amendments: list[dict] = Field(default_factory=list)


def provisional(config):
    return SearchProtocol(
        problem=config.topic,
        candidate_rqs=[config.rq]
        if config.rq
        else [
            f"How is {config.topic} conceptualised within a bounded educational context?",
            f"Which mechanisms or contextual conditions explain {config.topic}?",
            f"Where do findings or measures about {config.topic} converge or conflict?",
        ],
        focal_rq=config.rq
        or f"Which evidence explains {config.topic} within an explicitly bounded educational context?",
        competing_explanations=[
            "Selection and measurement explanations require comparison with substantive mechanisms"
        ],
        stage=config.education_level or "provisional",
        setting=config.context,
        geography=config.geography or "provisional",
        period=f"{config.year_from or 'unbounded'}–{config.year_to or config.search_date}",
        constructs=[config.topic],
        language=config.language,
        inclusion=config.inclusion,
        exclusion=config.exclusion,
        scope_justification="Provisional topic decomposition; agent must refine constructs, synonyms and populations before substantive selection",
        keyword_clusters={
            "focal": [config.topic],
            "theory": ["theory", "framework"],
            "contrary": ["null", "contradictory", "critical"],
            "spelling_alternatives": [
                "Check British/American spellings and construct-specific synonyms before expansion"
            ],
        },
        descriptors=config.descriptors,
        citation_chaining="Backward references plus permitted forward citation chasing, with actual provider recorded",
    )
