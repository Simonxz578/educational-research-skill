"""A failed search never establishes novelty."""


def evaluate(gaps, sources, logs):
    known = {s.id for s in sources}
    results = []
    coverage = any(e.get("status") == "ERIC_SEARCHED" for e in logs)
    for gap in gaps:
        required = (
            "search_boundary",
            "closest_source_ids",
            "missing_dimension",
            "evidence",
            "method_fit",
            "novelty_boundary",
        )
        valid = all(gap.get(k) for k in required)
        valid &= set(gap.get("closest_source_ids", [])) <= known
        valid &= len(gap.get("closest_source_ids", [])) >= 3
        prohibited = any(w in str(gap).lower() for w in ("first ever", "no studies exist", "unexplored"))
        result = {
            **gap,
            "confidence": "provisionally supported"
            if valid and coverage and not prohibited
            else "speculative",
            "qualification": "Bounded comparison, not an originality guarantee; human review required",
        }
        if prohibited:
            result["rejected_overclaim"] = True
            result["original_assertion"] = dict(gap)
            result["missing_dimension"] = "Gap assertion rejected: exceeds documented search boundary"
            result["evidence"] = "Compare closest work before making any novelty claim"
            result["novelty_boundary"] = "No originality claim warranted"
        results.append(result)
    return results or [
        {
            "confidence": "speculative",
            "missing_dimension": "Not established",
            "evidence": "Insufficient closest-work comparison; search absence is not evidence of a gap",
            "closest_source_ids": [s.id for s in sources[:10]],
            "method_fit": "Proposed design must address the scoped question",
            "novelty_boundary": "No novelty claim warranted",
        }
    ]
