"""Adversarial synthetic HTTP documents: retrieval never certifies actual research reading."""

from pathlib import Path
import fitz
import httpx
import pytest
from educational_research.core.access import FullTextLocation
from educational_research.fulltext.acquire import Acquirer, acquisition_issues, safe_url, VERIFIED
from educational_research.models import Author, Source
from tests.v3_factory import bundle

TITLE = "TEST ONLY Study Routines and Independent Learning Outcomes"
LICENCE = "https://creativecommons.org/licenses/by/4.0/"


def work():
    return Source(
        id="TEST_ACCESS",
        title=TITLE,
        authors=[Author(family="Fictional", given="Synthetic")],
        doi="10.5555/test-only-access",
        year=2024,
        identity="SYNTHETIC",
        synthetic=True,
        url="https://publisher.example.test/article",
        abstract="TEST ONLY abstract; metadata does not establish an accessible full text.",
    )


def location(url="https://publisher.example.test/article", **kwargs):
    values = dict(
        url=url,
        route="publisher",
        version="publishedVersion",
        licence_url=LICENCE,
        licence_evidence_url="https://publisher.example.test/licence",
        legal_basis="Generated TEST ONLY mock document with explicit permissive licence",
    )
    values.update(kwargs)
    return FullTextLocation(**values)


def paragraph(section, index):
    return (
        f"TEST ONLY {section} paragraph {index}. "
        "This generated document tests machine extraction and validation boundaries. "
        "No genuine participant, institution, article, author, empirical observation or research claim is represented. "
        "A synthetic account of reported study routines is kept distinct from independently observed learning outcomes. "
        "The example merely exercises document signatures, substantive section structure and stable paragraph locations. "
        "All hypothetical measures, procedures, comparisons and limitations must remain fictional. "
        "Retrieval success cannot establish that a researcher has critically read the document or that a source may be republished. "
        "Actual interpretation requires lawful primary evidence and separate critical assessment."
    )


def full_html(extra=""):
    sections = ["Introduction", "Methods", "Results", "Discussion", "References"]
    body = "".join(
        f"<h2>{section}</h2>" + "".join(f"<p>{paragraph(section, index)}</p>" for index in (1, 2))
        for section in sections
    )
    return (
        f'<html><head><link rel="license" href="{LICENCE}"></head>'
        f"<body><h1>{TITLE}</h1><p>Synthetic Fictional, 2024</p><article>{body}</article>{extra}</body></html>"
    ).encode()


def readable_pdf():
    with fitz.open() as doc:
        for section in ["Introduction", "Methods", "Results", "Discussion", "References"]:
            page = doc.new_page()
            page.insert_textbox(
                fitz.Rect(45, 40, 550, 100), TITLE + "\nSynthetic Fictional, 2024", fontsize=12
            )
            page.insert_textbox(fitz.Rect(45, 110, 550, 145), section, fontsize=12)
            page.insert_textbox(fitz.Rect(45, 160, 550, 420), paragraph(section, 1), fontsize=11)
            page.insert_textbox(fitz.Rect(45, 450, 550, 710), paragraph(section, 2), fontsize=11)
        return doc.tobytes()


def run_acquisition(
    tmp_path, responses, locations=None, source=None, robots="User-agent: *\nAllow: /", **kwargs
):
    requested, sleeps = [], []

    def handle(request):
        requested.append(str(request.url))
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=robots, headers={"content-type": "text/plain"})
        value = responses.get(str(request.url))
        if callable(value):
            return value(request)
        if value is None:
            raise AssertionError("Unexpected network request: " + str(request.url))
        status, data, content_type, headers = value
        return httpx.Response(status, content=data, headers={"content-type": content_type, **headers})

    acquirer = Acquirer(tmp_path, transport=httpx.MockTransport(handle), sleep=sleeps.append, **kwargs)
    source = source or work()
    try:
        result = acquirer.acquire(source, locations=locations or [location()])
    finally:
        acquirer.close()
    return source, result, requested, sleeps


def test_doi_abstract_page_cannot_count_as_full_text(tmp_path):
    body = f"<html><h1>{TITLE}</h1><p>Synthetic Fictional</p><h2>Abstract</h2><p>{work().abstract}</p></html>".encode()
    source, result, _, _ = run_acquisition(tmp_path, {location().url: (200, body, "text/html", {})})
    assert result.status == "ABSTRACT_ONLY"
    assert result.retrieval_complete and not result.content_validated
    assert not result.close_reading_completed and source.reading is None
    assert not result.artifact_path


