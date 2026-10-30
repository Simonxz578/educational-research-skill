"""Lawful, bounded acquisition. Private files and observations never imply paper-read success."""

import hashlib
import ipaddress
import json
import re
import time
import socket
from xml.etree.ElementTree import ParseError
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode, urljoin
from urllib.robotparser import RobotFileParser
import httpx
from ..core.access import FullTextAcquisition, AccessAttempt
from ..core.discovery import utc_now
from ..core.reading import sha256_file
from .documents import extract, content_issues, ArticleHTML
from .providers import open_permission, licence_url, discover_locations

VERIFIED = {"OA_FULL_TEXT_VERIFIED", "REPOSITORY_FULL_TEXT_VERIFIED", "USER_SUPPLIED_LAWFUL_TEXT"}
SENSITIVE = {
    "api_key",
    "key",
    "token",
    "access_token",
    "password",
    "signature",
    "email",
    "x-amz-signature",
    "x-amz-credential",
    "x-amz-security-token",
}


def safe_url(url):
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in {None, 443}:
        raise ValueError("Only unauthenticated public HTTPS routes are supported")
    host = p.hostname.lower()
    if host in {"localhost", "metadata.google.internal"} or host.endswith((".local", ".internal")):
        raise ValueError("Private network routes are not acquisition sources")
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError("Non-public IP address is not an acquisition source")
    except ValueError as exc:
        if "Non-public" in str(exc):
            raise
        if re.fullmatch(r"[0-9.]+", host) or host.startswith("0x"):
            raise ValueError("Invalid public host") from None
    if any(
        key.lower() in SENSITIVE or key.lower().startswith("x-amz-") for key, _ in parse_qsl(p.query)
    ):
        raise ValueError("Credential-bearing URLs require authorised private handling")
    if any(name in host for name in ("sci-hub", "scihub", "libgen", "annas-archive")):
        raise ValueError("Unauthorised source route is not supported")
    return urlunsplit((p.scheme, p.netloc, p.path or "/", p.query, ""))


def display_url(url):
    p = urlsplit(url)
    query = [
        (k, "REDACTED" if k.lower() in SENSITIVE or k.lower().startswith("x-amz-") else v)
        for k, v in parse_qsl(p.query)
    ]
    return urlunsplit((p.scheme, p.hostname or "", p.path, urlencode(query), ""))


class AccessFailure(Exception):
    def __init__(self, status, reason, http_status=None, delay=None):
        self.status, self.reason, self.http_status, self.delay = status, reason, http_status, delay
        super().__init__(reason)


