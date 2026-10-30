"""TEST ONLY adversarial author-text inspection and honest abstract fallback regressions."""

from pathlib import Path

import pytest

from educational_research.core.evidence_depth import english_words, evidence_anchors
from educational_research.core.reading import reading_issues, sha256_file
from .v3_factory import bundle


def inspect(source):
    from educational_research.core.verification import verbatim_audit

    return verbatim_audit(source)


def four_anchors(source):
    source.reading.evidence = evidence_anchors(source.reading)
    source.quotes = []
    source.reading.quote_policy = "no_reproduction"
    return source.reading.evidence


def exact_original_count(source, count):
    """Use real independently labelled fixture passages, never explanation text as evidence."""
    assert count in {99, 100}
    anchors = four_anchors(source)
    paragraphs = ["TEST ONLY generated source. " + source.title]
    for n, entry in enumerate(anchors):
        length = 24 if count == 99 and n == 3 else 25
        original = " ".join(english_words(entry.exact_span)[:length])
        entry.exact_span = original
        segment = next(s for s in source.segments if source.id + ":" + s.id == entry.evidence_id)
        segment.text = original
        paragraphs += [entry.locator, original]
    path = Path(source.reading.document.local_path)
    path.write_text("\n\n".join(paragraphs))
    source.reading.document.sha256 = sha256_file(path)
    return source


def test_t1_long_ai_explanations_cannot_create_any_author_words(tmp_path):
    sources, *_ = bundle(tmp_path)
    source = sources[0]
    for entry in four_anchors(source):
        entry.exact_span = ""
        entry.paraphrase += (
            " A proposed independent interpretation is not the author's original wording." * 20
        )
    audit = inspect(source)
    assert audit["verified_original_words"] == 0
    assert audit["original_word_shortfall"] == 100
    assert audit["issues"]


def test_t2_short_verified_fragments_plus_commentary_do_not_meet_inspection_floor(tmp_path):
    sources, *_ = bundle(tmp_path)
    source = sources[0]
    for entry in four_anchors(source):
        # Each short fragment really occurs, but the actual inspected total stays far below 100.
        entry.exact_span = " ".join(entry.exact_span.split()[5:12])
        entry.paraphrase += " Our wider interpretation needs independent scholarly assessment." * 20
    audit = inspect(source)
    assert 0 < audit["verified_original_words"] < 100
    assert audit["original_word_shortfall"] > 0
    assert audit["issues"]


@pytest.mark.parametrize("count", [99, 100])
def test_t3_author_word_floor_uses_each_sources_actual_matched_spans(tmp_path, count):
    sources, *_ = bundle(tmp_path)
    source = exact_original_count(sources[0], count)
    audit = inspect(source)
    assert audit["verified_original_words"] == count
    assert audit["original_word_shortfall"] == 100 - count
    assert bool(audit["issues"]) is (count == 99)


def test_t3_real_original_inspection_does_not_require_another_hundred_ai_words(tmp_path):
    sources, *_ = bundle(tmp_path)
    source = sources[0]
    replacements = [
        "The synthetic authors distinguish reported study routines from observed learning outcomes.",
        "Their fictional survey and separate hypothetical task observations illustrate different evidence types.",
        "A reported routine cannot establish observed learning outcomes; the finding is illustrative.",
        "Recall, selection and measurement differences prevent generalising these synthetic illustrations.",
    ]
    for entry, wording in zip(four_anchors(source), replacements):
        entry.paraphrase = wording
    assert sum(len(english_words(e.paraphrase)) for e in source.reading.evidence) < 100
    audit = inspect(source)
    assert audit["verified_original_words"] >= 100 and audit["issues"] == []
    assert not reading_issues(source, reader_ready=True)


@pytest.mark.parametrize("defect", ["source_id", "evidence_source", "absent_span", "digest"])
def test_t4_mismatched_or_invented_primary_evidence_fails(tmp_path, defect):
    sources, *_ = bundle(tmp_path)
    source = sources[0]
    four_anchors(source)
    if defect == "source_id":
        source.reading.source_id = sources[1].id
    elif defect == "evidence_source":
        source.reading.evidence[0].evidence_id = sources[1].id + ":claim"
    elif defect == "absent_span":
        source.reading.evidence[
            0
        ].exact_span = "This is an invented author sentence absent from the archived work."
    else:
        source.reading.document.sha256 = "0" * 64
    assert inspect(source)["issues"]


