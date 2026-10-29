"""Reproducible manual Scholar queries and genuine user export import; no scraper."""

import csv
from urllib.parse import urlencode
from ..config import today
from ..models import Source, Author


def plan(topic, since=None):
    queries = [
        f'"{topic}"',
        f"{topic} review meta-analysis",
        f"{topic} null contradictory findings",
        f"{topic} theory mechanism",
    ]
    return [
        {
            "query": q,
            "url": "https://scholar.google.com/scholar?"
            + urlencode({"q": q, **({"as_ylo": since} if since else {})}),
            "date": today(),
            "status": "GOOGLE_SCHOLAR_NOT_CHECKED",
        }
        for q in queries
    ]


def import_csv(path):
    """CSV exported/curated by user: title,authors,year,url,query,observed_at,cited_by.

    Observation provenance is required. Import is user-attested, never independently browser-verified.
    """
    records, logs = [], []
    with open(path, newline="", encoding="utf-8-sig") as stream:
        for i, row in enumerate(csv.DictReader(stream), 1):
            if not all(row.get(k) for k in ("title", "url", "query", "observed_at")):
                raise ValueError("Scholar import requires title, URL, exact query and observation date")
            records.append(
                Source(
                    id=f"SCH{i:04}",
                    title=row["title"],
                    authors=[
                        Author(literal=a.strip()) for a in row.get("authors", "").split(";") if a.strip()
                    ],
                    year=int(row["year"]) if row.get("year") else None,
                    url=row["url"],
                    providers=["Google Scholar user export"],
                    provenance=[
                        {
                            "provider": "Google Scholar",
                            "kind": "user-attested export",
                            "observed_at": row["observed_at"],
                            "url": row["url"],
                        }
                    ],
                )
            )
            logs.append(
                {
                    "provider": "Google Scholar",
                    "status": "SCHOLAR_USER_EXPORT_IMPORTED",
                    "query": row["query"],
                    "date": row["observed_at"],
                    "observed": 1,
                    "url": row["url"],
                    "citation_count_user_reported": row.get("cited_by"),
                }
            )
    return records, logs