def test_fake_pdf_with_login_html_and_403_stop_paths(tmp_path):
    fake = "https://publisher.example.test/paper.pdf"
    source, result, requested, _ = run_acquisition(
        tmp_path / "fake",
        {fake: (200, b"<html><p>Sign in to access this article</p></html>", "application/pdf", {})},
        [location(fake)],
    )
    assert result.status == "PAYWALL_OR_LOGIN_BLOCKED"
    assert not result.artifact_path and source.reading is None
    assert requested.count(fake) == 1
    blocked = "https://publisher.example.test/blocked"
    later = "https://publisher.example.test/another"
    _, result, requested, _ = run_acquisition(
        tmp_path / "denied",
        {blocked: (403, b"Forbidden", "text/html", {})},
        [location(blocked), location(later)],
    )
    assert result.status == "PAYWALL_OR_LOGIN_BLOCKED"
    assert blocked in requested and later not in requested


def test_429_obeys_backoff_stops_host_and_tries_independent_route(tmp_path):
    first = "https://publisher.example.test/rate-limited"
    same = "https://publisher.example.test/another-route"
    fallback = "https://repository.example.test/aam"
    _, result, requested, sleeps = run_acquisition(
        tmp_path,
        {
            first: (429, b"Rate limited", "text/plain", {"Retry-After": "7"}),
            fallback: (200, full_html(), "text/html", {}),
        },
        [
            location(first),
            location(same),
            location(fallback, route="repository", version="acceptedVersion"),
        ],
    )
    assert requested.count(first) == 1 and same not in requested
    assert 7 in sleeps and result.attempts[0].retry_after_seconds == 7
    assert result.status == "REPOSITORY_FULL_TEXT_VERIFIED"
    assert "acceptedVersion" in result.version_difference
    assert not result.close_reading_completed


@pytest.mark.parametrize(
    "content,media,expected_media",
    [(readable_pdf, "application/pdf", "application/pdf"), (full_html, "text/html", "text/html")],
)
def test_actual_document_bytes_validate_without_inventing_reading(
    tmp_path, content, media, expected_media
):
    source, result, _, _ = run_acquisition(tmp_path, {location().url: (200, content(), media, {})})
    assert result.status == "OA_FULL_TEXT_VERIFIED"
    assert result.retrieval_complete and result.content_validated and result.legal_usage_verified
    assert result.media_type == expected_media and Path(result.artifact_path).is_file()
    assert Path(result.extracted_text_path).is_file() and not acquisition_issues(result)
    assert not result.close_reading_completed and source.reading is None
    assert all(row["locator"] and row["text"] for row in result.paragraphs)
    if expected_media == "application/pdf":
        assert result.page_count == 5 and result.paragraphs[0]["locator"].startswith("PDF page")
    else:
        assert any("Methods, paragraph" in row["locator"] for row in result.paragraphs)


def test_aam_version_is_retained_and_unknown_version_is_not_promoted(tmp_path):
    url = location().url
    _, aam, _, _ = run_acquisition(
        tmp_path / "aam",
        {url: (200, full_html(), "text/html", {})},
        [location(route="repository", version="acceptedVersion")],
    )
    assert aam.status == "REPOSITORY_FULL_TEXT_VERIFIED" and aam.location.version == "acceptedVersion"
    assert "unavailable version of record" in aam.version_difference
    assert all("PDF page" not in p["locator"] for p in aam.paragraphs)
    _, unknown, _, _ = run_acquisition(
        tmp_path / "unknown", {url: (200, full_html(), "text/html", {})}, [location(version="unknown")]
    )
    assert unknown.status == "RIGHTS_OR_VERSION_UNCLEAR" and not unknown.artifact_path


@pytest.mark.parametrize(
    "payload,media",
    [
        (b"%PDF-1.7\nnot an actual PDF", "application/pdf"),
        (b"<html><p>Not a PDF at all.</p></html>", "application/pdf"),
    ],
)
def test_broken_pdf_is_not_validated_or_read(tmp_path, payload, media):
    _, result, _, _ = run_acquisition(tmp_path, {location().url: (200, payload, media, {})})
    assert result.status == "FULL_TEXT_RETRIEVED_NOT_VALIDATED" and not result.artifact_path
    assert not result.content_validated and not result.close_reading_completed


