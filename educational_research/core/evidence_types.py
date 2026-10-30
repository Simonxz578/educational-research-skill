"""Distinct source, explanation and interpretation layers; separate usage decisions."""

from typing import Literal
from pydantic import Field
from ..models_base import Record

Decision = Literal["allowed", "denied", "not_checked"]


class EvidenceRights(Record):
    public_word_allowance: int | None = Field(default=None, ge=0)
    access: Decision = "not_checked"
    processing: Decision = "not_checked"
    private_retention: Decision = "not_checked"
    public_quotation: Decision = "not_checked"
    access_basis: str = ""
    processing_basis: str = ""
    retention_basis: str = ""
    quotation_basis: str = ""
    licence_url: str = ""


class TextLayer(Record):
    kind: Literal["VERBATIM_PRIMARY_TEXT", "SOURCE_ANCHORED_EXPLANATION", "OUR_INTERPRETATION"]
    text: str
    word_count: int = Field(ge=0)
    evidence_ids: list[str] = Field(default_factory=list)
    scope: Literal["FULL_TEXT", "ABSTRACT_ONLY"] = "FULL_TEXT"


class AbstractEvidence(Record):
    source_id: str
    publication_id: str
    title: str
    source_url: str
    provider: Literal["publisher", "Crossref", "ERIC", "user_attested"]
    version: Literal["publishedAbstract"] = "publishedAbstract"
    text: str
    artifact_path: str
    artifact_sha256: str
    extraction_sha256: str
    checked_at: str
    identity_verified: bool
    rights: EvidenceRights
    explanation: str = ""
    explanation_checked: bool = False
    interpretation: str = (
        "Full-text evidence, detailed methods and inferential limits have not been checked."
    )
    quotation: str = ""
    quotation_locator: str = "Published abstract"
    reader: str = "native published-abstract verifier; not a full-text reader"
    scope: Literal["ABSTRACT_ONLY"] = "ABSTRACT_ONLY"
