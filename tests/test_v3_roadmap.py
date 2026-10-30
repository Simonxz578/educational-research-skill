"""Reader-first contract, primary text and end-to-end quota regressions (TEST ONLY)."""

import json
from pathlib import Path
import pytest
import fitz
from educational_research.config import Config
from educational_research.cli import main
from educational_research.core.protocol import provisional
from educational_research.core.selection import select_sources
from educational_research.core.reading import reading_issues
from educational_research.core.gates import evaluate_gates
from educational_research.core.deliverables import validate_delivery, MATRIX_GROUPS
from educational_research.core.reader import ReaderView
from educational_research.render.roadmap import SECTIONS
from scripts.validate_research_pack import validate
from .v3_factory import bundle


def invoke(folder, count=10, read_count=None, semantics="exact", total=None, extra=()):
    folder = Path(folder)
    inputs = folder / "evidence" / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    cfg = Config(topic="library learning", target_references=count, source_semantics=semantics)
    protocol = provisional(cfg)
    records, synthesis, observations, _ = bundle(inputs / "corpus", total or count)
    if read_count is not None:
        for s in records[read_count:]:
            s.quotes = []
            s.reading = None
            s.access = "ABSTRACT_ONLY"
    args = [
        "--topic",
        "library learning",
        "--offline",
        "--target-references",
        str(count),
        "--source-semantics",
        semantics,
        "--output-dir",
        str(folder),
    ]
    for flag, value in [
        ("sources", [s.model_dump() for s in records]),
        ("synthesis", synthesis.model_dump()),
        ("discovery-records", [o.model_dump() for o in observations]),
        ("protocol", protocol.model_dump()),
    ]:
        path = inputs / (flag + ".json")
        path.write_text(json.dumps(value))
        args += ["--" + flag, str(path)]
    status = main(args + list(extra))
    return status, json.loads((folder / "evidence" / "audit.json").read_text())


def test_t01_default_floor_and_t05_explicit_count_precedence():
    assert Config().quota == 10 and Config(target_words=200).quota == 10
    assert Config(target_words=10000).quota == 100
    c = Config(target_words=10000, target_references=20)
    assert c.quota == 20 and c.deep_review_requirement == 20 and c.selection_semantics == "exact"
    assert Config(target_references=5).deep_review_requirement == 10


@pytest.mark.parametrize("count", [10, 20])
def test_t02_t06_t16_t17_t18_native_reader_and_complete_evidence(tmp_path, count):
    status, audit = invoke(tmp_path / "pack", count)
    folder = tmp_path / "pack"
    evidence = folder / "evidence"
    assert status == 0 and audit["included"] == count
    assert audit["research_quality"]["gates"]["G2"]["counts"]["required"] == count
    assert audit["research_quality"]["gates"]["G2"]["status"] == "PASS"
    assert audit["research_quality"]["overall_status"] == "PARTIAL"  # synthetic never authentic research
    assert sorted(p.name for p in folder.glob("*.pdf")) == ["Research_Roadmap.pdf"]
    assert {p.name for p in folder.iterdir()} == {"Research_Roadmap.pdf", "README.md", "evidence"}
    view = ReaderView.model_validate_json((evidence / "Reader_View.json").read_text())
    matrix = json.loads((evidence / "Evidence_Matrix.json").read_text())
    refs = json.loads((evidence / "verified_references.csl.json").read_text())
    assert len(view.papers) == len(refs) == len(matrix) == count
    assert all(set(fields) <= row.keys() for row in matrix for fields in MATRIX_GROUPS.values())
    assert validate(folder) == []
    assert validate_delivery(folder)["errors"] == []
    with fitz.open(folder / "Research_Roadmap.pdf") as pdf:
        text = " ".join(p.get_text() for p in pdf)
        assert all(f"[{s.source_id}]" in text for s in view.papers)
        assert "Research Quality Gates" not in text and "relevance_score" not in text
        assert "APA 7 REFERENCES" in text and "TEST ONLY" in text
        assert len(pdf) <= (10 if count == 10 else 16)
        assert audit["pdf"]["errors"] == []
        assert "Test" not in " ".join(audit["pdf"]["fonts"])
        for page in pdf:
            for section in SECTIONS:
                if section in page.get_text():
                    assert len(page.get_text().split(section)[-1].split()) > 10
            spans = [
                s
                for b in page.get_text("dict")["blocks"]
                if "lines" in b
                for line in b["lines"]
                for s in line["spans"]
            ]
            assert all(s["color"] == 0 for s in spans)
            assert all("Times" in s["font"] or "LiberationSerif" in s["font"] for s in spans)
            assert all(s["size"] >= 9.5 for s in spans if 55 < s["bbox"][1] < 790)
            assert all(s["bbox"][0] >= 56.2 and s["bbox"][2] <= 539.1 for s in spans)
            assert not page.get_images()
        # A final single-reference orphan must not create a huge blank page.
        last = [
            s
            for b in pdf[-1].get_text("dict")["blocks"]
            if "lines" in b
            for line in b["lines"]
            for s in line["spans"]
            if 55 < s["bbox"][1] < 790
        ]
        assert max(s["bbox"][3] for s in last) > 400


