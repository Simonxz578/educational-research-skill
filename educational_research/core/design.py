"""Conditional empirical design and feasibility audit, with no fabricated access or data."""

from typing import Literal
from pydantic import Field
from ..models_base import Record


class Strand(Record):
    rq: str = ""
    purpose: str = ""
    outcome: str = ""
    estimand: str = ""
    measures: dict[str, str] = Field(default_factory=dict)
    sampling_frame: str = ""
    sampling_logic: str = ""
    data_sources: list[str] = Field(default_factory=list)
    analysis: str = ""
    sample_rationale: str = ""
    missingness_bias: str = ""
    reflexivity: str = ""
    negative_cases: str = ""
    audit_trail: str = ""


class Integration(Record):
    rq: str = ""
    design: str = ""
    timing: str = ""
    connection: str = ""
    joint_display: str = ""
    discordance: str = ""
    meta_inference: str = ""
    weighting: str = ""


class StudyDesign(Record):
    non_users_access: Literal[
        "not_confirmed", "requested", "confirmed", "unavailable", "not_applicable"
    ] = "not_confirmed"
    outcome_timing: str = ""
    participant_eligibility: str = ""
    kind: Literal["mixed_methods", "qualitative", "quantitative", "conceptual"]
    purpose: str
    quan: Strand | None = None
    qual: Strand | None = None
    integration: Integration | None = None
    construct_ids: list[str] = Field(default_factory=list)
    ethics_consent: str = ""
    access_status: Literal["not_confirmed", "requested", "confirmed", "not_applicable"] = "not_confirmed"
    access_evidence: str = ""
    storage: str = ""
    recruitment: str = ""
    non_user_comparison: str = ""
    requires_non_users: bool = False
    go_conditions: list[str] = Field(default_factory=list)
    no_go_conditions: list[str] = Field(default_factory=list)
    fallback: str = ""


def audit_design(design, required=False, construct_ids=(), require_v042=False):
    if design is None:
        return {
            "status": "FAIL" if required else "NOT_APPLICABLE",
            "issues": ["Empirical proposal requires a method-fit/feasibility record"]
            if required
            else [],
        }
    issues = []

    def require(record, names, label):
        if record is None:
            issues.append(f"{label}: missing strand/integration")
        else:
            for field in names:
                if not getattr(record, field):
                    issues.append(f"{label}: missing {field}")

    if design.kind in {"quantitative", "mixed_methods"}:
        require(
            design.quan,
            [
                "rq",
                "purpose",
                "estimand",
                "outcome",
                "measures",
                "sampling_frame",
                "sampling_logic",
                "data_sources",
                "analysis",
                "sample_rationale",
                "missingness_bias",
            ],
            "QUAN",
        )
    if design.kind in {"qualitative", "mixed_methods"}:
        require(
            design.qual,
            [
                "rq",
                "purpose",
                "sampling_logic",
                "data_sources",
                "analysis",
                "reflexivity",
                "negative_cases",
                "audit_trail",
            ],
            "QUAL",
        )
    if design.kind == "mixed_methods":
        require(
            design.integration,
            [
                "rq",
                "design",
                "timing",
                "connection",
                "joint_display",
                "discordance",
                "meta_inference",
                "weighting",
            ],
            "INTEGRATION",
        )
        if design.quan and design.qual and design.quan.rq.strip() == design.qual.rq.strip():
            issues.append("Independent QUAN/QUAL purposes are not specified")
    if design.kind != "conceptual":
        if require_v042:
            for field in ["outcome_timing", "participant_eligibility"]:
                if not getattr(design, field):
                    issues.append(
                        f"FEASIBILITY: missing {field}; intentions and observed behaviour must remain distinct"
                    )
            if design.kind in {"quantitative", "mixed_methods"} and design.access_status != "confirmed":
                issues.append(
                    "QUAN access/numbers are not established; keep the sequence conditional and activate the feasible fallback"
                )
            if design.requires_non_users and design.non_users_access != "confirmed":
                issues.append(
                    "Required non-user access is not confirmed; an eligible comparison cannot be assumed"
                )
        for field in [
            "ethics_consent",
            "storage",
            "recruitment",
            "go_conditions",
            "no_go_conditions",
            "fallback",
        ]:
            if not getattr(design, field):
                issues.append(f"FEASIBILITY: missing {field}")
        if design.requires_non_users and not design.non_user_comparison:
            issues.append("Recruitment omits required non-user comparison")
        if design.requires_non_users and design.non_users_access == "unavailable":
            issues.append(
                "Required non-users cannot be recruited; revise the question/design and activate the stated fallback"
            )
        if design.access_status == "confirmed" and not design.access_evidence:
            issues.append("Institutional/data access claimed without evidence")
        if not design.construct_ids or not set(design.construct_ids) <= set(construct_ids):
            issues.append("Design measures/coding do not resolve to framework constructs")
    return {
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
        "access_status": design.access_status,
        "fallback": design.fallback,
        "interpretation": "Proposed design, not completed research or guaranteed feasibility",
    }
