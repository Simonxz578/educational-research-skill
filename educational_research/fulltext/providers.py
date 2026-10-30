"""OA pointers are discovery only. No retired Unpaywall search or Scholar scraper."""

import os
import re
from difflib import SequenceMatcher
from urllib.parse import quote
from ..core.access import FullTextLocation
from ..search import crossref
from ..utils.cache import FetchError


def licence_url(value):
    value = (value or "").lower().strip()
    if value.startswith("https://creativecommons.org/") or value.startswith(
        "http://creativecommons.org/"
    ):
        return value.replace("http://", "https://")
    licences = {"cc-by": "by/4.0/", "cc-by-sa": "by-sa/4.0/", "cc0": "../publicdomain/zero/1.0/"}
    if value == "cc0":
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    return "https://creativecommons.org/licenses/" + licences[value] if value in licences else ""


def open_permission(url):
    return bool(
        re.fullmatch(
            r"https?://creativecommons\.org/(?:licenses/by(?:-sa)?/[1-4]\.0|publicdomain/zero/1\.0)/?",
            url,
        )
    )


def discover_locations(source, client, providers=("crossref", "openalex", "unpaywall", "core")):
    locations = list(source.full_text_locations)
    if source.acquisition and source.acquisition.location:
        locations.append(source.acquisition.location)
    logs = []

    def request(provider, url, params=None, headers=None):
        try:
            result = client.get(url, params=params, headers=headers)
            logs.append(
                {"provider": provider, "status": "POINTER_RESPONSE_OBSERVED", "source_id": source.id}
            )
            return result
        except FetchError as exc:
            logs.append(
                {
                    "provider": provider,
                    "status": "UNAVAILABLE",
                    "source_id": source.id,
                    "reason": str(exc).split(": ")[-1],
                }
            )
            return {}

    def add(url, route, version="unknown", licence="", evidence=""):
        if not url:
            return
        if url.startswith("http://"):
            url = "https://" + url[len("http://") :]
        rights = licence_url(licence)
        locations.append(
            FullTextLocation(
                url=url,
                route=route,
                version=version
                if version in {"publishedVersion", "acceptedVersion", "submittedVersion"}
                else "unknown",
                licence_url=rights,
                licence_evidence_url=evidence,
                legal_basis="Public OA location; document licence and terms must be checked",
                processing_permission="allowed" if open_permission(rights) else "unclear",
            )
        )

    metadata = next(
        (
            p.get("raw_metadata")
            for p in reversed(source.provenance)
            if p.get("provider") == "Crossref" and p.get("raw_metadata") and not p.get("conflicts")
        ),
        {},
    )
    if source.doi and "crossref" in providers and not source.synthetic:
        response = request("Crossref", "https://api.crossref.org/works/" + quote(source.doi, safe="/"))
        if response.get("message"):
            metadata = response["message"]
            crossref.verify(source, metadata)
    licences = metadata.get("license", [])
    for link in metadata.get("link", []):
        ver = "publishedVersion" if link.get("content-version") == "vor" else "unknown"
        right = next(
            (
                x.get("URL", "")
                for x in licences
                if x.get("content-version") in {"vor", "unspecified", None}
            ),
            "",
        )
        add(link.get("URL"), "publisher", ver, right, f"https://api.crossref.org/works/{source.doi}")
    # The publisher landing page can expose real full HTML and citation_pdf_url; it is not pre-verified.
    if source.url.startswith(("http://", "https://")) and not source.synthetic:
        add(source.url, "eric" if "files.eric.ed.gov" in source.url else "publisher")
    if source.doi and "openalex" in providers and not source.synthetic:
        headers = (
            {"Authorization": "Bearer " + os.environ["OPENALEX_API_KEY"]}
            if os.getenv("OPENALEX_API_KEY")
            else None
        )
        result = request(
            "OpenAlex",
            "https://api.openalex.org/works/https://doi.org/" + quote(source.doi, safe="/"),
            headers=headers,
        )
        for loc in [result.get("best_oa_location"), *(result.get("locations") or [])]:
            if loc and loc.get("is_oa"):
                route = (
                    "publisher" if (loc.get("source") or {}).get("type") == "journal" else "repository"
                )
                add(
                    loc.get("pdf_url") or loc.get("landing_page_url"),
                    route,
                    loc.get("version"),
                    loc.get("license"),
                    result.get("id", ""),
                )
    if source.doi and not source.synthetic:
        add("https://doi.org/" + source.doi, "publisher")
    eric_meta = next(
        (p.get("raw_metadata", {}) for p in source.provenance if p.get("provider") == "ERIC"), {}
    )
    if source.eric_id and str(eric_meta.get("e_fulltextauth", "")).lower() in {"1", "true", "t", "yes"}:
        add("https://files.eric.ed.gov/fulltext/" + source.eric_id + ".pdf", "eric")
    email = os.getenv("UNPAYWALL_EMAIL")
    if source.doi and "unpaywall" in providers and not source.synthetic:
        if email:
            result = request(
                "Unpaywall",
                "https://api.unpaywall.org/v2/" + quote(source.doi, safe="/"),
                {"email": email},
            )
            for loc in result.get("oa_locations", []):
                add(
                    loc.get("url_for_pdf") or loc.get("url"),
                    "publisher" if loc.get("host_type") == "publisher" else "repository",
                    loc.get("version"),
                    loc.get("license"),
                    "https://api.unpaywall.org/v2/" + source.doi,
                )
        else:
            logs.append(
                {
                    "provider": "Unpaywall",
                    "status": "NOT_CHECKED",
                    "reason": "UNPAYWALL_EMAIL not configured",
                }
            )
    if source.doi and "core" in providers and not source.synthetic:
        if os.getenv("CORE_API_KEY") and os.getenv("CORE_API_TERMS_ACCEPTED") == "1":
            result = request(
                "CORE",
                "https://api.core.ac.uk/v3/search/works",
                {"q": f'doi:"{source.doi}"', "limit": 5},
                {"Authorization": "Bearer " + os.environ["CORE_API_KEY"]},
            )
            for work in result.get("results", []):
                same = crossref.doi(work.get("doi")) == source.doi
                same &= (
                    SequenceMatcher(
                        None,
                        crossref.clean_title(source.title),
                        crossref.clean_title(work.get("title", "")),
                    ).ratio()
                    >= 0.94
                )
                if same:
                    for url in (
                        work.get("downloadUrl", [])
                        if isinstance(work.get("downloadUrl"), list)
                        else [work.get("downloadUrl")]
                    ):
                        add(
                            url,
                            "core",
                            "unknown",
                            work.get("license"),
                            "https://api.core.ac.uk/v3/search/works",
                        )
        else:
            logs.append(
                {
                    "provider": "CORE",
                    "status": "NOT_CHECKED",
                    "reason": "CORE_API_KEY and CORE_API_TERMS_ACCEPTED=1 required; current provider terms apply",
                }
            )
    priority = {"publisher": 0, "eric": 1, "repository": 2, "core": 3, "manual": 4, "user": -1}
    version = {"publishedVersion": 0, "acceptedVersion": 1, "submittedVersion": 2, "unknown": 3}
    # Prefer richer rights/version provenance when several providers identify the same URL.
    ordered = sorted(
        locations, key=lambda x: (priority[x.route], version[x.version], not bool(x.licence_url), x.url)
    )
    seen, unique = set(), []
    for loc in ordered:
        key = loc.local_path or loc.url
        if key not in seen:
            unique.append(loc)
            seen.add(key)
    return unique, logs