def test_t5_duplicated_passages_cannot_be_counted_under_four_role_labels(tmp_path):
    sources, *_ = bundle(tmp_path)
    source = sources[0]
    anchors = four_anchors(source)
    for entry in anchors[1:]:
        entry.exact_span = anchors[0].exact_span
    audit = inspect(source)
    assert audit["verified_original_words"] < 100
    assert audit["issues"]


def test_t5_overlapping_passages_do_not_inflate_original_words(tmp_path):
    sources, *_ = bundle(tmp_path)
    source = sources[0]
    anchors = four_anchors(source)
    original = " ".join(english_words(" ".join(e.exact_span for e in anchors))[:95])
    words = original.split()
    for n, entry in enumerate(anchors):
        entry.exact_span = " ".join(words[n * 20 : n * 20 + 25])
        segment = next(s for s in source.segments if source.id + ":" + s.id == entry.evidence_id)
        segment.text = entry.exact_span
    path = Path(source.reading.document.local_path)
    path.write_text("TEST ONLY overlapping-fragment adversary\n\n" + original)
    source.reading.document.sha256 = sha256_file(path)
    audit = inspect(source)
    assert audit["verified_original_words"] <= 85
    assert audit["issues"]


def test_t5_foreign_paper_passage_is_not_source_one_author_text(tmp_path):
    sources, *_ = bundle(tmp_path)
    first, second = sources[:2]
    anchors = four_anchors(first)
    anchors[0].exact_span = second.reading.evidence[0].exact_span
    assert inspect(first)["issues"]


def test_unicode_and_whitespace_normalisation_does_not_invent_words(tmp_path):
    sources, *_ = bundle(tmp_path)
    source = sources[0]
    anchors = four_anchors(source)
    expected = inspect(source)["verified_original_words"]
    # Actual document and logical spans differ only in ordinary Unicode/space presentation.
    path = Path(source.reading.document.local_path)
    path.write_text(path.read_text().replace(" ", "\u00a0"))
    source.reading.document.sha256 = sha256_file(path)
    audit = inspect(source)
    assert audit["verified_original_words"] == expected
    assert audit["issues"] == []
    anchors[0].exact_span += " fabricated"
    assert inspect(source)["issues"]


# All abstract records below are generated TEST ONLY; no authentic research is asserted.
def abstract_work(source, folder, words=95, quote_allowed=False):
    from educational_research.fulltext.abstracts import retain_abstract
    from educational_research.core.evidence_types import EvidenceRights

    source.reading = None
    source.quotes = []
    source.access = "ABSTRACT_ONLY"
    text = (
        "TEST ONLY. This published abstract describes interviews about library learning routines. "
        "Participants were invited to discuss the questions in a bounded educational setting. "
        "The abstract specifies the interview method and contextual scope without reporting results. "
    )
    text = " ".join((text * 10).split()[:words])
    rights = EvidenceRights(
        access="allowed",
        processing="allowed",
        private_retention="allowed",
        public_quotation="allowed" if quote_allowed else "not_checked",
        access_basis="Generated TEST ONLY abstract",
        processing_basis="Generated fixture",
        retention_basis="Generated fixture",
        quotation_basis="CC0 synthetic fixture" if quote_allowed else "",
    )
    evidence = retain_abstract(
        source,
        folder,
        text,
        "user_attested",
        source.url,
        rights,
        explanation="The indexed abstract describes interviews about library learning routines. It does not report a result.",
        explanation_checked=True,
    )
    if quote_allowed:
        evidence.quotation = "interviews about library learning routines"
    return source


@pytest.mark.parametrize("length", [95, 130])
def test_t7_t8_published_abstract_is_included_without_any_fulltext_credit(tmp_path, length):
    from educational_research.core.selection import select_sources
    from educational_research.config import Config
    from educational_research.fulltext.abstracts import abstract_issues

    sources, *_ = bundle(tmp_path / "sources")
    work = abstract_work(sources[0], tmp_path / "abstract", length)
    assert abstract_issues(work) == []
    chosen, candidates, selection = select_sources([work], Config(target_references=1))
    assert len(chosen) == 1 and not candidates
    assert selection.abstract_only_A == 1 and selection.full_text_verified_K == 0
    audit = inspect(work)
    assert audit["scope"] == "ABSTRACT_ONLY" and audit["original_word_shortfall"] is None
    assert "NOT_APPLICABLE" in audit["gate_status"]


