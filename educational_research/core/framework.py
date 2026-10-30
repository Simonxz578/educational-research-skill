"""Literature-led conceptual framework: explicit lenses, constructs, mechanisms and drift."""

import re
from typing import Literal
from pydantic import Field
from ..models_base import Record
from .reading import evidence_registry


class Lens(Record):
    id: str
    name: str
    source_ids: list[str]
    evidence_ids: list[str]
    explanatory_power: str
    epistemology: str
    scope_conditions: str
    method_fit: str
    operationalisation: str
    selected: bool = False
    selection_reason: str
    used_in: list[Literal["sampling", "measurement", "analysis", "interpretation"]] = Field(
        default_factory=list
    )


class Construct(Record):
    id: str
    name: str
    definition: str
    source_ids: list[str]
    evidence_ids: list[str]
    boundaries: str
    distinct_from: list[str] = Field(default_factory=list)
    rq_ids: list[str]
    claim_ids: list[str]
    operationalisation: str
    analysis_use: str
    expected_pattern: str
    disconfirming_pattern: str
    lens_ids: list[str]


class Relationship(Record):
    id: str
    source: str
    target: str
    mechanism: str
    status: Literal["source_verified", "hypothesised", "sensitising"]
    relation_type: Literal[
        "association",
        "proposed_mechanism",
        "moderation",
        "mediation",
        "feedback",
        "interpretative",
        "causal",
    ]
    evidence_ids: list[str] = Field(default_factory=list)
    conditions: str
    rival_mechanism: str
    negative_case: str
    causal_identification: str | None = None


class ConstructUse(Record):
    location: str
    stage: Literal[
        "title",
        "purpose",
        "rq",
        "theory",
        "measure",
        "coding",
        "analysis",
        "claim",
        "policy",
        "problem",
        "source_claim",
        "gap",
        "interpretation",
        "contribution",
    ]
    construct_id: str
    label: str
    justified_bridge: str = ""
    bridge_evidence_ids: list[str] = Field(default_factory=list)


class Framework(Record):
    schema_version: str = "2.0"
    phenomenon: str
    outcomes: list[str]
    rq_definitions: dict[str, str]
    candidates: list[Lens] = Field(default_factory=list)
    constructs: list[Construct] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    uses: list[ConstructUse] = Field(default_factory=list)
    combination_justification: str = ""
    no_single_theory_rationale: str = ""
    theory_failure: str
    modest_contribution: str
    scope_limits: str
    revision_triggers: list[str]


def _same_label(a, b):
    return re.sub(r"[^\w]", "", a.casefold()) == re.sub(r"[^\w]", "", b.casefold())


