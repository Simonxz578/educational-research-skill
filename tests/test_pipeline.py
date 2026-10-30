import json
import httpx
import pytest
import fitz
from educational_research.config import Config
from educational_research.pipeline import run
from educational_research.utils.cache import Client
from scripts.validate_research_pack import validate
from .factories import source


@pytest.mark.parametrize("count", [10, 100])
def test_full_compact_pack_load(tmp_path, count):
    path = tmp_path / "sources.json"
    path.write_text(json.dumps([source(i).model_dump() for i in range(1, count + 1)]))
    output = tmp_path / "pack"
    audit = run(
        Config(
            presentation="evidence-pack",
            topic="library learning",
            target_words=count * 100,
            offline=True,
        ),
        output,
        path,
    )
    assert audit["passed"] and audit["included"] == count
    assert audit["reference_shortfall"] == 0
    assert len(list(output.glob("*.pdf"))) == 1
    assert not (output / "Draft_Manuscript.md").exists()
    assert validate(output) == []
    ledger = json.loads((output / "evidence_ledger.json").read_text())
    assert all("text" not in seg for row in ledger for seg in row["segments"])
    with fitz.open(output / "Educational_Research_Essentials.pdf") as pdf:
        text = "\n".join(p.get_text() for p in pdf)
        assert "TEST ONLY" in text
        assert all(f"S{i:03}" in text for i in range(1, count + 1))
        assert audit["pdf"]["minimum_font_size"] >= 8
        assert any("Original excerpts" in p.get_text() for p in pdf)
        assert len(pdf) < 2 * count + 15


def test_live_failure_usable_honest_output(tmp_path):
    client = Client(
        tmp_path / "cache",
        transport=httpx.MockTransport(lambda r: httpx.Response(503)),
        sleep=lambda _: None,
    )
    audit = run(
        Config(presentation="evidence-pack", topic="library learning"),
        tmp_path / "pack",
        providers={"eric"},
        client=client,
    )
    assert audit["included"] == 0 and audit["reference_shortfall"] == 10
    logs = json.loads((tmp_path / "pack/search_log.json").read_text())
    assert not any(e["status"] == "ERIC_SEARCHED" for e in logs)
    assert any(e["status"] == "GOOGLE_SCHOLAR_NOT_CHECKED" for e in logs)


def test_explicit_draft_and_overlong_content(tmp_path):
    path = tmp_path / "source.json"
    path.write_text(json.dumps([source().model_dump()]))
    run(
        Config(presentation="evidence-pack", topic="library", offline=True, mode="draft"),
        tmp_path / "explicit",
        path,
        include_draft=True,
    )
    assert (tmp_path / "explicit/Draft_Manuscript.md").exists()
    data = source().model_dump()
    data["summary"] = " ".join(["word"] * 121)
    data["extractions"]["summary"]["text"] = data["summary"]
    path.write_text(json.dumps([data]))
    with pytest.raises(ValueError, match="compact limit"):
        run(Config(presentation="evidence-pack", topic="library", offline=True), tmp_path / "long", path)


def test_pdf_ingestion_and_cjk_rendering(tmp_path):
    from educational_research.ingest.pdf_reader import read_pdf

    path = tmp_path / "source.json"
    s = source()
    s.title = "TEST ONLY 图书馆学习"
    path.write_text(json.dumps([s.model_dump()]))
    result = run(
        Config(presentation="evidence-pack", topic="library learning", offline=True),
        tmp_path / "pack",
        path,
    )
    assert result["passed"]
    segments = read_pdf(tmp_path / "pack/Educational_Research_Essentials.pdf")
    assert segments[0].pdf_page == 1 and segments[0].printed_page is None
    assert "Educational Research" in segments[0].text
    assert segments[0].url.startswith("urn:sha256:")


def test_reviewed_synthesis_keeps_debate_and_gap_uncertainty(tmp_path):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    result = run(
        Config(presentation="evidence-pack", topic="library learning", offline=True),
        tmp_path / "pack",
        root / "tests/fixtures/verified_fixture.json",
        root / "examples/synthesis.synthetic.json",
    )
    graph = json.loads((tmp_path / "pack/argument_graph.json").read_text())
    gaps = json.loads((tmp_path / "pack/gap_evidence.json").read_text())
    assert any(e["kind"] == "contradicts" for e in graph["edges"])
    assert len(graph["claims"]) == 3
    assert all(v["sources"] >= 2 for v in result["claim_coverage"].values())
    assert gaps[0]["confidence"] == "speculative"