def test_scanned_or_empty_pdf_needs_ocr_review(tmp_path):
    with fitz.open() as doc:
        doc.new_page()
        data = doc.tobytes()
    _, result, _, _ = run_acquisition(tmp_path, {location().url: (200, data, "application/pdf", {})})
    assert result.status == "FULL_TEXT_RETRIEVED_NOT_VALIDATED"
    assert not result.close_reading_completed and not result.artifact_path


def test_user_supplied_access_does_not_grant_processing_rights(tmp_path):
    local = tmp_path / "user-paper.pdf"
    local.write_bytes(readable_pdf())
    _, result, requested, _ = run_acquisition(
        tmp_path / "acquisition",
        {},
        [
            location(
                route="user", local_path=str(local), processing_permission="unclear", terms_checked=False
            )
        ],
    )
    assert result.status == "RIGHTS_OR_VERSION_UNCLEAR" and not result.artifact_path
    assert not requested and "processing rights" in result.attempts[0].reason


def test_authorised_user_scope_can_be_recorded_without_network(tmp_path):
    local = tmp_path / "authorised.pdf"
    local.write_bytes(readable_pdf())
    _, result, requested, _ = run_acquisition(
        tmp_path / "acquisition",
        {},
        [
            location(
                route="user",
                local_path=str(local),
                processing_permission="allowed",
                terms_checked=True,
                permission_evidence="TEST ONLY generated content; user authorises this processing",
            )
        ],
    )
    assert result.status == "USER_SUPPLIED_LAWFUL_TEXT" and not requested
    assert result.location.permission_evidence and not result.close_reading_completed


def test_robots_denial_is_not_circumvented(tmp_path):
    _, result, requested, _ = run_acquisition(tmp_path, {}, robots="User-agent: *\nDisallow: /")
    assert result.status == "PAYWALL_OR_LOGIN_BLOCKED"
    assert requested == ["https://publisher.example.test/robots.txt"]


@pytest.mark.parametrize(
    "url",
    [
        "http://publisher.example.test/paper",
        "https://127.0.0.1/paper",
        "https://192.168.1.1/paper",
        "https://[::1]/paper",
        "https://localhost/paper",
        "https://metadata.google.internal/paper",
        "https://publisher.example.test/paper?token=private",
        "https://user:secret@publisher.example.test/paper",
        "https://publisher.example.test/paper?X-Amz-Signature=private",
    ],
)
def test_private_or_credential_bearing_routes_are_rejected(url):
    with pytest.raises(ValueError):
        safe_url(url)


def test_redirect_cannot_escape_to_private_network(tmp_path):
    _, result, requested, _ = run_acquisition(
        tmp_path, {location().url: (302, b"", "text/html", {"Location": "https://127.0.0.1/private"})}
    )
    assert result.status not in VERIFIED
    assert all("127.0.0.1" not in url for url in requested)


def test_changed_bytes_and_version_invalidate_previous_reading(tmp_path):
    records, *_ = bundle(tmp_path / "corpus")
    old_reading = records[0].reading
    source = work()
    source.reading = old_reading.model_copy(deep=True)
    _, acquired, _, _ = run_acquisition(
        tmp_path / "acquisition", {location().url: (200, full_html(), "text/html", {})}, source=source
    )
    assert any("SOURCE_VERSION_CHANGED" in issue for issue in acquisition_issues(acquired, old_reading))
    Path(acquired.artifact_path).write_bytes(b"changed after retrieval")
    assert any("changed or missing" in issue for issue in acquisition_issues(acquired))


def test_oversized_response_stops_without_retaining_artifact(tmp_path):
    _, result, _, _ = run_acquisition(
        tmp_path, {location().url: (200, full_html(), "text/html", {})}, max_bytes=300
    )
    assert result.status == "FULL_TEXT_RETRIEVED_NOT_VALIDATED"
    assert not result.artifact_path


def test_extended_abstract_with_section_keywords_is_not_a_complete_article(tmp_path):
    # Merely mentioning section names inside an abstract must not imitate those sections.
    html = (
        f'<html><head><link rel="license" href="{LICENCE}"></head>'
        f"<h1>{TITLE}</h1><p>Synthetic Fictional</p><h2>Abstract</h2>"
        "<p>Methods, results, discussion and references are keywords in this extended abstract.</p>"
        + "".join(f"<p>{paragraph('abstract', index)}</p>" for index in range(12))
        + "</html>"
    ).encode()
    _, result, _, _ = run_acquisition(tmp_path, {location().url: (200, html, "text/html", {})})
    assert result.status not in VERIFIED
    assert not result.content_validated


