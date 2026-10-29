"""Real APA CSL processor; no hand-built substitute bibliography."""

from citeproc import CitationStylesStyle, CitationStylesBibliography, Citation, CitationItem, formatter
from citeproc.source.json import CiteProcJSON
from citeproc_styles import get_style_filepath


def csl(source):
    record = {
        "id": source.id,
        "type": source.type,
        "title": source.title,
        "author": [a.model_dump(exclude_defaults=True) for a in source.authors],
        "container-title": source.journal,
        "publisher": source.publisher,
        "volume": source.volume,
        "issue": source.issue,
        "page": source.pages,
        "URL": source.url,
    }
    if source.year:
        record["issued"] = {"date-parts": [[source.year]]}
    if source.doi:
        record["DOI"] = source.doi
    return {k: v for k, v in record.items() if v}


def bibliography(sources):
    if not sources:
        return []
    # Official CSL APA style has et-al-min=21/use-first=19/use-last for 21+ authors.
    style = CitationStylesStyle(get_style_filepath("apa"), validate=False)
    bib = CitationStylesBibliography(style, CiteProcJSON([csl(s) for s in sources]), formatter.html)
    for s in sources:
        bib.register(Citation([CitationItem(s.id)]))
    bib.sort()
    output = bib.bibliography()
    identities = {s.id.casefold(): s.id for s in sources}
    return [
        (identities[item.key.casefold()], str(rendered)) for item, rendered in zip(bib.items, output)
    ]


def in_text(source):
    if not source.authors:
        name = source.title[:35]
    elif len(source.authors) == 1:
        name = source.authors[0].literal or source.authors[0].family
    elif len(source.authors) == 2:
        name = " & ".join(a.literal or a.family for a in source.authors)
    else:
        name = (source.authors[0].literal or source.authors[0].family) + " et al."
    return f"({name}, {source.year or 'n.d.'})"
