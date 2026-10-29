import os
import httpx
import pytest
from educational_research.utils.cache import Client, FetchError
from educational_research.search import eric, crossref


def test_rate_limit_cache_and_offline(tmp_path):
    attempts = []

    def response(request):
        attempts.append(request)
        if len(attempts) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(
            200,
            json={
                "response": {
                    "numFound": 1,
                    "docs": [
                        {
                            "id": "EJ000001",
                            "title": "Synthetic record",
                            "peerreviewed": "T",
                            "subject": ["Test descriptor"],
                        }
                    ],
                }
            },
        )

    client = Client(tmp_path, transport=httpx.MockTransport(response), sleep=lambda x: None)
    q = eric.query("reading", ["Reading Comprehension"], True, 2020, 2025, "Higher Education")
    sources, log = eric.search(client, q, 1)
    assert sources[0].eric_id == "EJ000001" and sources[0].peer_reviewed
    assert "peerreviewed:T" in attempts[-1].url.params["search"]
    assert log[0]["status"] == "ERIC_SEARCHED"
    eric.search(client, q, 1)
    assert len(attempts) == 2 and client.log[-1]["cache"]
    client.offline = True
    with pytest.raises(FetchError, match="OFFLINE"):
        eric.search(client, q, 1)


def test_failure_does_not_claim_search(tmp_path):
    client = Client(
        tmp_path, transport=httpx.MockTransport(lambda r: httpx.Response(503)), sleep=lambda _: None
    )
    with pytest.raises(FetchError):
        eric.search(client, "test", 1)


@pytest.mark.live
@pytest.mark.skipif(
    not os.getenv("RUN_LIVE_TESTS"), reason="Opt-in live ERIC/Crossref smoke tests; not executed offline"
)
def test_live_eric_and_metadata(tmp_path):
    client = Client(tmp_path)
    try:
        records, logs = eric.search(client, 'subject:"Reading Comprehension" AND peerreviewed:T', 1)
        message = client.get("https://api.crossref.org/works/10.1037/0033-295X.84.2.191")["message"]
    except FetchError as exc:
        pytest.skip(f"Network/provider unavailable: {exc}")
    assert records and records[0].eric_id and records[0].peer_reviewed
    assert logs[0]["status"] == "ERIC_SEARCHED"
    assert crossref.doi(message["DOI"]) == "10.1037/0033-295x.84.2.191"


def test_scholar_export_is_attested_not_automated_search(tmp_path):
    from educational_research.search.google_scholar_workflow import import_csv, plan

    file = tmp_path / "manual.csv"
    file.write_text(
        "title,url,query,observed_at\nTEST ONLY,https://example.test/paper,library learning,2026-10-29\n"
    )
    records, log = import_csv(file)
    assert records[0].identity == "UNVERIFIED"
    assert log[0]["status"] == "SCHOLAR_USER_EXPORT_IMPORTED"
    assert all(p["status"] == "GOOGLE_SCHOLAR_NOT_CHECKED" for p in plan("library learning"))
    file.write_text("title,url\nTEST ONLY,https://example.test/paper\n")
    with pytest.raises(ValueError, match="observation date"):
        import_csv(file)


def test_eric_query_keeps_explicit_context():
    q = eric.query(
        "learning", ["Learning Strategies"], True, 2020, 2025, "Primary Education", "United Kingdom"
    )
    assert 'educationlevel:"Primary Education"' in q
    assert 'identifiersgeo:"United Kingdom"' in q
    assert "publicationdateyear:[2020 TO 2025]" in q
