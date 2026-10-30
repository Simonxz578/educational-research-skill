"""Validated records keep scholarly claims, evidence and researcher interpretations separate."""

import re
from typing import Literal
from pydantic import Field, field_validator, model_validator
from .config import today
from .models_base import Record
from .core.reading import FullTextReading
from .core.access import FullTextAcquisition, FullTextLocation
from .core.evidence_types import AbstractEvidence


def quotation_units(text):
    """Words plus individual CJK characters: no whitespace loophole for source quotes."""
    cjk = re.findall(r"[\u2e80-\u9fff]", text)
    other = re.sub(r"[\u2e80-\u9fff]", " ", text)
    return len(cjk) + len(re.findall(r"\S+", other))


class Author(Record):
    family: str = ""
    given: str = ""
    literal: str = ""

    @model_validator(mode="after")
    def named(self):
        if not (self.family or self.literal):
            raise ValueError("Author needs family or organisation literal")
        return self


class Segment(Record):
    id: str
    text: str
    url: str
    locator: str = "location unknown"
    pdf_page: int | None = Field(default=None, ge=1)
    printed_page: str | None = None
    licence: str = "not verified"
    checked_at: str = Field(default_factory=today)


class Quote(Record):
    text: str
    segment_id: str
    translation: str | None = None
    translation_kind: Literal["user", "published", "not translated"] = "not translated"


class Extraction(Record):
    text: str
    segment_ids: list[str] = Field(min_length=1)
    basis: Literal["source-author claim", "source evidence", "researcher interpretation"]


class Metric(Record):
    name: Literal["JIF", "SJR", "CiteScore", "h5-index", "article_citations", "FWCI"]
    value: float = Field(ge=0)
    source: str
    checked_at: str
    year: int | None = None
    category: str | None = None
    quartile: str | None = None

    @model_validator(mode="after")
    def context(self):
        if self.name in {"JIF", "SJR", "CiteScore", "h5-index"} and (not self.year or not self.category):
            raise ValueError("Journal metrics require year and subject category")
        if not self.source.startswith(("https://", "http://")):
            raise ValueError("Metric needs a provenance URL")
        return self


class Assessment(Record):
    value: float = Field(ge=0, le=100)
    rationale: str
    checked_at: str