def test_t03_twenty_target_ten_readings_has_exact_shortfall(tmp_path):
    status, audit = invoke(tmp_path / "pack", 20, read_count=10, extra=["--strict-quality-gates"])
    assert status == 3 and audit["included"] == 10
    selection = audit["source_selection"]
    gate = audit["research_quality"]["gates"]["G2"]
    assert selection["qualified_deep_read_K"] == 10 and selection["shortfall"] == 10
    assert gate["counts"]["required"] == 20 and gate["counts"]["shortfall"] == 10
    assert gate["status"] == "FAIL"
    candidates = json.loads((tmp_path / "pack/evidence/Candidates.json").read_text())
    assert len(candidates) == 10
    with fitz.open(tmp_path / "pack/Research_Roadmap.pdf") as pdf:
        assert "SOURCE SHORTFALL" in pdf[0].get_text()
        assert "10 selected of 20 target" in " ".join(p.get_text() for p in pdf)
    assert validate(tmp_path / "pack") == []


@pytest.mark.parametrize(
    "semantics,target,total,expected",
    [("exact", 12, 20, 12), ("at_least", 12, 20, 20), ("exact", 25, 30, 25)],
)
def test_t04_exact_at_least_and_twenty_five(tmp_path, semantics, target, total, expected):
    records, *_ = bundle(tmp_path, total)
    config = Config(target_references=target, source_semantics=semantics)
    chosen, _, selection = select_sources(records, config)
    assert len(chosen) == expected and selection.deep_review_requirement_N == target
    assert selection.shortfall == 0


def test_default_is_not_hidden_ten_source_cap(tmp_path):
    records, *_ = bundle(tmp_path, 20)
    chosen, _, selection = select_sources(records, Config())
    assert len(chosen) == 20 and selection.requested_user_N is None


def test_t07_quote_budget_t08_exact_span_and_t10_anchor_independence(tmp_path):
    records, *_ = bundle(tmp_path)
    source = records[0]
    assert not reading_issues(source, reader_ready=True)
    assert sum(len(q.text.split()) for q in source.quotes) <= 20
    source.reading.evidence[0].exact_span = "Invented words not in the primary source"
    assert any("exact" in i or "anchor" in i for i in reading_issues(source, reader_ready=True))
    records, *_ = bundle(tmp_path / "again")
    s = records[0]
    for e in s.reading.evidence:
        e.exact_span = s.reading.evidence[0].exact_span
        e.paraphrase = s.reading.evidence[0].paraphrase
    assert any("Repeated" in i for i in reading_issues(s, reader_ready=True))
    s.quotes.append(s.quotes[0])
    assert any("one or two" in i for i in reading_issues(s, reader_ready=True))


