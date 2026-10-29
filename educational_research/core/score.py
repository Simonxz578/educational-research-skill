"""Explainable 45/20/15/10/10 weighting, with disclosed missingness."""

from .screen import relevance
from ..config import today

WEIGHTS = {
    "relevance": 45,
    "study_quality": 20,
    "journal_influence": 15,
    "article_impact": 10,
    "argument_value": 10,
}


def score(source, topic):
    components, reasons = {}, {}
    for key, weight in WEIGHTS.items():
        assessment = source.assessments.get(key)
        if assessment:
            # Journal/article scores must not be supplied without supporting metrics.
            valid = not (
                key == "journal_influence"
                and not any(m.name in {"JIF", "SJR", "CiteScore", "h5-index"} for m in source.metrics)
            )
            valid &= not (
                key == "article_impact"
                and not any(m.name in {"article_citations", "FWCI"} for m in source.metrics)
            )
            if valid:
                components[key + "_score"] = round(weight * assessment.value / 100, 2)
                reasons[key] = assessment.model_dump()
                continue
        if key == "relevance":
            components[key + "_score"] = round(weight * relevance(source, topic) / 100, 2)
            reasons[key] = {
                "rationale": "Lexical coverage only; provisional until contextual review",
                "checked_at": today(),
            }
        else:
            components[key + "_score"] = None
    available = sum(w for k, w in WEIGHTS.items() if components[k + "_score"] is not None)
    total = round(100 * sum(v or 0 for v in components.values()) / available, 2) if available else None
    return {
        **components,
        "total_priority_score": total,
        "available_weight": available,
        "metric_missingness": [k for k in WEIGHTS if components[k + "_score"] is None],
        "score_rationales": reasons,
        "priority_status": "PROVISIONAL" if available < 100 else "ASSESSED",
        "why_included": source.relevance_explanation + "; " + source.role,
    }


def rank(sources, topic):
    # Low relevance cannot be rescued by journal prestige.
    return sorted(
        sources,
        key=lambda s: (
            score(s, topic)["relevance_score"] >= 22.5,
            score(s, topic)["total_priority_score"] or 0,
        ),
        reverse=True,
    )


def select_diverse(sources, limit):
    """Reserve one place for each critical/foundation role before filling ranked slots."""
    protected = {
        "counterargument",
        "counterexample",
        "contradiction",
        "foundation",
        "method",
        "null evidence",
    }
    selected, seen = [], set()
    for source in sources:
        if source.role in protected and source.role not in seen:
            selected.append(source)
            seen.add(source.role)
            if len(selected) == limit:
                return selected
    selected += [s for s in sources if s not in selected][: max(0, limit - len(selected))]
    return [s for s in sources if s in selected]
