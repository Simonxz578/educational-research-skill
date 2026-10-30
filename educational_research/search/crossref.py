"""Identity comparison never silently overwrites conflicting bibliographic fields."""

import re
from difflib import SequenceMatcher
from urllib.parse import quote
from ..models import Author
from ..config import today


def doi(value):
    if not value:
        return None
    value = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).lower()
    return value if re.fullmatch(r"10\.\d{4,9}/\S+", value) else None


def clean_title(value):
    return re.sub(r"[^\w]", "", value.casefold())


def year(record, field):
    parts = record.get(field, {}).get("date-parts", [[]])[0]
    return parts[0] if parts else None


def verify(source, message):
    original = source.model_dump(
        include={
            "id",
            "title",
            "authors",
            "year",
            "doi",
            "url",
            "journal",
            "publisher",
            "volume",
            "issue",
            "pages",
        }
    )
    conflicts = {}
    title = (message.get("title") or [""])[0]
    received_doi = doi(message.get("DOI"))
    if source.doi and doi(source.doi) != received_doi:
        conflicts["doi"] = [source.doi, received_doi]
    if SequenceMatcher(None, clean_title(source.title), clean_title(title)).ratio() < 0.94:
        conflicts["title"] = [source.title, title]
    authors = [
        Author(family=a.get("family", ""), given=a.get("given", ""), literal=a.get("name", ""))
        for a in message.get("author", [])
        if a.get("family") or a.get("name")
    ]
    supplied = [a.family.casefold() or a.literal.casefold() for a in source.authors]
    found = [a.family.casefold() or a.literal.casefold() for a in authors]
    if supplied and found and supplied != found:
        conflicts["authors"] = [supplied, found]
    issue_year = year(message, "published-print") or year(message, "issued")
    online_year = year(message, "published-online")
    possible_years = {y for y in (issue_year, online_year) if y}
    if source.year and possible_years and source.year not in possible_years:
        conflicts["year"] = [source.year, sorted(possible_years)]
    source.provenance.append(
        {
            "provider": "Crossref",
            "url": f"https://api.crossref.org/works/{received_doi}",
            "checked_at": today(),
            "raw_metadata": message,
            "input_metadata": original,
            "conflicts": conflicts,
        }
    )
    source.online_year, source.issue_year = online_year, issue_year
    updates = message.get("update-to", [])
    source.publication_status = (
        "UPDATE_NOTICE_REQUIRES_REVIEW" if updates else "NO_UPDATE_IN_CROSSREF_METADATA"
    )
    if updates:
        source.warnings.append("Publisher/Crossmark update must be checked before using findings")
    if conflicts or not (title and authors and possible_years and received_doi):
        source.identity = "CONFLICT" if conflicts else "UNVERIFIED"
        return source
    # Preserve a supplied online year; flag year selection for a publisher/VoR check.
    if source.year and issue_year and source.year != issue_year:
        source.identity = "CONFLICT"
        source.warnings.append("Online-first/issue citation year requires publisher verification")
        return source
    source.title, source.authors, source.doi = title, authors, received_doi
    source.year = issue_year or online_year
    source.journal = (message.get("container-title") or [source.journal])[0]
    source.volume, source.issue = message.get("volume", ""), message.get("issue", "")
    source.pages = message.get("page", message.get("article-number", ""))
    source.publisher = message.get("publisher", "")
    source.type = {
        "journal-article": "article-journal",
        "book": "book",
        "dissertation": "thesis",
        "posted-content": "article",
    }.get(message.get("type"), "article")
    source.identity = "VERIFIED"
    source.providers = sorted(set(source.providers + ["Crossref"]))
    source.warnings.append(
        "Crossref identity matched; publisher/VoR and correction status require review"
    )
    return source


def enrich(client, source):
    if source.synthetic:
        return source
    if source.doi:
        message = client.get("https://api.crossref.org/works/" + quote(doi(source.doi) or "", safe="/"))[
            "message"
        ]
    else:
        data = client.get(
            "https://api.crossref.org/works", {"query.bibliographic": source.title, "rows": 1}
        )
        items = data.get("message", {}).get("items", [])
        if not items:
            return source
        message = items[0]
    return verify(source, message)