def test_t09_abstract_is_only_candidate_and_t19_missing_discovery(tmp_path):
    records, syn, _, _ = bundle(tmp_path)
    for s in records:
        s.quotes = []
        s.reading = None
        s.access = "ABSTRACT_ONLY"
    chosen, candidates, selection = select_sources(records, Config())
    assert not chosen and len(candidates) == 10 and selection.shortfall == 10
    qa = evaluate_gates(Config(), chosen, syn, [], [], {"errors": [], "native_cli": True})
    assert qa["gates"]["G1"]["status"] == "BLOCKED" and qa["gates"]["G2"]["status"] == "FAIL"


def test_t23_no_unattributed_reader_claim_and_t24_consistent_counters(tmp_path):
    _, audit = invoke(tmp_path / "pack", 10)
    folder = tmp_path / "pack/evidence"
    view = json.loads((folder / "Reader_View.json").read_text())
    sel = json.loads((folder / "Source_Selection.json").read_text())
    assert view["source_selection"] == sel == audit["source_selection"]
    assert sel["quotation_count"] == 20
    qa_text = (folder / "QA_Report.md").read_text()
    assert "selected 10/10; deeply reviewed 10/10; micro-excerpts 20; shortfall 0" in qa_text
    for work in view["papers"]:
        for statement in [
            work["source_author_position"],
            *work["source_reasoning_and_results"],
            work["source_limitations"],
            work["our_inference"],
        ]:
            assert statement["evidence_ids"] and statement["locators"]
    view["papers"][0]["source_author_position"]["text"] = "An unsupported novel claim"
    (folder / "Reader_View.json").write_text(json.dumps(view))
    assert any("wording" in e or "changed after" in e for e in validate_delivery(folder)["errors"])


def test_theoretical_anchors_do_not_invent_empirical_samples(tmp_path):
    records, *_ = bundle(tmp_path)
    s = records[0]
    s.reading.scholarly_kind = "theoretical"
    s.reading.coverage = "relevant_chapter"
    mappings = {
        "claim": "definition",
        "method": "mechanism",
        "result": "reasoning",
        "limitation": "boundary",
    }
    for e in s.reading.evidence:
        e.content_type = mappings.get(e.content_type, e.content_type)
    assert not reading_issues(s, reader_ready=True)


def test_low_relevance_cannot_pad_requested_corpus(tmp_path):
    records, *_ = bundle(tmp_path)
    records[0].assessments["relevance"].value = 10
    chosen, candidates, selection = select_sources(records, Config(target_references=10))
    assert len(chosen) == 9 and selection.shortfall == 1
    assert any("Low assessed relevance" in reason for row in candidates for reason in row["reasons"])


def test_optional_audit_pdf_requires_explicit_request(tmp_path):
    _, audit = invoke(tmp_path / "pack", 10, extra=["--include-audit-pdf"])
    assert (tmp_path / "pack/Research_Roadmap.pdf").exists()
    assert (tmp_path / "pack/evidence/Educational_Research_Essentials.pdf").exists()
    assert validate(tmp_path / "pack") == []


def test_originating_quantity_intent_is_preserved(tmp_path):
    _, audit = invoke(tmp_path / "pack", 10, extra=["--user-quantity-intent", "至少10篇文献"])
    protocol = json.loads((tmp_path / "pack/evidence/search_protocol.json").read_text())
    receipt = json.loads((tmp_path / "pack/evidence/Execution_Receipt.json").read_text())
    assert protocol["quantity_intent"]["originating_user_intent"] == "至少10篇文献"
    assert protocol["amendments"][-1]["previous_quantity_intent"]["originating_user_intent"] is None
    assert receipt["source_selection"]["originating_user_intent"] == "至少10篇文献"
    assert receipt["source_selection"] == audit["source_selection"]