class Source(Record):
    schema_version: Literal["1.0", "2.0", "3.0", "4.2", "4.3", "4.4"] = "4.4"
    abstract_evidence: AbstractEvidence | None = None
    reading: FullTextReading | None = None
    acquisition: FullTextAcquisition | None = None
    full_text_locations: list[FullTextLocation] = Field(default_factory=list)
    work_id: str | None = None
    id: str
    title: str
    authors: list[Author] = Field(default_factory=list)
    year: int | None = None
    online_year: int | None = None
    issue_year: int | None = None
    type: str = "article-journal"
    journal: str = ""
    publisher: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str | None = None
    url: str = ""
    eric_id: str | None = None
    peer_reviewed: bool | None = None
    descriptors: list[str] = Field(default_factory=list)
    education_level: str = "not reported"
    country: str = "not reported"
    participants: str = "not reported"
    design: str = "not reported"
    evidence_kind: str = "not verified"
    objective: str = "not verified"
    theory: str = "not verified"
    abstract: str = ""
    summary: str = "not verified"
    source_argument: str = "not verified"
    target_argument: str = "not constructed"
    relevance_explanation: str = "not assessed"
    limitations: str = "not verified"
    evidence_strength: str = "not assessed"
    cluster: str = "Unclassified"
    role: str = "candidate"
    comparison_ids: list[str] = Field(default_factory=list)
    relationship: str = "not assessed"
    access: Literal[
        "FULL_TEXT_VERIFIED",
        "ABSTRACT_ONLY",
        "METADATA_ONLY",
        "USER_SUPPLIED",
        "UNAVAILABLE",
        "FULL_TEXT_READ_BY_AGENT",
        "USER_SUPPLIED_FULL_TEXT",
        "UNVERIFIED",
    ] = "METADATA_ONLY"
    identity: Literal["VERIFIED", "UNVERIFIED", "CONFLICT", "SYNTHETIC"] = "UNVERIFIED"
    publication_status: str = "not checked"
    checked_at: str = Field(default_factory=today)
    providers: list[str] = Field(default_factory=list)
    segments: list[Segment] = Field(default_factory=list)
    quotes: list[Quote] = Field(default_factory=list)
    extractions: dict[str, Extraction] = Field(default_factory=dict)
    metrics: list[Metric] = Field(default_factory=list)
    assessments: dict[str, Assessment] = Field(default_factory=dict)
    provenance: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    quote_budget: int = Field(default=20, ge=0, le=200)
    permissive_licence_url: str | None = None
    synthetic: bool = False

    @model_validator(mode="before")
    @classmethod
    def migrate_v1(cls, value):
        if isinstance(value, dict) and "schema_version" not in value:
            value = {**value, "schema_version": "1.0"}
        return value

    @field_validator("doi")
    @classmethod
    def valid_doi(cls, value):
        if value is None:
            return value
        value = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).lower()
        if not re.fullmatch(r"10\.\d{4,9}/\S+", value):
            raise ValueError("Invalid DOI syntax; leave genuinely DOI-less works null")
        return value

    @model_validator(mode="after")
    def traceability(self):
        from .core.verification import canonical

        if self.synthetic and self.identity != "SYNTHETIC":
            raise ValueError("Synthetic records must have SYNTHETIC identity")
        if self.identity == "SYNTHETIC" and not self.synthetic:
            raise ValueError("SYNTHETIC identity requires synthetic flag")
        if (
            self.quote_budget > (25 if self.schema_version == "1.0" else 20)
            and not self.permissive_licence_url
        ):
            raise ValueError("Extended quotation budget requires licence provenance")
        segments = {s.id: s for s in self.segments}
        if self.access == "FULL_TEXT_VERIFIED" and not self.segments:
            raise ValueError("Full-text verification requires actual evidence segments")
        if len(segments) != len(self.segments):
            raise ValueError("Duplicate segment IDs")
        if self.quotes and self.access not in {
            "FULL_TEXT_VERIFIED",
            "USER_SUPPLIED",
            "FULL_TEXT_READ_BY_AGENT",
            "USER_SUPPLIED_FULL_TEXT",
        }:
            raise ValueError("No verified excerpts from abstract/metadata-only records")
        for q in self.quotes:
            seg = segments.get(q.segment_id)
            if not seg or canonical(q.text) not in canonical(seg.text) or not q.text.strip():
                raise ValueError("Quote is not an exact source span")
            if seg.locator == "location unknown" or not seg.url:
                raise ValueError("Quote requires a locator and access URL")
        if sum(quotation_units(q.text) for q in self.quotes) > self.quote_budget:
            raise ValueError("Per-source quotation budget exceeded")
        for field, extraction in self.extractions.items():
            if not all(i in segments for i in extraction.segment_ids):
                raise ValueError("Extraction points to a missing segment")
            if field == "source_argument" and extraction.basis != "source-author claim":
                raise ValueError("Source argument must be attributed to source authors")
            if field == "target_argument" and extraction.basis != "researcher interpretation":
                raise ValueError("Target argument must be researcher interpretation")
        for field in ("summary", "source_argument", "target_argument"):
            value = getattr(self, field)
            if value not in {"not verified", "not constructed"}:
                extraction = self.extractions.get(field)
                if not extraction or extraction.text != value:
                    raise ValueError(f"{field} requires matching extraction provenance")
        if self.source_argument == self.target_argument and self.source_argument != "not verified":
            raise ValueError("Source and target arguments must remain distinct")
        return self

    def public_record(self):
        record = self.model_dump()
        # Run outputs do not reproduce full protected texts or local upload paths.
        record["segments"] = [s.model_dump(exclude={"text"}) for s in self.segments]
        if (
            self.reading
            and self.reading.document.rights
            and self.reading.document.rights.private_retention != "allowed"
        ):
            record["reading"] = None
            record["quotes"] = []
            if record.get("acquisition"):
                record["acquisition"]["paragraphs"] = []
        return record


def restore_public_source(row):
    """Rehydrate redacted private matrix records without pretending absent text was checked."""
    data = {k: v for k, v in row.items() if k in Source.model_fields}
    data["authors"] = [Author.model_validate(a) for a in row["authors"]]
    data["segments"] = [
        Segment.model_validate({**s, "text": s.get("text", "")}) for s in row["segments"]
    ]
    data["quotes"] = [Quote.model_validate(q) for q in row["quotes"]]
    data["assessments"] = {k: Assessment.model_validate(v) for k, v in row["assessments"].items()}
    data["extractions"] = {
        k: Extraction.model_validate(v) for k, v in row.get("extractions", {}).items()
    }
    data["metrics"] = [Metric.model_validate(v) for v in row.get("metrics", [])]
    data["full_text_locations"] = [
        FullTextLocation.model_validate(v) for v in row.get("full_text_locations", [])
    ]
    data["reading"] = FullTextReading.model_validate(row["reading"]) if row.get("reading") else None
    data["acquisition"] = (
        FullTextAcquisition.model_validate(row["acquisition"]) if row.get("acquisition") else None
    )
    data["abstract_evidence"] = (
        AbstractEvidence.model_validate(row["abstract_evidence"])
        if row.get("abstract_evidence")
        else None
    )
    return Source.model_construct(**data)