def test_t9_unverified_abstract_string_does_not_promote_metadata(tmp_path):
    from educational_research.core.selection import select_sources
    from educational_research.config import Config

    sources, *_ = bundle(tmp_path)
    work = sources[0]
    work.reading = None
    work.quotes = []
    work.access = "METADATA_ONLY"
    work.abstract = "An unverified assertion of an abstract is not a source artifact."
    chosen, candidates, selection = select_sources([work], Config())
    assert not chosen and len(candidates) == 1 and selection.included_N == 0


def test_t10_missing_abstract_results_stay_missing_in_the_reader(tmp_path):
    from educational_research.core.reader import build_reader
    from educational_research.core.protocol import provisional
    from educational_research.core.selection import select_sources
    from educational_research.core.gates import evaluate_gates
    from educational_research.config import Config

    sources, syn, obs, logs = bundle(tmp_path / "sources")
    work = abstract_work(sources[0], tmp_path / "abstract")
    config = Config(topic="library learning")
    selected, _, selection = select_sources([work], config)
    qa = evaluate_gates(config, selected, syn, logs, obs)
    view = build_reader(config, provisional(config), selected, syn, selection, qa)
    paper = view.papers[0]
    assert paper.evidence_status == "ABSTRACT_ONLY" and paper.source_reasoning_and_results == []
    assert paper.original_microquotes == [] and paper.verified_original_words == 0
    assert "does not report a result" in paper.source_author_position.text
    assert [x.kind for x in paper.layers] == [
        "VERBATIM_PRIMARY_TEXT",
        "SOURCE_ANCHORED_EXPLANATION",
        "OUR_INTERPRETATION",
    ]
    assert qa["gates"]["G2"]["status"] == "FAIL" and qa["gates"]["G4"]["status"] != "PASS"


def test_t12_thirteen_full_seven_abstracts_are_twenty_items_and_references(tmp_path):
    import json
    import fitz
    from educational_research.cli import main
    from educational_research.config import Config
    from educational_research.core.protocol import provisional
    from scripts.validate_research_pack import validate

    folder = tmp_path / "pack"
    inputs = folder / "evidence/inputs"
    inputs.mkdir(parents=True)
    sources, syn, obs, _ = bundle(inputs / "corpus", 20)
    for source in sources[13:]:
        abstract_work(source, inputs / "abstracts", 130)
    args = [
        "--topic",
        "library learning",
        "--target-references",
        "20",
        "--offline",
        "--strict-quality-gates",
        "--output-dir",
        str(folder),
    ]
    for flag, value in [
        ("sources", [s.model_dump() for s in sources]),
        ("synthesis", syn.model_dump()),
        ("protocol", provisional(Config(topic="library learning", target_references=20)).model_dump()),
        ("discovery-records", [o.model_dump() for o in obs]),
    ]:
        path = inputs / (flag + ".json")
        path.write_text(json.dumps(value))
        args += ["--" + flag, str(path)]
    assert main(args) == 3
    selection = json.loads((folder / "evidence/Source_Selection.json").read_text())
    assert (
        selection["included_N"],
        selection["full_text_verified_K"],
        selection["abstract_only_A"],
        selection["shortfall"],
    ) == (20, 13, 7, 7)
    refs = json.loads((folder / "evidence/verified_references.csl.json").read_text())
    assert len(refs) == 20
    assert validate(folder) == []
    assert validate(folder, strict=True)
    with fitz.open(folder / "Research_Roadmap.pdf") as pdf:
        text = " ".join(page.get_text() for page in pdf)
        assert "13 FULL TEXTS, 7 ABSTRACTS" in text
        assert "ABSTRACT ONLY" in text and "FULL TEXT" in text
        for source in sources:
            assert "[" + source.id + "]" in text


def test_t13_t14_abstract_quotation_is_matched_and_requires_its_own_permission(tmp_path):
    from educational_research.fulltext.abstracts import abstract_issues

    sources, *_ = bundle(tmp_path / "sources")
    work = abstract_work(sources[0], tmp_path / "abstract", quote_allowed=True)
    assert abstract_issues(work) == []
    work.abstract_evidence.rights.public_quotation = "not_checked"
    assert abstract_issues(work)
    work.abstract_evidence.rights.public_quotation = "allowed"
    work.abstract_evidence.quotation = "An invented sentence absent from the original abstract"
    assert abstract_issues(work)


