"""Bidirectional ID and author-year audit with unresolved items disclosed."""

import re


def audit(text, sources):
    ids = {s.id for s in sources}
    cited_ids = set(re.findall(r"\b(?:S\d+|EJ\d+|ED\d+)\b", text))
    recognised = set(cited_ids & ids)
    unresolved = list(sorted(cited_ids - ids))
    # Parenthetical APA citations; narrative and complex multilingual names need human review.
    for parenthesis in re.findall(r"\(([^()]*(?:19|20)\d{2}[a-z]?[^()]*)\)", text):
        for citation in parenthesis.split(";"):
            years = re.findall(r"\b((?:19|20)\d{2})[a-z]?\b", citation)
            matches = [
                s
                for s in sources
                if str(s.year) in years
                and any((a.family or a.literal).casefold() in citation.casefold() for a in s.authors)
            ]
            if matches:
                recognised.update(s.id for s in matches)
            else:
                unresolved.append(citation.strip())
    return {
        "unresolved_citations": unresolved,
        "uncited_references": sorted(ids - recognised),
        "recognised_sources": sorted(recognised),
        "scope": "ID and parenthetical author-year checks; narrative citations require human review",
    }