def audit_framework(framework, sources, claims, topic="", rq="", design=None):
    issues, drift = [], []
    if framework is None:
        return {
            "status": "FAIL",
            "issues": ["No literature-led framework supplied"],
            "drift": [],
            "alignment": [],
        }
    f = framework
    registry, source_ids = evidence_registry(sources), {s.id for s in sources}
    claim_ids, rqs = {c.id for c in claims}, set(f.rq_definitions)
    constructs, lenses = {c.id: c for c in f.constructs}, {lens.id: lens for lens in f.candidates}
    selected = [lens for lens in f.candidates if lens.selected]
    if len(constructs) != len(f.constructs) or len(lenses) != len(f.candidates):
        issues.append("Duplicate framework IDs")
    if not f.constructs or not f.relationships or not f.revision_triggers:
        issues.append("Framework lacks constructs, relationships or disconfirming revision triggers")
    if len(f.candidates) < 2 and not f.no_single_theory_rationale:
        issues.append("Compare plausible candidate lenses or justify conceptual synthesis")
    if not selected and not f.no_single_theory_rationale:
        issues.append("No primary lens or justified no-single-theory synthesis")
    if len(selected) > 1 and not f.combination_justification:
        issues.append("Unjustified theoretical stacking")
    for item in list(f.candidates) + list(f.constructs):
        if not set(item.source_ids) <= source_ids or not item.source_ids:
            issues.append(f"{item.id}: unresolved theoretical source")
        if not item.evidence_ids or not set(item.evidence_ids) <= registry.keys():
            issues.append(f"{item.id}: unresolved framework evidence")
        elif any(registry[e]["source_id"] not in item.source_ids for e in item.evidence_ids):
            issues.append(f"{item.id}: evidence not attributable to named sources")
    for lens in selected:
        linked = [c for c in f.constructs if lens.id in c.lens_ids]
        if (
            not lens.used_in
            or not linked
            or not all(c.operationalisation and c.analysis_use for c in linked)
        ):
            issues.append(
                f"{lens.id}: decorative lens; unused in sampling/measurement/analysis/interpretation"
            )
    alignment = []
    for c in f.constructs:
        if (
            not set(c.rq_ids) <= rqs
            or not c.rq_ids
            or not set(c.claim_ids) <= claim_ids
            or not c.claim_ids
        ):
            issues.append(f"{c.id}: missing or unresolved RQ/claim alignment")
        if not set(c.lens_ids) <= lenses.keys():
            issues.append(f"{c.id}: unknown theoretical lens")
        if not all(
            [
                c.definition,
                c.boundaries,
                c.operationalisation,
                c.analysis_use,
                c.expected_pattern,
                c.disconfirming_pattern,
            ]
        ):
            issues.append(f"{c.id}: unmeasurable or incompletely bounded construct")
        if _same_label(c.definition, c.name):
            issues.append(f"{c.id}: circular construct definition")
        alignment.append(
            {
                "construct_id": c.id,
                "name": c.name,
                "lens_ids": c.lens_ids,
                "rq_ids": c.rq_ids,
                "claim_ids": c.claim_ids,
                "evidence_ids": c.evidence_ids,
                "operationalisation": c.operationalisation,
                "analysis": c.analysis_use,
                "expected_pattern": c.expected_pattern,
                "disconfirming_pattern": c.disconfirming_pattern,
            }
        )
    for relation in f.relationships:
        if relation.source not in constructs or relation.target not in constructs:
            issues.append(f"{relation.id}: unknown construct endpoint")
        if not set(relation.evidence_ids) <= registry.keys() or (
            relation.status == "source_verified" and not relation.evidence_ids
        ):
            issues.append(f"{relation.id}: source-verified link without resolvable evidence")
        if relation.relation_type == "causal" and not relation.causal_identification:
            issues.append(f"{relation.id}: causal link without an identification argument")
    for use in f.uses:
        c = constructs.get(use.construct_id)
        if c is None:
            issues.append(f"{use.location}: unknown construct")
        elif not _same_label(use.label, c.name) and not (
            use.justified_bridge
            and use.bridge_evidence_ids
            and set(use.bridge_evidence_ids) <= registry.keys()
        ):
            drift.append(
                {
                    "location": use.location,
                    "stage": use.stage,
                    "construct": c.id,
                    "expected": c.name,
                    "observed": use.label,
                    "kind": "UNJUSTIFIED_CONSTRUCT_SUBSTITUTION",
                }
            )
    # Audit actual title/RQ labels, not solely self-reported framework-use metadata.
    for location, value in [("title", topic), ("rq", rq)]:
        for c in f.constructs:
            for near in c.distinct_from:
                if near.casefold() in value.casefold() and c.name.casefold() not in value.casefold():
                    bridges = [
                        u
                        for u in f.uses
                        if u.stage == location
                        and u.construct_id == c.id
                        and u.justified_bridge
                        and u.bridge_evidence_ids
                    ]
                    if not bridges:
                        drift.append(
                            {
                                "location": location,
                                "expected": near,
                                "observed": c.name,
                                "kind": "TITLE_RQ_MEASURE_DRIFT",
                            }
                        )
    for outcome in f.outcomes:
        if not any(_same_label(outcome, c.name) for c in f.constructs):
            justified = any(
                _same_label(u.label, outcome)
                and u.justified_bridge
                and u.bridge_evidence_ids
                and set(u.bridge_evidence_ids) <= registry.keys()
                for u in f.uses
            )
            if not justified:
                drift.append(
                    {
                        "location": "framework.outcomes",
                        "expected": outcome,
                        "observed": list(c.name for c in f.constructs),
                        "kind": "OUTCOME_CONSTRUCT_NOT_OPERATIONALISED",
                    }
                )
    # General boundaries are supplied by the framework, not a topic-specific preset.
    for c in f.constructs:
        for other in f.constructs:
            if c.id != other.id and (other.name in c.distinct_from or c.name in other.distinct_from):
                if _same_label(c.operationalisation, other.operationalisation) and not any(
                    u.justified_bridge and u.bridge_evidence_ids
                    for u in f.uses
                    if u.construct_id in {c.id, other.id}
                ):
                    drift.append(
                        {
                            "location": "operationalisation",
                            "constructs": [c.id, other.id],
                            "kind": "DISTINCT_CONSTRUCTS_CONFLATED",
                        }
                    )
    if drift:
        issues.append("Construct drift/conflation requires explicit evidence-led repair")
    return {
        "status": "PASS" if not issues else "FAIL",
        "issues": sorted(set(issues)),
        "drift": drift,
        "alignment": alignment,
        "assessment": "STRUCTURAL; interpretation requires expert review",
    }


def mermaid(framework):
    if not framework:
        return 'flowchart LR\n  pending["Framework not established"]\n'
    # Remap arbitrary user IDs to safe Mermaid identifiers; escape content as JSON strings.
    import json

    ids = {c.id: f"N{i}" for i, c in enumerate(framework.constructs)}
    rows = ["flowchart LR"]
    rows += [f"  {ids[c.id]}[{json.dumps(c.name, ensure_ascii=False)}]" for c in framework.constructs]
    for link in framework.relationships:
        if link.source in ids and link.target in ids:
            arrow = "-->" if link.status == "source_verified" else "-.->"
            rows.append(
                f"  {ids[link.source]} {arrow}|{json.dumps(link.id + ': ' + link.status)}| {ids[link.target]}"
            )
    return "\n".join(rows) + "\n"
