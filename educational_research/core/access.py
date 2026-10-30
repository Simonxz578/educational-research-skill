"""Acquisition is a machine observation, never a record of critical reading."""

from typing import Literal
from pydantic import Field
from ..models_base import Record

AccessStatus = Literal[
    "OA_FULL_TEXT_VERIFIED",
    "REPOSITORY_FULL_TEXT_VERIFIED",
    "USER_SUPPLIED_LAWFUL_TEXT",
    "ABSTRACT_ONLY",
    "PAYWALL_OR_LOGIN_BLOCKED",
    "FULL_TEXT_RETRIEVED_NOT_VALIDATED",
    "FULL_TEXT_UNAVAILABLE",
    "RIGHTS_OR_VERSION_UNCLEAR",
]


class FullTextLocation(Record):
    url: str
    route: Literal["publisher", "eric", "repository", "core", "manual", "user"]
    version: Literal["publishedVersion", "acceptedVersion", "submittedVersion", "unknown"] = "unknown"
    licence_url: str = ""
    licence_evidence_url: str = ""
    legal_basis: str = ""
    processing_permission: Literal["allowed", "local_only", "unclear", "forbidden"] = "unclear"
    permission_evidence: str = ""
    local_path: str | None = None
    terms_checked: bool = False


class AccessAttempt(Record):
    route: str
    url: str
    checked_at: str
    status: AccessStatus
    http_status: int | None = None
    reason: str
    retry_after_seconds: float | None = None


class FullTextAcquisition(Record):
    schema_version: str = "4.2"
    source_id: str
    status: AccessStatus = "FULL_TEXT_UNAVAILABLE"
    checked_at: str
    location: FullTextLocation | None = None
    artifact_path: str | None = None
    sha256: str | None = None
    extracted_text_path: str | None = None
    extracted_text_sha256: str | None = None
    media_type: str = ""
    page_count: int | None = None
    structure: list[str] = Field(default_factory=list)
    paragraphs: list[dict[str, str]] = Field(default_factory=list)
    attempts: list[AccessAttempt] = Field(default_factory=list)
    metadata_identity: str = "UNVERIFIED"
    retrieval_complete: bool = False
    content_validated: bool = False
    legal_usage_verified: bool = False
    close_reading_completed: bool = False
    version_difference: str = ""
    notice: str = "Machine checks do not establish comprehension, interpretive accuracy or public-reproduction rights."
