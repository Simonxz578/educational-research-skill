"""Deterministic checks supplement, never replace, critical reading."""

import re

CAPS = {"summary": 55, "source_argument": 40, "target_argument": 40, "relevance_explanation": 30}


def warnings(source):
    result = list(source.warnings)
    if source.access not in {"FULL_TEXT_VERIFIED", "USER_SUPPLIED"}:
        result.append("ABSTRACT/METADATA EVIDENCE ONLY: full-text claims not verified")
    if source.identity not in {"VERIFIED", "SYNTHETIC"}:
        result.append("Unresolved citation identity: retained as candidate, not verified bibliography")
    if source.evidence_kind in {"self-report", "retrospective", "correlation"} and re.search(
        r"\b(causes?|proves?|improves?|effective|demonstrates?)\b", source.target_argument, re.I
    ):
        result.append(
            "OVERCLAIM: reported perceptions/correlation cannot establish observed causal outcomes"
        )
    if source.publication_status == "not checked":
        result.append("Publication corrections/retractions not checked")
    return sorted(set(result))


def validate_compact(sources):
    errors = []
    for s in sources:
        for field, limit in CAPS.items():
            if len(getattr(s, field).split()) > limit:
                errors.append(f"{s.id}: {field} exceeds compact limit {limit}; revise before rendering")
    return errors


def audit_draft(text, sources):
    """A line-addressed review map; never silently rewrites author prose."""
    issues = []
    for line, paragraph in enumerate(text.splitlines(), 1):
        if not paragraph.strip():
            continue
        ids = re.findall(r"\b(?:S\d+|EJ\d+|ED\d+)\b", paragraph)
        known = {s.id for s in sources}
        if any(i not in known for i in ids):
            issues.append({"line": line, "kind": "unresolved_source_id", "ids": ids})
        if re.search(r"\b(proves?|causes?|always|no studies|first ever|unexplored)\b", paragraph, re.I):
            issues.append(
                {
                    "line": line,
                    "kind": "overstatement_review",
                    "action": "Qualify against cited evidence and search boundary",
                }
            )
        if (
            len(paragraph.split()) > 20
            and not ids
            and not re.search(r"\(.*?\d{4}[a-z]?.*?\)", paragraph)
        ):
            issues.append(
                {
                    "line": line,
                    "kind": "unsupported_claim_review",
                    "action": "Attach source/evidence IDs or mark author reasoning",
                }
            )
    return issues