class Acquirer:
    def __init__(
        self, folder, metadata_client=None, transport=None, sleep=time.sleep, max_bytes=20_000_000
    ):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.folder.chmod(0o700)
        self.check_dns = transport is None
        self.metadata = metadata_client
        self.http = httpx.Client(
            transport=transport,
            timeout=25,
            follow_redirects=False,
            headers={
                "User-Agent": "EducationalResearchSkill/0.4.2 (lawful individual OA research)",
                "Accept": "application/pdf, application/xml, text/html;q=0.9",
            },
        )
        self.sleep, self.max_bytes = sleep, max_bytes
        self.robots, self.blocked_hosts = {}, set()
        self.last_request = {}

    def close(self):
        self.http.close()

    def _fetch(self, url, robots=True):
        current = safe_url(url)
        for _ in range(5):
            host = urlsplit(current).netloc
            if self.check_dns:
                try:
                    addresses = socket.getaddrinfo(
                        urlsplit(current).hostname, 443, type=socket.SOCK_STREAM
                    )
                    if not addresses or any(
                        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
                    ):
                        raise AccessFailure(
                            "FULL_TEXT_UNAVAILABLE", "DNS target is not a public network address"
                        )
                except socket.gaierror:
                    raise AccessFailure(
                        "FULL_TEXT_UNAVAILABLE", "Public host DNS could not be resolved"
                    ) from None
            if host in self.blocked_hosts:
                raise AccessFailure(
                    "PAYWALL_OR_LOGIN_BLOCKED", "Host paused after access denial or rate limit"
                )
            if robots and not self._permitted(current):
                raise AccessFailure(
                    "PAYWALL_OR_LOGIN_BLOCKED",
                    "robots.txt denies this access path or could not be checked",
                )
            if host in self.last_request:
                self.sleep(max(0, 1 - (time.monotonic() - self.last_request[host])))
            self.last_request[host] = time.monotonic()
            try:
                with self.http.stream("GET", current) as response:
                    status = response.status_code
                    if status in {301, 302, 303, 307, 308}:
                        current = safe_url(urljoin(current, response.headers.get("location", "")))
                        continue
                    if status in {401, 403, 429}:
                        delay = None
                        if status == 429:
                            from email.utils import parsedate_to_datetime
                            from datetime import datetime, timezone

                            value = response.headers.get("retry-after", "10")
                            try:
                                delay = max(0, float(value))
                            except ValueError:
                                try:
                                    delay = max(
                                        0,
                                        (
                                            parsedate_to_datetime(value) - datetime.now(timezone.utc)
                                        ).total_seconds(),
                                    )
                                except (ValueError, TypeError):
                                    delay = 10
                            # Do not retry this path; pause this host for the entire bounded run.
                            self.sleep(min(delay, 30))
                        self.blocked_hosts.add(host)
                        raise AccessFailure(
                            "PAYWALL_OR_LOGIN_BLOCKED",
                            "Access denied; stop this host/path and use an independent lawful route",
                            status,
                            delay,
                        )
                    if status != 200:
                        raise AccessFailure(
                            "FULL_TEXT_UNAVAILABLE", "HTTP response is not an available document", status
                        )
                    if int(response.headers.get("content-length", "0")) > self.max_bytes:
                        raise AccessFailure(
                            "FULL_TEXT_RETRIEVED_NOT_VALIDATED",
                            "Document exceeds bounded acquisition size",
                            status,
                        )
                    data = bytearray()
                    for chunk in response.iter_bytes():
                        data.extend(chunk)
                        if len(data) > self.max_bytes:
                            raise AccessFailure(
                                "FULL_TEXT_RETRIEVED_NOT_VALIDATED",
                                "Streaming size limit reached",
                                status,
                            )
                    return bytes(data), response.headers.get("content-type", ""), current
            except httpx.HTTPError:
                raise AccessFailure(
                    "FULL_TEXT_UNAVAILABLE", "Network/transport error; no document asserted"
                ) from None
        raise AccessFailure("FULL_TEXT_UNAVAILABLE", "Redirect limit reached")

    def _permitted(self, url):
        p = urlsplit(url)
        root = urlunsplit((p.scheme, p.netloc, "", "", ""))
        if root not in self.robots:
            try:
                data, _, _ = self._fetch(root + "/robots.txt", robots=False)
                parser = RobotFileParser()
                parser.parse(data.decode("utf-8", errors="replace").splitlines())
                self.robots[root] = parser
            except AccessFailure as exc:
                self.robots[root] = True if exc.http_status in {404, 410} else False
        policy = self.robots[root]
        return policy if isinstance(policy, bool) else policy.can_fetch("EducationalResearchSkill", url)

    def acquire(
        self,
        source,
        locations=None,
        max_routes=8,
        providers=("crossref", "openalex", "unpaywall", "core"),
    ):
        result = FullTextAcquisition(
            source_id=source.id, checked_at=utc_now(), metadata_identity=source.identity
        )
        if locations is None and self.metadata:
            locations, logs = discover_locations(source, self.metadata, providers)
            source.provenance.append(
                {"provider": "FullTextPointers", "observations": logs, "checked_at": utc_now()}
            )
        queue = list(locations if locations is not None else source.full_text_locations)
        seen = set()
        while queue and len(result.attempts) < max_routes:
            loc = queue.pop(0).model_copy(deep=True)
            key = loc.local_path or loc.url
            if key in seen:
                continue
            seen.add(key)
            try:
                if loc.route == "user":
                    if not (
                        loc.local_path
                        and loc.terms_checked
                        and loc.legal_basis
                        and loc.permission_evidence
                        and loc.processing_permission == "allowed"
                    ):
                        raise AccessFailure(
                            "RIGHTS_OR_VERSION_UNCLEAR",
                            "User access does not establish automated/hosted processing rights; record actual permitted scope first",
                        )
                    path = Path(loc.local_path)
                    if path.stat().st_size > self.max_bytes:
                        raise AccessFailure(
                            "FULL_TEXT_RETRIEVED_NOT_VALIDATED", "Local file exceeds size bound"
                        )
                    data, media, final_url = path.read_bytes(), "", loc.url
                else:
                    data, media, final_url = self._fetch(loc.url)
                if not data.lstrip().startswith(b"%PDF-"):
                    raw = data.decode("utf-8", errors="replace")
                    if any(
                        x in raw.lower()[:100000]
                        for x in [
                            "verify you are human",
                            "complete the captcha",
                            "sign in to access this article",
                            "purchase access to this article",
                            "access denied",
                        ]
                    ):
                        raise AccessFailure(
                            "PAYWALL_OR_LOGIN_BLOCKED",
                            "Login/CAPTCHA/paywall content is not full text",
                            200,
                        )
                    if "html" in media.lower() or "<html" in raw.lower():
                        parser = ArticleHTML()
                        parser.feed(raw)
                        rights = next(
                            iter(
                                parser.meta.get("dc.rights", [])
                                + parser.meta.get("dc.rights.license", [])
                                + [
                                    link.get("href", "")
                                    for link in parser.links
                                    if link.get("rel") == "license"
                                ]
                            ),
                            "",
                        )
                        if licence_url(rights):
                            loc.licence_url, loc.licence_evidence_url = licence_url(rights), final_url
                        # Individual publisher/repository links are pointers, never automatic full-text status.
                        for url in parser.meta.get("citation_pdf_url", []):
                            child = loc.model_copy(
                                update={"url": urljoin(final_url, url), "local_path": None}
                            )
                            if child.url not in seen:
                                queue.insert(0, child)
                result.retrieval_complete = True
                text, paragraphs, headings, media, pages = extract(data, media)
                issues = content_issues(source, text, paragraphs, headings)
                if issues:
                    status = (
                        "PAYWALL_OR_LOGIN_BLOCKED"
                        if "PAYWALL_OR_LOGIN_BLOCKED" in issues
                        else "ABSTRACT_ONLY"
                        if any("Abstract/fragment" in i for i in issues)
                        else "FULL_TEXT_RETRIEVED_NOT_VALIDATED"
                    )
                    raise AccessFailure(status, "; ".join(issues), 200)
                if source.identity not in {"VERIFIED", "SYNTHETIC"}:
                    raise AccessFailure(
                        "FULL_TEXT_RETRIEVED_NOT_VALIDATED",
                        "Bibliographic identity unresolved or conflicting; retained as candidate",
                        200,
                    )
                if loc.version == "unknown":
                    raise AccessFailure(
                        "RIGHTS_OR_VERSION_UNCLEAR",
                        "Actual version not established; do not borrow VoR pagination",
                        200,
                    )
                permitted = loc.route == "user" or (
                    open_permission(loc.licence_url) and bool(loc.licence_evidence_url)
                )
                if not permitted or loc.processing_permission in {"forbidden", "local_only"}:
                    raise AccessFailure(
                        "RIGHTS_OR_VERSION_UNCLEAR",
                        "Full document found, but permitted automated processing/licence evidence is unresolved",
                        200,
                    )
                loc.processing_permission = "allowed"
                loc.permission_evidence = loc.permission_evidence or loc.licence_evidence_url
                digest = hashlib.sha256(data).hexdigest()
                # Content-addressed paths prevent provider titles/IDs from escaping the private folder.
                extension = {"application/pdf": ".pdf", "text/html": ".html", "application/xml": ".xml"}[
                    media
                ]
                artifact = self.folder / (digest + extension)
                artifact.write_bytes(data)
                artifact.chmod(0o600)
                extracted = self.folder / (digest + ".txt")
                extracted.write_text(text, encoding="utf-8")
                extracted.chmod(0o600)
                result.status = (
                    "USER_SUPPLIED_LAWFUL_TEXT"
                    if loc.route == "user"
                    else "OA_FULL_TEXT_VERIFIED"
                    if loc.route in {"publisher", "eric"}
                    else "REPOSITORY_FULL_TEXT_VERIFIED"
                )
                result.location, result.artifact_path, result.sha256 = (
                    loc,
                    str(artifact.resolve()),
                    digest,
                )
                result.extracted_text_path, result.extracted_text_sha256 = (
                    str(extracted.resolve()),
                    sha256_file(extracted),
                )
                result.media_type, result.page_count, result.structure, result.paragraphs = (
                    media,
                    pages,
                    headings,
                    paragraphs,
                )
                result.metadata_identity, result.content_validated, result.legal_usage_verified = (
                    source.identity,
                    True,
                    True,
                )
                if loc.version != "publishedVersion":
                    result.version_difference = (
                        "Read the "
                        + loc.version
                        + "; findings, wording and locators may differ from the unavailable version of record."
                    )
                result.attempts.append(
                    AccessAttempt(
                        route=loc.route,
                        url=display_url(final_url),
                        checked_at=utc_now(),
                        status=result.status,
                        http_status=None if loc.route == "user" else 200,
                        reason="Actual body/identity/structure/version/rights checked by machine; close reading still required",
                    )
                )
                break
            except AccessFailure as exc:
                result.status = exc.status
                result.attempts.append(
                    AccessAttempt(
                        route=loc.route,
                        url=display_url(loc.url),
                        checked_at=utc_now(),
                        status=exc.status,
                        http_status=exc.http_status,
                        reason=exc.reason,
                        retry_after_seconds=exc.delay,
                    )
                )
            except (ValueError, OSError, RuntimeError, ParseError) as exc:
                result.status = "FULL_TEXT_RETRIEVED_NOT_VALIDATED"
                result.attempts.append(
                    AccessAttempt(
                        route=loc.route,
                        url=display_url(loc.url),
                        checked_at=utc_now(),
                        status=result.status,
                        reason="Unreadable resource: " + type(exc).__name__,
                    )
                )
        if (
            source.acquisition
            and source.reading
            and result.sha256
            and result.sha256 != source.reading.document.sha256
        ):
            result.close_reading_completed = False
            result.notice += " SOURCE_VERSION_CHANGED: prior reading is stale and must be repeated."
        source.acquisition = result
        return result


