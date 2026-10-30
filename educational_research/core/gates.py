"""Five non-bypassable acceptance gates; layout success is a separate property."""

import re
from typing import Literal
from pydantic import Field, model_validator
from ..models_base import Record
from ..config import today
from .reading import reading_audit, evidence_registry
from .discovery import discovery_status
from .framework import audit_framework
from .design import audit_design
from .novelty import challenge
from .quality import warnings


class GateResult(Record):
    status: Literal["PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_APPLICABLE"]
    reason: str
    counts: dict = Field(default_factory=dict)
    required_evidence_ids: list[str] = Field(default_factory=list)
    checked_at: str
    commands_executed: list[dict] = Field(default_factory=list)
    applicable: bool


class QualityGates(Record):
    schema_version: Literal["2.0"] = "2.0"
    overall_status: Literal["PASS", "PARTIAL", "FAIL", "BLOCKED"]
    label: str
    gates: dict[str, GateResult]
    framework_audit: dict
    design_audit: dict
    novelty_audit: dict
    reading_audit: list[dict]
    synthetic: bool
    structural_all_pass: bool
    scientific_notice: str

    @model_validator(mode="after")
    def no_false_completion(self):
        if set(self.gates) != {"G1", "G2", "G3", "G4", "G5"}:
            raise ValueError("All five research gates are required")
        if any(g.applicable != (g.status != "NOT_APPLICABLE") for g in self.gates.values()):
            raise ValueError("Applicable gates cannot be hidden as not applicable")
        if self.overall_status == "PASS" and (
            self.synthetic or any(g.applicable and g.status != "PASS" for g in self.gates.values())
        ):
            raise ValueError("Overall PASS cannot override incomplete gates or synthetic evidence")
        return self


def independent_key(s):
    # Versions of one work and duplicated artifacts cannot count as independent support.
    if s.work_id:
        return s.work_id.casefold()
    if s.doi:
        return s.doi.casefold()
    if s.reading:
        return s.reading.document.sha256
    return (
        re.sub(r"\W", "", s.title.casefold())
        + str(s.year)
        + "|".join(a.family or a.literal for a in s.authors)
    )