def test_actual_jats_preserves_bibliographic_front_matter_and_section_locators(tmp_path):
    sections = "".join(
        f'<sec id="{section.lower()}"><title>{section}</title>'
        + "".join(f"<p>{paragraph(section, index)}</p>" for index in (1, 2))
        + "</sec>"
        for section in ["Introduction", "Methods", "Results", "Discussion"]
    )
    xml = (
        "<article><front><article-meta>"
        f'<article-id pub-id-type="doi">10.5555/test-only-access</article-id><title-group><article-title>{TITLE}</article-title></title-group>'
        '<contrib-group><contrib contrib-type="author"><name><surname>Fictional</surname><given-names>Synthetic</given-names></name></contrib></contrib-group>'
        "<pub-date><year>2024</year></pub-date></article-meta></front>"
        f"<body>{sections}</body><back><ref-list><title>References</title><ref><mixed-citation>{paragraph('References', 1)}</mixed-citation></ref></ref-list></back></article>"
    ).encode()
    _, result, _, _ = run_acquisition(tmp_path, {location().url: (200, xml, "application/xml", {})})
    assert result.status == "OA_FULL_TEXT_VERIFIED"
    assert result.media_type == "application/xml"
    assert any("Methods, paragraph" in row["locator"] for row in result.paragraphs)
    assert "Fictional" in Path(result.extracted_text_path).read_text()


def test_metadata_oa_pointers_do_not_claim_acquisition_or_close_reading(monkeypatch):
    from educational_research.fulltext.providers import discover_locations

    monkeypatch.setenv("UNPAYWALL_EMAIL", "test-only@example.test")
    monkeypatch.delenv("CORE_API_KEY", raising=False)
    source = Source.model_validate({**work().model_dump(), "synthetic": False, "identity": "VERIFIED"})
    urls = []

    class Metadata:
        def get(self, url, params=None, headers=None):
            urls.append(url)
            if "api.crossref.org" in url:
                return {
                    "message": {
                        "DOI": source.doi,
                        "title": [TITLE],
                        "author": [{"family": "Fictional", "given": "Synthetic"}],
                        "issued": {"date-parts": [[2024]]},
                        "type": "journal-article",
                    }
                }
            if "api.openalex.org" in url:
                return {
                    "id": "https://openalex.org/WTEST",
                    "best_oa_location": {
                        "is_oa": True,
                        "pdf_url": "https://repository.example.test/accepted.pdf",
                        "version": "acceptedVersion",
                        "license": "cc-by",
                        "source": {"type": "repository"},
                    },
                }
            if "api.unpaywall.org" in url:
                assert params == {"email": "test-only@example.test"}
                return {
                    "oa_locations": [
                        {
                            "url_for_pdf": "https://publisher.example.test/vor.pdf",
                            "host_type": "publisher",
                            "version": "publishedVersion",
                            "license": "cc-by",
                        }
                    ]
                }
            raise AssertionError("Unexpected provider request")

    locations, logs = discover_locations(source, Metadata())
    assert urls and all("/v2/search" not in url for url in urls)
    assert any(url.startswith("https://api.unpaywall.org/v2/10.5555/") for url in urls)
    assert locations[0].route == "publisher" and locations[0].version == "publishedVersion"
    assert any(loc.route == "repository" and loc.version == "acceptedVersion" for loc in locations)
    assert source.acquisition is None and source.reading is None
    assert any(log["provider"] == "CORE" and log["status"] == "NOT_CHECKED" for log in logs)


def test_cited_related_work_cannot_masquerade_as_document_identity(tmp_path):
    document = full_html().replace(
        ("<h1>" + TITLE + "</h1>").encode(),
        (
            "<h1>TEST ONLY A Different Article About Instruments</h1>"
            "<p>Cited related work: " + TITLE + ". Fictional 2024.</p>"
        ).encode(),
    )
    _, result, _, _ = run_acquisition(tmp_path, {location().url: (200, document, "text/html", {})})
    assert result.status not in VERIFIED
    assert not result.content_validated
