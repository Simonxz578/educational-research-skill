"""Optional supplementary citation lookup with provenance and normal rate limiting."""

import os
from ..models import Metric
from ..config import today


def enrich(client, source):
    if not source.doi or source.identity != "VERIFIED":
        return source
    headers = (
        {"x-api-key": os.environ["SEMANTIC_SCHOLAR_API_KEY"]}
        if os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        else None
    )
    data = client.get(
        f"https://api.semanticscholar.org/graph/v1/paper/DOI:{source.doi}",
        {"fields": "title,citationCount,url"},
        headers,
    )
    if data.get("citationCount") is not None:
        source.metrics.append(
            Metric(
                name="article_citations",
                value=data["citationCount"],
                source=data["url"],
                checked_at=today(),
            )
        )
    return source
