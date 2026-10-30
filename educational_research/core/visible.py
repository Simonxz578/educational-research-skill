"""Source-first excerpts and independent finished-PDF word-position verification."""

import re
from .verification import canonical, verbatim_audit
from .reading import document_text
from .evidence_depth import english_words
from ..fulltext.providers import open_permission


def allowance(source, abstract=False):
    rights = source.abstract_evidence.rights if abstract else source.reading.document.rights
    if not rights or rights.public_quotation != "allowed" or not rights.quotation_basis:
        return 0
    if rights.public_word_allowance is not None:
        return rights.public_word_allowance
    licence = rights.licence_url or source.permissive_licence_url
    if licence and open_permission(licence):
        return 150  # MVP target 100; retain compact original passages, never an entire work.
    return min(20, source.quote_budget)


def take(text, count):
    words = list(re.finditer(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", text))
    if len(words) <= count:
        return text
    return text[: words[count - 1].end()] if count else ""


def excerpts(source):
    from .reader import ReaderQuote
    from .reading import reader_scope

    abstract = reader_scope(source) == "ABSTRACT_ONLY"
    cap = min(100, allowance(source, abstract))
    if abstract:
        a = source.abstract_evidence
        candidates = [
            (a.text, source.id + ":published_abstract", "Published abstract; " + a.version, a.source_url)
        ]
    else:
        audit = verbatim_audit(source)
        candidates = [
            (s["exact_text"], s["evidence_id"], s["locator"] + "; " + s["version"], s["source_url"])
            for s in audit["spans"]
        ]
        # With limited rights, use the already reviewed short fragments.
        if cap < 100:
            candidates = [
                (
                    q.text,
                    source.id + ":" + q.segment_id,
                    next(s.locator for s in source.segments if s.id == q.segment_id)
                    + "; "
                    + source.reading.document.version,
                    source.url,
                )
                for q in source.quotes
            ]
    # Prefer complete sentences across roles when they fit the reviewed amount.
    # The 100-word fallback explicitly marks any necessary boundary omission.
    if not abstract and allowance(source, abstract) >= 100:
        complete = []
        for text, eid, locator, url in candidates:
            end = re.search(r'[.!?]["”’)]*(?=\s|$)', text)
            if end:
                value = text[: end.end()]
                complete.append(
                    ReaderQuote(
                        text=value,
                        evidence_id=eid,
                        locator=locator,
                        url=url,
                        omitted_after=len(value) < len(text),
                    )
                )
        total = sum(len(english_words(q.text)) for q in complete)
        if len(complete) == len(candidates) and 100 <= total <= min(150, allowance(source, abstract)):
            return complete
    result = []
    for text, eid, locator, url in candidates:
        remaining = cap - sum(len(english_words(q.text)) for q in result)
        if remaining <= 0:
            break
        quota = remaining if abstract or cap < 100 else min(25, remaining)
        value = take(text, quota)
        if value:
            result.append(
                ReaderQuote(
                    text=value,
                    evidence_id=eid,
                    locator=locator,
                    url=url,
                    omitted_after=len(value) < len(text),
                )
            )
    return result


def count_display(source, quotes, printed=None):
    """Count distinct positions in the actual version, restricted to the source's PDF block."""
    from .reading import reader_scope
    from ..fulltext.abstracts import abstract_issues

    abstract = reader_scope(source) == "ABSTRACT_ONLY"
    issues = []
    if abstract:
        a = source.abstract_evidence
        issues += abstract_issues(source)
        actual = canonical(a.text)
        permitted = [actual]
        version = a.version
        locations = {source.id + ":published_abstract": "Published abstract; " + version}
    else:
        from .reading import sha256_file
        from pathlib import Path

        doc = source.reading.document
        if (
            not Path(doc.local_path).is_file()
            or sha256_file(doc.local_path) != doc.sha256
            or source.reading.source_id != source.id
        ):
            return dict(
                shown=0,
                target=100,
                status="PROVISIONAL",
                reason="original artifact identity/digest mismatch",
                issues=["Original artifact identity/digest mismatch"],
            )
        audit = verbatim_audit(source)
        actual = canonical(
            document_text(source.reading.document.local_path, source.reading.document.sha256)
        )
        permitted = [canonical(s["exact_text"]) for s in audit["spans"]]
        permitted += [canonical(q.text) for q in source.quotes]
        version = source.reading.document.version
        locations = {s["evidence_id"]: s["locator"] + "; " + version for s in audit["spans"]}
        locations.update(
            {
                source.id + ":" + q.segment_id: next(
                    s.locator for s in source.segments if s.id == q.segment_id
                )
                + "; "
                + version
                for q in source.quotes
            }
        )
    positions = set()
    tokens = list(re.finditer(r"\b[A-Za-z]+(?:['-][A-Za-z]+)*\b", actual))
    printed = canonical(printed) if printed is not None else None
    for q in quotes:
        span = canonical(q.text)
        if (
            not span
            or not q.evidence_id.startswith(source.id + ":")
            or not any(span in p for p in permitted)
            or q.locator != locations.get(q.evidence_id)
        ):
            issues.append("Unverified original passage/version")
            continue
        matches = list(re.finditer(re.escape(span), actual))
        if len(matches) != 1:
            issues.append("Ambiguous or absent original span")
            continue
        if (
            printed is not None
            and ("“" + span + "”") not in printed
            and ('"' + span + '"') not in printed
            and ('"' + span + ' [...]"') not in printed
        ):
            issues.append("Original passage missing from finished PDF")
            continue
        m = matches[0]
        found = {i for i, w in enumerate(tokens) if m.start() <= w.start() and w.end() <= m.end()}
        if positions & found:
            issues.append("Repeated/overlapping original positions")
        positions.update(found)
    if sum(len(english_words(q.text)) for q in quotes) > allowance(source, abstract):
        issues.append("Public quotation allowance exceeded")
    shown = len(positions)
    reason = (
        "reproduction permission not established"
        if allowance(source, abstract) == 0
        else "permitted quotation allowance below target"
        if allowance(source, abstract) < 100
        else "available verified original passages below target"
    )
    return dict(
        shown=shown,
        target=100,
        status="PASS" if shown >= 100 and not issues else "PROVISIONAL",
        reason="" if shown >= 100 and not issues else reason,
        issues=issues,
    )


def project(source, paper):
    paper.display_excerpts = excerpts(source)
    audit = count_display(source, paper.display_excerpts)
    paper.original_words_shown = audit["shown"]
    paper.display_status = audit["status"]
    paper.display_reason = audit["reason"]