def evaluate_gates(config, sources, synthesis, logs, observations, delivery=None, graph_errors=()):
    evidence = evidence_registry(sources)
    readings = reading_audit(
        sources,
        reader_ready=config.presentation == "roadmap" or config.strict_quality_gates,
        synthesis=synthesis,
    )
    qualified = {r["source_id"] for r in readings if r["qualified"]}
    source_map = {s.id: s for s in sources}
    distinct = {independent_key(source_map[s]) for s in qualified}
    discovery = discovery_status(logs, observations)
    framework = audit_framework(
        synthesis.framework,
        sources,
        synthesis.claims,
        config.topic,
        config.rq or "",
        synthesis.study_design,
    )
    design = audit_design(
        synthesis.study_design,
        config.empirical_proposal,
        [c.id for c in synthesis.framework.constructs] if synthesis.framework else [],
        require_v042=config.presentation == "roadmap" or config.strict_quality_gates,
    )
    novelty = challenge(synthesis.novelty, sources, discovery["status"] == "PASS")
    # Unknown evidence cannot turn into a confident novelty verdict.
    if (
        synthesis.novelty
        and any(c.source_id not in qualified for c in synthesis.novelty.comparisons)
        and novelty["status"] == "PASS"
    ):
        novelty.update(verdict="INSUFFICIENT_EVIDENCE", status="FAIL")
        novelty["issues"].append(
            "Closest-work challenge includes sources without qualified full-text reading"
        )
    argument_issues = list(graph_errors)
    from .graph import validate_graph

    try:
        validate_graph(synthesis, sources)
    except ValueError as exc:
        argument_issues.append(str(exc))
    if not 3 <= len(synthesis.claims) <= (5 if config.presentation == "roadmap" else 7):
        argument_issues.append(
            "A substantive reader argument spine requires 3–5 warranted major claims"
            if config.presentation == "roadmap"
            else "A substantive argument spine requires 3–7 warranted major claims"
        )
    for c in synthesis.claims:
        from .reading import reader_scope

        if (
            any(reader_scope(s) == "ABSTRACT_ONLY" for s in sources if s.id in c.source_ids)
            and c.evidence_scope != "PRELIMINARY_ABSTRACT"
        ):
            argument_issues.append(
                f"{c.id}: abstract sources cannot support an unqualified full-text claim"
            )
        if re.search(r"\b(proves?|causes?|causal impact)\b", c.text + " " + c.own_inference, re.I):
            kinds = [
                e.finding_kind
                for s in sources
                if s.id in c.source_ids and s.reading
                for e in s.reading.evidence
                if e.evidence_id in c.evidence_ids
            ]
            if kinds and not any(k == "tested" for k in kinds):
                argument_issues.append(
                    f"{c.id}: causal wording is unsupported by tested/identified evidence"
                )
        valid = [source_map[i] for i in c.source_ids if i in qualified]
        if len({independent_key(s) for s in valid}) < 2:
            argument_issues.append(f"{c.id}: fewer than two independent qualified full texts")
        if not set(c.opposing_evidence_ids) <= evidence.keys():
            argument_issues.append(f"{c.id}: unresolved opposing evidence")
        if not c.evidence_ids or not set(c.evidence_ids) <= evidence.keys():
            argument_issues.append(f"{c.id}: unresolved evidence")
        if any(i.split(":", 1)[0] not in c.source_ids for i in c.evidence_ids):
            argument_issues.append(f"{c.id}: evidence attributed to another work")
        if any(not any(i.startswith(s.id + ":") for i in c.evidence_ids) for s in valid):
            argument_issues.append(f"{c.id}: supporting author named without a passage")
        if not set(c.source_ids) <= c.author_positions.keys():
            argument_issues.append(f"{c.id}: source-author positions not attributed")
        required = [
            "comparison",
            "warrant",
            "warrant_id",
            "objection",
            "objection_id",
            "qualification",
            "own_inference",
            "scope",
            "section",
            "paragraph_plan",
            "transition_warrant",
            "relative_strength",
            "theory_ids",
            "rq_ids",
        ]
        if any(not getattr(c, k) for k in required):
            argument_issues.append(
                f"{c.id}: incomplete comparison/warrant/rival/inference/paragraph alignment"
            )
        if synthesis.framework and (
            not set(c.theory_ids) <= {lens.id for lens in synthesis.framework.candidates}
            or not set(c.rq_ids) <= synthesis.framework.rq_definitions.keys()
        ):
            argument_issues.append(f"{c.id}: unresolved theory/RQ links")
    for s in sources:
        if any("OVERCLAIM" in w for w in warnings(s)):
            argument_issues.append(f"{s.id}: inference exceeds source evidence")
        if s.reading:
            for rival in s.reading.opposing_source_ids:
                preserved = rival in source_map and (
                    any(
                        e.kind
                        in {
                            "contradicts",
                            "qualifies",
                            "method_incompatible",
                            "different_context",
                            "same_construct_different_measure",
                        }
                        and {s.id, rival} <= {e.source, e.target}
                        and e.evidence_ids
                        for e in synthesis.edges
                    )
                    or any(
                        any(i.startswith(rival + ":") for i in c.opposing_evidence_ids)
                        for c in synthesis.claims
                    )
                )
                if not preserved:
                    argument_issues.append(f"{s.id}: opposing evidence {rival} silently omitted")
    for edge in synthesis.edges:
        if edge.kind != "depends_on" and (
            not edge.evidence_ids or not set(edge.evidence_ids) <= evidence.keys()
        ):
            argument_issues.append("Graph relationship lacks resolvable evidence")
    required_count = config.deep_review_requirement
    reduced = config.min_reviewed_fulltexts < 10
    substantive = config.substantive

    def gate(status, reason, counts=None, ids=None):
        return {
            "status": status,
            "reason": reason,
            "counts": counts or {},
            "required_evidence_ids": ids or [],
            "checked_at": today(),
            "commands_executed": [],
        }

    gates = {
        "G1": gate(
            discovery["status"],
            "; ".join(discovery["issues"]) or "ERIC executions and dated Scholar observations preserved",
            {"eric": discovery["eric_executions"], "scholar": discovery["scholar_observations"]},
        ),
        "G2": gate(
            "PASS" if len(distinct) >= required_count and not reduced else "FAIL",
            "Deep-reading structural eligibility, not comprehension certification"
            if len(distinct) >= required_count and not reduced
            else "Insufficient independent, highly relevant full-text reading; reduced coverage cannot earn strict acceptance",
            {
                "qualified": len(distinct),
                "required": required_count,
                "reduced_coverage": reduced,
                "selection_target_N": config.quota,
                "shortfall": max(0, required_count - len(distinct)),
            },
            [e.evidence_id for s in sources if s.id in qualified for e in s.reading.evidence],
        ),
        "G3": gate(
            "FAIL" if argument_issues else "PASS",
            "; ".join(sorted(set(argument_issues)))
            or "Comparative source claims, evidence, warrants, objections and own inference are structurally linked",
            {"claims": len(synthesis.claims)},
            [i for c in synthesis.claims for i in c.evidence_ids],
        ),
        "G4": gate(
            novelty["status"],
            novelty["verdict"] + "; " + "; ".join(novelty["issues"]),
            {"closest_studies": len(novelty["comparisons"])},
        ),
        "G5": gate(
            "PASS"
            if delivery and not delivery.get("errors") and delivery.get("native_cli", True)
            else "PARTIAL"
            if delivery is None
            else "FAIL",
            "Native CLI, complete matrix, consistency, PDF and receipt checks"
            if delivery and not delivery.get("errors") and delivery.get("native_cli", True)
            else "Native CLI execution required; Python API rendering remains provisional"
            if delivery and not delivery.get("native_cli", True)
            else "; ".join(delivery.get("errors", []))
            if delivery
            else "Native deliverable validation pending",
        ),
    }
    if framework["status"] != "PASS" or design["status"] == "FAIL":
        gates["G3"]["status"] = "FAIL"
        gates["G3"]["reason"] += "; framework/method-fit incomplete"
    if not substantive:
        for key in ["G2", "G3", "G4"]:
            gates[key]["status"] = "NOT_APPLICABLE"
            gates[key]["reason"] = "Exploratory mode: substantive completion not claimed"
    for g in gates.values():
        g["applicable"] = g["status"] != "NOT_APPLICABLE"
    all_pass = all(g["status"] in {"PASS", "NOT_APPLICABLE"} for g in gates.values())
    synthetic = any(s.synthetic or "TEST ONLY" in s.title.upper() for s in sources) or any(
        o.synthetic for o in observations
    )
    if any(o.synthetic for o in observations):
        gates["G1"]["reason"] = (
            "TEST ONLY structural observation fixtures; no actual ERIC or Scholar search is asserted by these fixtures"
        )
    if any(s.synthetic or "TEST ONLY" in s.title.upper() for s in sources):
        gates["G2"]["reason"] += "; TEST ONLY corpus is not scholarly evidence"
    overall = "PASS" if all_pass and not synthetic and substantive else "PARTIAL"
    return {
        "schema_version": "2.0",
        "overall_status": overall,
        "label": "STRUCTURALLY_COMPLETE_FOR_EXPERT_REVIEW"
        if overall == "PASS"
        else "PROVISIONAL - NOT FULLY VERIFIED",
        "gates": gates,
        "framework_audit": framework,
        "design_audit": design,
        "novelty_audit": novelty,
        "reading_audit": readings,
        "synthetic": synthetic,
        "structural_all_pass": all_pass,
        "scientific_notice": "Structural eligibility does not certify comprehension, source authenticity, originality or journal acceptance",
    }