def test_t6_blocked_fulltext_automatically_falls_back_to_exact_indexed_abstract(tmp_path):
    import httpx
    from educational_research.models import Source
    from educational_research.core.access import FullTextLocation
    from educational_research.fulltext.acquire import Acquirer
    from educational_research.fulltext.abstracts import acquire_abstract, abstract_issues
    from educational_research.core.selection import select_sources
    from educational_research.config import Config

    work = Source(
        id="TEST1",
        title="TEST ONLY interviews about library learning",
        doi="10.5555/fixture",
        identity="VERIFIED",
        url="https://publisher.example.test/login",
    )

    def respond(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(403)

    class Metadata:
        def get(self, *args, **kwargs):
            return {
                "message": {
                    "DOI": work.doi,
                    "title": [work.title],
                    "author": [{"family": "Fictional"}],
                    "issued": {"date-parts": [[2024]]},
                    "abstract": "<jats:p>TEST ONLY. We conducted interviews about library learning. This abstract reports a method but no result.</jats:p>",
                }
            }

    acquirer = Acquirer(tmp_path / "full", transport=httpx.MockTransport(respond), sleep=lambda _: None)
    try:
        acquired = acquirer.acquire(work, [FullTextLocation(url=work.url, route="publisher")])
        assert acquired.status == "PAYWALL_OR_LOGIN_BLOCKED"
        abstract = acquire_abstract(work, tmp_path / "abstracts", Metadata(), acquirer)
        assert abstract and abstract_issues(work) == [] and "conducted interviews" in abstract.text
        chosen, _, selection = select_sources([work], Config())
        assert (
            len(chosen) == 1 and selection.abstract_only_A == 1 and selection.full_text_verified_K == 0
        )
    finally:
        acquirer.close()


def test_t16_fresh_topic_and_twenty_work_request_needs_no_history_or_manual_upload(
    tmp_path, monkeypatch
):
    import httpx
    from educational_research.utils.cache import Client
    from educational_research.fulltext.acquire import Acquirer
    from educational_research.cli import main
    import educational_research.pipeline as pipeline
    import educational_research.fulltext.acquire as access
    import json
    import re

    monkeypatch.chdir(tmp_path)
    for key in ["CORE_API_KEY", "UNPAYWALL_EMAIL", "OPENALEX_API_KEY"]:
        monkeypatch.delenv(key, raising=False)

    def respond(request):
        if request.url.host == "api.ies.ed.gov":
            query = request.url.params.get("search", "")
            offset = 10 if "theory" in query else 0
            start = int(request.url.params.get("start", 0))
            rows = int(request.url.params.get("rows", 10))
            docs = [
                {
                    "id": f"EJ{n:06}",
                    "title": f"TEST ONLY library learning interviews {n:02}",
                    "author": ["Fictional, Author"],
                    "publicationdateyear": "2024",
                    "description": f"TEST ONLY published abstract {n}: We conducted interviews about library learning. No full study is available in this fixture.",
                }
                for n in range(offset + start + 1, min(offset + start + rows + 1, offset + 11))
            ]
            return httpx.Response(200, json={"response": {"numFound": 10, "docs": docs}})
        if request.url.host == "api.crossref.org":
            title = request.url.params.get("query.bibliographic", "")
            found = re.search(r"(\d+)$", title) if title else re.search(r"(\d+)$", request.url.path)
            n = int(found.group(1)) if found else 1
            record = {
                "DOI": f"10.5555/test-{n}",
                "title": [f"TEST ONLY library learning interviews {n:02}"],
                "author": [{"family": "Fictional", "given": "Author"}],
                "issued": {"date-parts": [[2024]]},
                "type": "journal-article",
                "abstract": f"<p>TEST ONLY published abstract {n}: We conducted interviews about library learning. No result is reported here.</p>",
            }
            return httpx.Response(
                200, json={"message": {"items": [record]}} if title else {"message": record}
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(respond)
    monkeypatch.setattr(
        pipeline,
        "Client",
        lambda folder, offline=False: Client(
            folder, offline=offline, transport=transport, sleep=lambda _: None
        ),
    )
    monkeypatch.setattr(
        access,
        "Acquirer",
        lambda folder, metadata_client=None: Acquirer(
            folder, metadata_client=metadata_client, transport=transport, sleep=lambda _: None
        ),
    )
    assert main(["--topic", "library learning", "--target-references", "20"]) == 0
    selection = json.loads((tmp_path / "outputs/research/evidence/Source_Selection.json").read_text())
    assert selection["included_N"] == 20 and selection["abstract_only_A"] == 20
    assert selection["full_text_verified_K"] == 0 and selection["shortfall"] == 20
    assert (tmp_path / "outputs/research/Research_Roadmap.pdf").is_file()


def test_t13_t14_fulltext_inspection_never_grants_extended_reproduction(tmp_path):
    from educational_research.core.evidence_types import EvidenceRights

    sources, *_ = bundle(tmp_path)
    work = sources[0]
    work.quote_budget = 40
    work.permissive_licence_url = "https://creativecommons.org/licenses/by/4.0/"
    work.reading.document.licence = "ordinary protected article; no extended permission"
    work.reading.document.rights = EvidenceRights(
        access="allowed",
        processing="allowed",
        private_retention="allowed",
        public_quotation="allowed",
        access_basis="TEST ONLY authorised access",
        processing_basis="TEST ONLY permission",
        retention_basis="TEST ONLY permission",
        quotation_basis="Short quotation only",
    )
    assert inspect(work)["verified_original_words"] >= 100
    assert any(
        "Extended public reproduction" in issue for issue in reading_issues(work, reader_ready=True)
    )
    work.reading.document.licence = "CC BY 4.0, independently verified TEST ONLY fixture licence"
    work.reading.document.rights.quotation_basis = (
        "Generated fixture; CC BY licence and attribution recorded"
    )
    assert not any(
        "Extended public reproduction" in issue for issue in reading_issues(work, reader_ready=True)
    )


def test_t11_abstract_comparison_is_only_visible_as_explicitly_preliminary(tmp_path):
    from educational_research.core.reader import build_reader
    from educational_research.core.protocol import provisional
    from educational_research.core.selection import select_sources
    from educational_research.core.gates import evaluate_gates
    from educational_research.config import Config

    sources, syn, obs, logs = bundle(tmp_path / "corpus")
    for s in sources:
        abstract_work(s, tmp_path / "abstracts")
    syn.claims = syn.claims[:1]
    claim = syn.claims[0]
    claim.evidence_ids = [s + ":published_abstract" for s in claim.source_ids]
    cfg = Config(topic="library learning")
    selected, _, selection = select_sources(sources, cfg)
    qa = evaluate_gates(cfg, selected, syn, logs, obs)
    assert qa["gates"]["G2"]["status"] == "FAIL" and qa["gates"]["G4"]["status"] != "PASS"
    view = build_reader(cfg, provisional(cfg), selected, syn, selection, qa)
    assert not view.chains
    claim.evidence_scope = "PRELIMINARY_ABSTRACT"
    view = build_reader(cfg, provisional(cfg), selected, syn, selection, qa)
    assert len(view.chains) == 1 and view.chains[0]["evidence_scope"] == "PRELIMINARY_ABSTRACT"


def test_title_and_reference_spans_do_not_count_as_original_argument(tmp_path):
    sources, *_ = bundle(tmp_path)
    work = sources[0]
    anchor = four_anchors(work)[0]
    anchor.locator = "References, paragraph 1"
    next(s for s in work.segments if work.id + ":" + s.id == anchor.evidence_id).locator = anchor.locator
    result = inspect(work)
    assert any("reference text" in issue for issue in result["issues"])


def test_essential_abstract_is_not_displaced_merely_to_improve_fulltext_score(tmp_path):
    from educational_research.core.selection import select_sources
    from educational_research.config import Config

    sources, *_ = bundle(tmp_path / "sources")
    landmark = abstract_work(sources[1], tmp_path / "abstract")
    landmark.role = "essential"
    chosen, _, selection = select_sources([sources[0], landmark], Config(target_references=1))
    assert [s.id for s in chosen] == [landmark.id] and selection.abstract_only_A == 1


def test_markup_extraction_does_not_duplicate_published_abstract_words():
    from educational_research.fulltext.abstracts import clean_abstract

    assert (
        clean_abstract("<abstract><p>First real sentence.</p><p>Second real sentence.</p></abstract>")
        == "First real sentence. Second real sentence."
    )


def test_native_html_extraction_does_not_count_nested_cells_twice():
    from educational_research.fulltext.documents import extract

    text, *_ = extract(
        b"<html><h1>TEST ONLY</h1><table><tr><td><p>One authentic passage.</p></td></tr></table></html>",
        "text/html",
    )
    assert text.count("One authentic passage.") == 1