def acquisition_issues(acquisition, reading=None):
    if acquisition is None:
        return []
    issues = []
    if (
        acquisition.status not in VERIFIED
        or not acquisition.content_validated
        or not acquisition.legal_usage_verified
    ):
        issues.append("Acquisition/legal/completeness status does not establish usable full text")
    for path, digest in [
        (acquisition.artifact_path, acquisition.sha256),
        (acquisition.extracted_text_path, acquisition.extracted_text_sha256),
    ]:
        if not path or not digest or not Path(path).is_file() or sha256_file(path) != digest:
            issues.append("Acquired source/extraction changed or missing; revalidate and reread")
    if reading and (
        reading.document.sha256 != acquisition.sha256
        or not acquisition.location
        or reading.document.version != acquisition.location.version
    ):
        issues.append("SOURCE_VERSION_CHANGED: reading artifact/version differs from acquired document")
    return sorted(set(issues))


def write_access_outputs(output, sources, skipped=()):
    output = Path(output)
    rows = []
    handoff = [
        "# Full-text access handoff",
        "",
        "Private operator record. Retrieval, completeness, legal usage and close reading are separate; no institutional login is inherited.",
        "",
    ]
    for s in sources:
        a = s.acquisition
        if a and s.reading:
            from ..core.reading import reading_issues

            a.close_reading_completed = not reading_issues(s, reader_ready=True, require_depth=False)
        rows.append(
            {
                "source_id": s.id,
                "acquisition": a.model_dump() if a else None,
                "reading_record_present": s.reading is not None,
            }
        )
        if not a or a.status not in VERIFIED:
            handoff += [
                f"## {s.title}",
                f"DOI: {s.doi or 'No verified DOI'}; source: {display_url(s.url)}",
                f"Status: {a.status if a else 'NOT_ATTEMPTED'}; required version: identified VoR or explicitly identified lawful AAM/preprint.",
            ]
            if a:
                handoff += [f"- {x.route}: {x.url} — {x.status}: {x.reason}" for x in a.attempts]
            handoff += [
                "Next action: obtain an authorised copy and document processing/quotation scope, ask library staff for a lawful route, or choose an independently relevant accessible alternative. Do not send passwords or use proxy/CAPTCHA workarounds.",
                "",
            ]
    if skipped:
        handoff += ["Bounded acquisition did not attempt: " + ", ".join(skipped)]
    (output / "Full_Text_Access.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    (output / "Full_Text_Access_Handoff.md").write_text("\n".join(handoff), encoding="utf-8")
