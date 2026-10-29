"""Conservative deduplication and relevance-first screening."""

import re
from difflib import SequenceMatcher
from ..search.crossref import doi, clean_title


def tokens(value):
    return {
        w
        for w in re.findall(r"\w+", value.casefold())
        if len(w) > 2 and w not in {"the", "and", "for", "with"}
    }


def relevance(source, topic):
    target = tokens(topic)
    observed = tokens(source.title + " " + source.abstract + " " + " ".join(source.descriptors))
    return 100 * len(target & observed) / max(1, len(target))


def deduplicate(sources):
    unique, excluded = [], []
    for source in sources:
        match = None
        for prior in unique:
            d1, d2 = doi(source.doi), doi(prior.doi)
            if d1 and d2:
                same = d1 == d2
                if (
                    same
                    and SequenceMatcher(
                        None, clean_title(source.title), clean_title(prior.title)
                    ).ratio()
                    < 0.94
                ):
                    source.identity = prior.identity = "CONFLICT"
                    source.warnings.append(
                        "Same DOI assigned to conflicting titles; manual identity review required"
                    )
                    prior.warnings.append(
                        "Same DOI assigned to conflicting titles; manual identity review required"
                    )
                    same = False
            elif source.eric_id and prior.eric_id and source.eric_id == prior.eric_id:
                same = True
            else:
                same = (
                    source.year == prior.year
                    and bool(source.authors)
                    and bool(prior.authors)
                    and source.authors[0] == prior.authors[0]
                    and source.type == prior.type
                    and SequenceMatcher(
                        None, clean_title(source.title), clean_title(prior.title)
                    ).ratio()
                    > 0.98
                )
            if same:
                match = prior
                break
        if match:
            excluded.append({"id": source.id, "reason": "duplicate work", "duplicate_of": match.id})
            match.provenance += source.provenance
            match.providers = sorted(set(match.providers + source.providers))
        else:
            unique.append(source)
    return unique, excluded


def screen(sources, topic, threshold=25):
    included, excluded = [], []
    for source in sources:
        reason = None
        if relevance(source, topic) < threshold and source.assessments.get("relevance", None) is None:
            reason = "Low lexical relevance; manual scope review may restore this source"
        elif source.identity == "CONFLICT":
            reason = "Unresolved metadata conflict"
        elif "retract" in source.publication_status.lower():
            reason = "Retraction requires contextual use, not unqualified support"
        if reason:
            excluded.append({"id": source.id, "reason": reason})
        else:
            included.append(source)
    return included, excluded
