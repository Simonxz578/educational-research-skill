import pytest
from pydantic import ValidationError
from educational_research.config import Config
from educational_research.models import Source, Author, Metric, Assessment
from educational_research.core.screen import deduplicate
from educational_research.core.score import score, rank, select_diverse
from educational_research.core.quality import warnings, audit_draft
from educational_research.core.gaps import evaluate
from educational_research.core.graph import Synthesis, Claim, validate_graph
from educational_research.search.crossref import doi, verify
from educational_research.citations.format import bibliography
from educational_research.citations.audit import audit
from .factories import source


def test_quota_not_prose():
    assert Config(target_words=1000).quota == 10
    assert Config(target_words=10000).quota == 100
    assert Config(target_words=10000, target_references=7).quota == 7


def test_wrong_quote_locator_budget_and_access_rejected():
    data = source().model_dump()
    data["quotes"][0]["text"] = "Invented quotation"
    with pytest.raises(ValidationError, match="exact source span"):
        Source(**data)
    data = source().model_dump()
    data["segments"][0]["locator"] = "location unknown"
    with pytest.raises(ValidationError, match="locator"):
        Source(**data)
    data = source().model_dump()
    data["access"] = "ABSTRACT_ONLY"
    with pytest.raises(ValidationError, match="abstract/metadata"):
        Source(**data)
    data = source().model_dump()
    data["quote_budget"] = 3
    with pytest.raises(ValidationError, match="budget"):
        Source(**data)


def test_extraction_layers_and_scientific_overclaim():
    data = source().model_dump()
    data["extractions"]["target_argument"]["basis"] = "source-author claim"
    with pytest.raises(ValidationError):
        Source(**data)
    s = source()
    s.target_argument = "This causes improved attainment"
    assert any("OVERCLAIM" in w for w in warnings(s))
    assert audit_draft("This proves the first ever causal result.", [s])


def test_doi_and_dedup_identity():
    assert doi("https://doi.org/10.1234/ABC") == "10.1234/abc"
    assert doi("madeup") is None
    a, b = source(), source(2)
    a.doi, b.doi = "10.1234/ABC", "10.1234/abc"
    assert len(deduplicate([a, b])[0]) == 1
    b.doi = "10.1234/different"
    assert len(deduplicate([a, b])[0]) == 2


def metadata(s):
    return {
        "DOI": "10.1234/synthetic",
        "title": [s.title],
        "author": [{"family": a.family, "given": a.given} for a in s.authors],
        "published-print": {"date-parts": [[2024]]},
        "published-online": {"date-parts": [[2023]]},
        "container-title": ["Synthetic Journal"],
        "type": "journal-article",
    }


def test_metadata_conflicts_not_silently_overwritten():
    s = source()
    s.synthetic, s.identity, s.year = False, "UNVERIFIED", 1999
    result = verify(s, metadata(s))
    assert result.identity == "CONFLICT"
    assert result.year == 1999
    s = source()
    s.synthetic, s.identity, s.year = False, "UNVERIFIED", 2023
    assert verify(s, metadata(s)).identity == "CONFLICT"
    s = source()
    s.synthetic, s.identity = False, "UNVERIFIED"
    m = metadata(s)
    m["title"] = ["Entirely different work"]
    assert verify(s, m).identity == "CONFLICT"


def test_metric_context_and_missingness():
    with pytest.raises(ValidationError):
        Metric(name="JIF", value=4, source="https://example.test/jcr", checked_at="2026-10-29")
    s = source()
    result = score(s, "library learning")
    assert result["available_weight"] == 75
    assert result["journal_influence_score"] is None
    assert result["article_impact_score"] is None
    assert result["total_priority_score"] == round((42.75 + 12 + 8) / 75 * 100, 2)
    assert "journal_influence" in result["metric_missingness"]


def test_relevance_beats_prestige_and_critical_work_retained():
    a, b = source(), source(2)
    a.assessments["relevance"].value = 90
    b.assessments["relevance"].value = 20
    b.metrics = [
        Metric(
            name="JIF",
            value=100,
            source="https://example.test/jcr",
            year=2024,
            category="synthetic",
            checked_at="2026-10-29",
        )
    ]
    b.assessments["journal_influence"] = Assessment(
        value=100, rationale="fictional", checked_at="2026-10-29"
    )
    assert rank([b, a], "library")[0] == a
    b.role = "counterargument"
    assert b in select_diverse([a, b], 1)


def test_gap_and_graph_boundaries():
    s = source()
    assert (
        evaluate([{"missing_dimension": "no studies exist"}], [s], [])[0]["confidence"] == "speculative"
    )
    graph = Synthesis(claims=[Claim(id="C001", text="Proposed claim", source_ids=["MISSING"])])
    with pytest.raises(ValueError, match="unknown source"):
        validate_graph(graph, [s])
    graph = Synthesis(
        claims=[
            Claim(id="C001", text="a", depends_on=["C002"]),
            Claim(id="C002", text="b", depends_on=["C001"]),
        ]
    )
    with pytest.raises(ValueError, match="cycle"):
        validate_graph(graph, [])


def test_actual_apa_csl_twenty_one_authors_and_italics():
    s = source()
    s.authors = [Author(family=f"Writer{i:02}", given="Avery") for i in range(1, 22)]
    s.doi = "10.1234/synthetic"
    refs = bibliography([s])
    assert refs[0][0] == s.id
    formatted = refs[0][1]
    assert "Writer19" in formatted and "Writer20" not in formatted and "Writer21" in formatted
    assert "…" in formatted or "..." in formatted
    assert "<i>" in formatted
    assert "https://doi.org/10.1234/synthetic" in formatted


def test_bidirectional_citation_audit():
    s = source()
    report = audit("Claim (Fictional001, 2024). Unknown S999.", [s])
    assert report["uncited_references"] == []
    assert report["unresolved_citations"] == ["S999"]
    assert audit("Claim (Fictional001, 2023).", [s])["unresolved_citations"]


def test_cjk_budget_and_invalid_doi():
    from educational_research.models import quotation_units

    assert quotation_units("学习者报告学习习惯变化") > 1
    data = source().model_dump()
    data["doi"] = "not-a-real-doi"
    with pytest.raises(ValidationError, match="DOI syntax"):
        Source(**data)


def test_conflicting_same_doi_not_false_merge():
    a, b = source(), source(2)
    a.doi = b.doi = "10.1234/duplicate"
    b.title = "An unrelated title entirely"
    unique, excluded = deduplicate([a, b])
    assert len(unique) == 2 and not excluded
    assert all(s.identity == "CONFLICT" for s in unique)


def test_claim_cannot_borrow_unattributed_evidence():
    a, b = source(), source(2)
    graph = Synthesis(
        claims=[Claim(id="C001", text="Claim", source_ids=[a.id], evidence_ids=[b.id + ":body"])]
    )
    with pytest.raises(ValueError, match="attributed sources"):
        validate_graph(graph, [a, b])


def test_bibliography_order_and_organisation_book():
    a, b = source(), source(2)
    a.authors = [Author(literal="Zeta Organisation")]
    b.authors = [Author(literal="Alpha Organisation")]
    b.type = "book"
    b.publisher = "TEST ONLY Fictional Press"
    refs = bibliography([a, b])
    assert [sid for sid, _ in refs] == [b.id, a.id]
    assert "Alpha Organisation" in refs[0][1]
    assert "<i>" in refs[0][1] and "Fictional Press" in refs[0][1]
