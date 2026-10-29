"""Named article citation index; not journal impact factor."""

import os
from urllib.parse import quote
from ..config import today
from ..models import Metric


def enrich(client, source):
    if not source.doi or source.identity != "VERIFIED":
        return source
    headers = (
        {"Authorization": "Bearer " + os.environ["OPENALEX_API_KEY"]}
        if os.getenv("OPENALEX_API_KEY")
        else None
    )
    url = "https://api.openalex.org/works/https://doi.org/" + quote(source.doi, safe="/")
    result = client.get(url, headers=headers)
    if result.get("cited_by_count") is not None:
        source.metrics.append(
            Metric(
                name="article_citations",
                value=result["cited_by_count"],
                source=result["id"],
                checked_at=today(),
            )
        )
    if result.get("fwci") is not None:
        source.metrics.append(
            Metric(name="FWCI", value=result["fwci"], source=result["id"], checked_at=today())
        )
    source.provenance.append(
        {"provider": "OpenAlex", "url": result.get("id", url), "checked_at": today()}
    )
    source.providers = sorted(set(source.providers + ["OpenAlex"]))
    return source
