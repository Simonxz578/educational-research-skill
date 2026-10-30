"""API contract inspected at https://eric.ed.gov/api/eric-api.yaml."""

import logging
import json
import hashlib
from ..core.discovery import utc_now
from ..core.reading import sha256_file
import re
from ..models import Author, Source, Segment
from ..core.access import FullTextLocation
from ..config import today

API = "https://api.ies.ed.gov/eric/"
FIELDS = (
    "id,title,author,source,publicationdateyear,description,subject,peerreviewed,"
    "educationlevel,identifiersgeo,language,publicationtype,url,e_fulltextauth,sourceid"
)


def literal(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def query(
    topic,
    descriptors=(),
    peer_reviewed=False,
    year_from=None,
    year_to=None,
    education_level=None,
    geography=None,
):
    parts = [f"({topic})"]
    parts += [f"subject:{literal(d)}" for d in descriptors]
    if peer_reviewed:
        parts.append("peerreviewed:T")
    if year_from or year_to:
        parts.append(f"publicationdateyear:[{year_from or '*'} TO {year_to or '*'}]")
    if education_level:
        parts.append(f"educationlevel:{literal(education_level)}")
    if geography:
        parts.append(f"identifiersgeo:{literal(geography)}")
    return " AND ".join(parts)


def as_list(value):
    return value if isinstance(value, list) else [value] if value else []


def normalise(doc):
    authors = []
    for a in as_list(doc.get("author")):
        family, sep, given = a.partition(",")
        authors.append(Author(family=family.strip(), given=given.strip()) if sep else Author(literal=a))
    abstract = doc.get("description", "")
    url = f"https://eric.ed.gov/?id={doc['id']}"
    year_match = re.search(r"\d{4}", str(doc.get("publicationdateyear", "")))
    return Source(
        id=doc["id"],
        eric_id=doc["id"],
        title=doc.get("title", "Untitled record"),
        authors=authors,
        year=int(year_match[0]) if year_match else None,
        journal=doc.get("source", ""),
        abstract=abstract,
        access="ABSTRACT_ONLY" if abstract else "METADATA_ONLY",
        url=url,
        peer_reviewed={"T": True, "F": False}.get(str(doc.get("peerreviewed"))),
        descriptors=as_list(doc.get("subject")),
        education_level="; ".join(as_list(doc.get("educationlevel"))) or "not reported",
        country="; ".join(as_list(doc.get("identifiersgeo"))) or "not reported",
        providers=["ERIC"],
        full_text_locations=[
            FullTextLocation(url=u, route="eric" if "files.eric.ed.gov" in u else "publisher")
            for u in as_list(doc.get("url"))
            if str(u).startswith("https://")
        ],
        segments=[Segment(id="abstract", text=abstract, url=url, locator="ERIC abstract")]
        if abstract
        else [],
        provenance=[{"provider": "ERIC", "url": url, "checked_at": today(), "raw_metadata": doc}],
        warnings=["ERIC indexing does not establish evidence quality"],
    )


def search(client, search_query, limit=30, sort=None):
    records, log, start = [], [], 0
    # ERIC's documented endpoint supports start/rows, not an invented sort API.
    while len(records) < limit:
        params = {
            "search": search_query,
            "format": "json",
            "start": start,
            "rows": min(50, limit - len(records)),
            "fields": FIELDS,
        }
        data = client.get(API, params)
        response = data.get("response", {})
        docs = response.get("docs", [])
        log.append(
            {
                "provider": "ERIC",
                "status": "ERIC_SEARCHED",
                "query": search_query,
                "date": today(),
                "filters": params,
                "found": response.get("numFound", 0),
                "observed": len(docs),
                "ids": [d["id"] for d in docs],
            }
        )
        if not client.log or not client.log[-1].get("cache"):
            artifact = client.cache / (
                "eric-execution-"
                + hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
                + ".json"
            )
            artifact.write_text(json.dumps(data), encoding="utf-8")
            log[-1]["observation"] = {
                "provider": "ERIC",
                "query": search_query,
                "executed_at": utc_now(),
                "filters": params,
                "returned_count": response.get("numFound", 0),
                "results": [
                    {
                        "id": d["id"],
                        "title": d.get("title", ""),
                        "url": f"https://eric.ed.gov/?id={d['id']}",
                    }
                    for d in docs
                ],
                "artifact_path": str(artifact.resolve()),
                "artifact_sha256": sha256_file(artifact),
                "observation_kind": "api_response",
                "observer": "native ERIC adapter",
                "synthetic": False,
            }
        else:
            log[-1]["status"] = "ERIC_CACHED"
        records.extend(normalise(d) for d in docs)
        logging.info("ERIC batch start=%s observed=%s", start, len(docs))
        if not docs or start + len(docs) >= response.get("numFound", 0):
            break
        start += len(docs)
    return records, log
