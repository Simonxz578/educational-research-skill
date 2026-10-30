"""Count actual non-overlapping author-text positions, never explanation words."""

import hashlib
import re
import unicodedata
from pathlib import Path
from .reading import document_text, sha256_file
from .evidence_depth import english_words, evidence_anchors


def canonical(text):
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    text = text.translate(
        str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "\u00a0": " "})
    )
    return re.sub(r"\s+", " ", text).strip()


def verbatim_audit(source):
    result = {
        "kind": "VERBATIM_PRIMARY_TEXT",
        "scope": "FULL_TEXT",
        "verified_original_words": 0,
        "original_word_shortfall": 100,
        "threshold": 100,
        "spans": [],
        "issues": [],
    }
    r = source.reading
    if r is None:
        if source.abstract_evidence:
            result.update(
                scope="ABSTRACT_ONLY",
                gate_status="NOT_APPLICABLE_TO_ABSTRACT / NOT_FULL_TEXT_VERIFIED",
                original_word_shortfall=None,
                abstract_original_words=len(english_words(source.abstract_evidence.text)),
                issues=["Published abstract is not a deep full-text reading"],
            )
            return result
        result["issues"] = [
            "No actual full-text reading/spans; explanation does not count as author text"
        ]
        return result
    doc = r.document
    if doc.processing_permission != "allowed" or (
        doc.rights
        and any(
            getattr(doc.rights, k) != "allowed" for k in ["access", "processing", "private_retention"]
        )
    ):
        result["issues"] = [
            "Original text was not inspected: access/processing/retention rights unresolved"
        ]
        return result
    if r.access_status in {"ABSTRACT_ONLY", "METADATA_ONLY"} or "abstract" in doc.version.casefold():
        result.update(
            scope="ABSTRACT_ONLY",
            gate_status="NOT_APPLICABLE_TO_ABSTRACT / NOT_FULL_TEXT_VERIFIED",
            original_word_shortfall=None,
            issues=["Abstract/metadata version is not a full-text inspection"],
        )
        return result
    if (
        source.acquisition
        and source.acquisition.location
        and (
            doc.version != source.acquisition.location.version or doc.sha256 != source.acquisition.sha256
        )
    ):
        result["issues"] = ["Original source version/artifact differs from the validated acquisition"]
        return result
    path = Path(doc.local_path)
    if r.source_id != source.id or not path.is_file() or sha256_file(path) != doc.sha256:
        result["issues"] = ["Wrong source or missing/changed full-text artifact"]
        return result
    try:
        actual = canonical(document_text(str(path.resolve()), doc.sha256))
    except (OSError, ValueError, RuntimeError, UnicodeError):
        result["issues"] = ["Original version cannot be extracted for inspection"]
        return result
    segments = {f"{source.id}:{s.id}": s for s in source.segments}
    covered, seen = set(), set()
    word_positions = [
        (m.start(), m.end()) for m in re.finditer(r"\b[A-Za-z]+(?:['-][A-Za-z]+)*\b", actual)
    ]
    for entry in evidence_anchors(r):
        if entry is None:
            result["issues"].append("Four distinct substantive original-text roles are required")
            continue
        span = canonical(entry.exact_span)
        if (
            re.search(
                r"(?:^|/)\s*(?:abstract|references|bibliography|metadata|front matter|title)(?:\s*,|\s*$|\s*/)",
                entry.locator,
                re.I,
            )
            or entry.locator.lower().startswith("jats metadata")
            or (span and span in canonical(source.title))
        ):
            result["issues"].append(
                f"{entry.evidence_id}: title/metadata/abstract/reference text is not full-text argument evidence"
            )
            continue
        segment = segments.get(entry.evidence_id)
        if (
            not span
            or entry.status != "checked_against_text"
            or segment is None
            or entry.locator != segment.locator
        ):
            result["issues"].append(
                f"{entry.evidence_id}: unchecked/misattributed original span or locator"
            )
            continue
        from urllib.parse import urldefrag

        urls = {
            urldefrag(url)[0]
            for url in [
                source.url,
                doc.source_url,
                "https://doi.org/" + source.doi if source.doi else "",
            ]
            if url
        }
        if source.acquisition and source.acquisition.location:
            urls.add(urldefrag(source.acquisition.location.url)[0])
        if urldefrag(segment.url)[0] not in urls:
            result["issues"].append(
                f"{entry.evidence_id}: passage URL belongs to a different source/route"
            )
            continue
        if segment.text and span not in canonical(segment.text):
            result["issues"].append(f"{entry.evidence_id}: text does not match its source passage")
            continue
        matches = [m.start() for m in re.finditer(re.escape(span), actual)]
        start = entry.start_offset
        if start is not None:
            if start not in matches or entry.end_offset != start + len(span):
                result["issues"].append(f"{entry.evidence_id}: invalid canonical source offsets")
                continue
        elif len(matches) == 1:
            start = matches[0]
        else:
            result["issues"].append(
                f"{entry.evidence_id}: absent or ambiguous span; provide exact canonical offsets"
            )
            continue
        end = start + len(span)
        positions = {i for i, (a, b) in enumerate(word_positions) if start <= a and b <= end}
        if span in seen or not positions or positions & covered:
            result["issues"].append(
                f"{entry.evidence_id}: repeated/overlapping spans cannot inflate original words"
            )
        else:
            covered.update(positions)
        seen.add(span)
        words = english_words(span)
        if len(words) >= 20 and len(set(w.lower() for w in words)) < len(words) / 4:
            result["issues"].append(
                f"{entry.evidence_id}: repeated-word padding is not substantive original evidence"
            )
        result["spans"].append(
            {
                "source_id": source.id,
                "publication_id": source.doi
                or source.work_id
                or source.eric_id
                or source.url
                or source.id,
                "evidence_id": entry.evidence_id,
                "source_url": segment.url,
                "version": doc.version,
                "artifact_sha256": doc.sha256,
                "extraction_sha256": hashlib.sha256(actual.encode()).hexdigest(),
                "locator": entry.locator,
                "start_offset": start,
                "end_offset": end,
                "offset_basis": "NFKC punctuation/whitespace canonical extraction",
                "exact_text": entry.exact_span,
                "role": entry.content_type,
                "attributed_claim": entry.paraphrase,
                "reader": r.reader,
                "read_at": r.read_at,
                "scope": r.coverage,
                "rights": doc.rights.model_dump() if doc.rights else None,
            }
        )
    result["verified_original_words"] = len(covered)
    result["original_word_shortfall"] = max(0, 100 - len(covered))
    if len(covered) < 100:
        result["issues"].append(
            f"Verbatim original-text inspection shortfall: {len(covered)}/100; AI explanation is excluded"
        )
    result["issues"] = sorted(set(result["issues"]))
    return result
