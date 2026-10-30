"""Authentic abstract fallback; no unseen full-text claims or invented paraphrases."""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote
from ..core.evidence_types import AbstractEvidence, EvidenceRights
from ..core.discovery import utc_now
from ..core.reading import sha256_file
from ..core.verification import canonical
from ..search.crossref import clean_title, verify
from ..utils.cache import FetchError
from .documents import ArticleHTML, normal


def clean_abstract(value):
    from html.parser import HTMLParser

    class Plain(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
            self.hidden = 0

        def handle_starttag(self, tag, attrs):
            if tag in {"script", "style"}:
                self.hidden += 1
            if tag in {"p", "jats:p", "abstract", "jats:abstract", "title", "jats:title", "br", "sec"}:
                self.parts.append(" ")

        def handle_endtag(self, tag):
            if tag in {"script", "style"}:
                self.hidden = max(0, self.hidden - 1)
            self.parts.append(" ")

        def handle_data(self, text):
            if not self.hidden:
                self.parts.append(text)

    parser = Plain()
    parser.feed(value or "")
    return normal("".join(parser.parts))


def retain_abstract(
    source, folder, text, provider, source_url, rights=None, explanation="", explanation_checked=False
):
    text = clean_abstract(text)
    if not text or source.identity not in {"VERIFIED", "SYNTHETIC"}:
        return None
    rights = rights or EvidenceRights(
        access="allowed",
        processing="allowed",
        private_retention="allowed",
        access_basis="Actual public scholarly metadata/abstract response",
        processing_basis="Public metadata API abstract inspection; not private institutional content",
        retention_basis="Private provenance record of the accessed published abstract",
        public_quotation="not_checked",
    )
    if any(getattr(rights, k) != "allowed" for k in ["access", "processing", "private_retention"]):
        return None
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    folder.chmod(0o700)
    payload = {
        "source_id": source.id,
        "publication_id": source.doi or source.eric_id or source.work_id or source.url,
        "title": source.title,
        "source_url": source_url,
        "provider": provider,
        "version": "publishedAbstract",
        "text": text,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    path = folder / (hashlib.sha256(encoded).hexdigest() + ".json")
    path.write_bytes(encoded)
    path.chmod(0o600)
    evidence = AbstractEvidence(
        **payload,
        artifact_path=str(path.resolve()),
        artifact_sha256=sha256_file(path),
        extraction_sha256=hashlib.sha256(canonical(text).encode()).hexdigest(),
        checked_at=utc_now(),
        identity_verified=True,
        rights=rights,
        explanation=explanation,
        explanation_checked=explanation_checked,
    )
    source.abstract_evidence = evidence
    source.abstract = text
    return evidence


def abstract_issues(source):
    a = source.abstract_evidence
    if a is None:
        return ["No verified published abstract"]
    issues = []
    if (
        source.identity not in {"VERIFIED", "SYNTHETIC"}
        or not a.identity_verified
        or a.source_id != source.id
        or a.publication_id != (source.doi or source.eric_id or source.work_id or source.url)
        or clean_title(a.title) != clean_title(source.title)
    ):
        issues.append("Published abstract identity/source/version mismatch")
    if (
        not a.text.strip()
        or not a.source_url.startswith(("http://", "https://"))
        or a.version != "publishedAbstract"
    ):
        issues.append("Missing actual abstract text, URL or published-abstract version")
    if any(getattr(a.rights, k) != "allowed" for k in ["access", "processing", "private_retention"]):
        issues.append("Abstract access/processing/private-retention scope unresolved")
    path = Path(a.artifact_path)
    if not path.is_file() or sha256_file(path) != a.artifact_sha256:
        issues.append("Published abstract artifact missing or changed")
    else:
        try:
            saved = json.loads(path.read_text())
            if any(
                saved.get(k) != getattr(a, k)
                for k in [
                    "source_id",
                    "publication_id",
                    "title",
                    "source_url",
                    "provider",
                    "version",
                    "text",
                ]
            ):
                issues.append("Abstract does not match its original response record")
        except (ValueError, OSError):
            issues.append("Unreadable abstract verifier")
    if hashlib.sha256(canonical(a.text).encode()).hexdigest() != a.extraction_sha256:
        issues.append("Abstract extraction digest mismatch")
    if a.quotation:
        from .providers import open_permission

        extended = (
            source.permissive_licence_url == a.rights.licence_url
            and open_permission(a.rights.licence_url)
            and bool(a.rights.quotation_basis)
        ) or (
            a.rights.public_word_allowance is not None
            and a.rights.public_word_allowance >= source.quote_budget
            and bool(a.rights.quotation_basis)
        )
        if source.quote_budget > 20 and not extended:
            issues.append("Extended abstract reproduction lacks verified licence/permission scope")
        if (
            a.rights.public_quotation != "allowed"
            or not a.rights.quotation_basis
            or canonical(a.quotation) not in canonical(a.text)
        ):
            issues.append("Abstract quotation is not matched/permitted")
        from ..models import quotation_units

        used = quotation_units(a.quotation) * (
            1
            + ((a.explanation if a.explanation_checked else "") + " " + a.interpretation).count(
                a.quotation
            )
        )
        if used > source.quote_budget:
            issues.append("Abstract quotation budget exceeded")
    return sorted(set(issues))


def acquire_abstract(source, folder, metadata_client=None, acquirer=None):
    """Publisher abstract first; indexed abstract next. Network attempts remain bounded."""
    if source.abstract_evidence and not abstract_issues(source):
        return source.abstract_evidence
    if source.identity == "CONFLICT":
        return None
    if acquirer and source.url.startswith("https://"):
        from .acquire import AccessFailure

        try:
            data, media, url = acquirer._fetch(source.url)
            if "html" in media or b"<html" in data[:2000].lower():
                parser = ArticleHTML()
                parser.feed(data.decode("utf-8", errors="replace"))
                title = next(iter(parser.meta.get("citation_title", [])), None)
                if (
                    title
                    and clean_title(title) == clean_title(source.title)
                    and source.identity == "VERIFIED"
                ):
                    texts = parser.meta.get("citation_abstract", []) + parser.meta.get(
                        "dc.description", []
                    )
                    if not texts:
                        active = False
                        parts = []
                        for tag, value in parser.blocks:
                            if tag.startswith("h"):
                                if active:
                                    break
                                active = value.strip().lower() == "abstract"
                            elif active:
                                parts.append(value)
                        texts = [" ".join(parts)] if parts else []
                    if texts and texts[0].strip():
                        return retain_abstract(source, folder, texts[0], "publisher", url)
        except (AccessFailure, ValueError, OSError):
            pass
    metadata = next(
        (
            p.get("raw_metadata")
            for p in reversed(source.provenance)
            if p.get("provider") == "Crossref" and p.get("raw_metadata") and not p.get("conflicts")
        ),
        None,
    )
    if metadata_client and source.doi and (not metadata or not metadata.get("abstract")):
        try:
            metadata = metadata_client.get(
                "https://api.crossref.org/works/" + quote(source.doi, safe="/")
            ).get("message", {})
            verify(source, metadata)
        except FetchError:
            metadata = None
    if metadata and metadata.get("abstract") and source.identity == "VERIFIED":
        verify(source, metadata)
        if source.identity == "VERIFIED":
            return retain_abstract(
                source,
                folder,
                metadata["abstract"],
                "Crossref",
                "https://api.crossref.org/works/" + source.doi,
            )
    eric = next(
        (p.get("raw_metadata", {}) for p in source.provenance if p.get("provider") == "ERIC"), {}
    )
    if (
        eric.get("description")
        and eric.get("id") == source.eric_id
        and clean_title(eric.get("title", "")) == clean_title(source.title)
        and source.identity != "CONFLICT"
    ):
        if not source.doi:
            source.identity = "VERIFIED"
        return retain_abstract(
            source, folder, eric["description"], "ERIC", "https://eric.ed.gov/?id=" + source.eric_id
        )
    return None


def abstract_explanation(evidence):
    if evidence.explanation_checked and evidence.explanation.strip():
        return evidence.explanation
    # A safe automatic projection reports only literal topical mentions, never invented outcomes.
    concepts = [
        label
        for pattern, label in [
            (r"\binterviews?\b", "interviews"),
            (r"\bsurveys?\b", "surveys"),
            (r"\brandomi[sz]ed\b", "random allocation"),
            (r"\bqualitative\b", "qualitative research"),
            (r"\blongitudinal\b", "longitudinal research"),
            (r"\bretrieval\b", "retrieval practice"),
            (r"\bcareer\b", "career-related questions"),
        ]
        if re.search(pattern, evidence.text, re.I)
    ]
    if concepts:
        return (
            "According to the published abstract, the topics explicitly mentioned include "
            + ", ".join(concepts[:3])
            + ". No further method, result or limitation is inferred from these mentions."
        )
    return "A matching published abstract is available at the source link. Its full-text methods, results and limitations remain unverified; no additional author claim is inferred."
