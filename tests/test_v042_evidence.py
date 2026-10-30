"""Adversarial v0.4.2 evidence accounting and reader regressions (TEST ONLY)."""

import json
import re

import fitz
import pytest

from educational_research.cli import main
from educational_research.config import Config
from educational_research.core.design import StudyDesign, Strand, audit_design
from educational_research.core.evidence_depth import (
    STOP,
    cross_source_boilerplate,
    english_words,
    evidence_anchors,
    primary_depth_audit,
    quotation_usage,
)
from educational_research.core.framework import audit_framework
from educational_research.core.gates import evaluate_gates
from educational_research.core.novelty import challenge
from educational_research.core.protocol import provisional
from educational_research.core.reader import SECTIONS
from educational_research.core.reading import reading_audit, reading_issues
from educational_research.core.selection import select_sources
from scripts.validate_research_pack import validate
from .v3_factory import bundle


def exact_explanation_length(source, count):
    """Trim fixture paraphrases for an exact accounting boundary; invent no source span."""
    assert count in {99, 100}
    for index, entry in enumerate(evidence_anchors(source.reading)):
        count_here = 24 if count == 99 and index == 3 else 25
        entry.paraphrase = " ".join(english_words(entry.paraphrase)[:count_here]) + "."
    assert primary_depth_audit(source.reading, source.quotes)["primary_evidence_words"] == count


@pytest.mark.parametrize("count,expected_qualified", [(99, 10), (100, 10)])
def test_source_floor_is_individual_and_short_prose_is_retained(tmp_path, count, expected_qualified):
    sources, synthesis, observations, logs = bundle(tmp_path)
    exact_explanation_length(sources[0], count)
    config = Config(topic="library learning", target_references=10)
    selected, candidates, selection = select_sources(sources, config)
    assert len(selected) == 10 and not candidates
    assert selection.qualified_deep_read_K == expected_qualified
    assert selection.shortfall == 10 - expected_qualified
    assert selection.primary_evidence_shortfalls == {}
    qa = evaluate_gates(
        config, selected, synthesis, logs, observations, {"errors": [], "native_cli": True}
    )
    assert qa["gates"]["G2"]["status"] == "PASS"
    # The other nine much longer explanations must not make up the one-source deficit.
    assert qa["gates"]["G2"]["counts"]["qualified"] == expected_qualified


def test_title_inference_locators_and_verbatim_fragments_do_not_fill_primary_floor(tmp_path):
    sources, *_ = bundle(tmp_path)
    s = sources[0]
    exact_explanation_length(s, 99)
    initial = primary_depth_audit(s.reading, s.quotes)
    s.title += " " + "Background context and research relevance. " * 30
    for e in s.reading.evidence:
        e.researcher_inference += " " + "An independent interpretation needs additional evidence. " * 30
        e.locator += " " + "Chapter section page paragraph reference. " * 30
    # Exact quote words inserted into a paraphrase still do not add explanatory words.
    evidence_anchors(s.reading)[0].paraphrase += " " + s.quotes[0].text
    after = primary_depth_audit(s.reading, s.quotes)
    assert after["primary_evidence_words"] == initial["primary_evidence_words"] == 99
    assert after["shortfall"] == 0  # v0.4.3 has no AI-explanation quota


def test_repeated_sentences_and_generic_filler_cannot_satisfy_depth(tmp_path):
    sources, *_ = bundle(tmp_path)
    s = sources[0]
    for e in evidence_anchors(s.reading):
        e.paraphrase = (
            "The synthetic authors distinguish reported study routines from observed learning outcomes. "
            * 10
            + "This study highlights important contributions to the literature."
        )
    result = primary_depth_audit(s.reading, s.quotes)
    assert result["primary_evidence_words"] < 100
    assert any("duplicated" in item for item in result["issues"])
    assert any("filler" in item for item in result["issues"])
    assert reading_issues(s, reader_ready=True)


def test_redundant_words_within_distinct_sentences_do_not_buy_a_pass(tmp_path):
    sources, *_ = bundle(tmp_path)
    s = sources[0]
    for e in evidence_anchors(s.reading):
        grounded = sorted({w.casefold() for w in english_words(e.exact_span)} - STOP)
        e.paraphrase = " ".join(grounded[:3] + [grounded[3]] * 24) + "."
    audit = primary_depth_audit(s.reading, s.quotes)
    assert audit["issues"], "One repeated noun cannot provide 24 useful evidence words"
    assert reading_issues(s, reader_ready=True)


def test_cross_source_boilerplate_is_detected_and_not_counted_as_independent_depth(tmp_path):
    sources, *_ = bundle(tmp_path)
    for first, second in zip(evidence_anchors(sources[0].reading), evidence_anchors(sources[1].reading)):
        second.paraphrase = first.paraphrase
    duplicates = cross_source_boilerplate(sources)
    assert sources[1].id in duplicates[sources[0].id]
    audit = {r["source_id"]: r for r in reading_audit(sources, reader_ready=True)}
    assert not audit[sources[0].id]["qualified"]
    assert not audit[sources[1].id]["qualified"]
    assert any("boilerplate" in issue for issue in audit[sources[0].id]["issues"])


def test_real_quote_repeated_in_argument_uses_the_same_work_budget(tmp_path):
    sources, synthesis, observations, logs = bundle(tmp_path)
    source = sources[0]
    assert quotation_usage(source) <= source.quote_budget
    synthesis.claims[0].comparison += " " + source.quotes[0].text + "."
    assert quotation_usage(source, [synthesis.claims[0].comparison]) > source.quote_budget
    qa = evaluate_gates(
        Config(topic="library learning"),
        sources,
        synthesis,
        logs,
        observations,
        {"errors": [], "native_cli": True},
    )
    assert qa["gates"]["G2"]["status"] == "FAIL", (
        "A repeated microquote in integration is still reproduction from the same work"
    )


def test_closest_work_can_refute_gap_and_remove_false_reader_contribution(tmp_path):
    sources, synthesis, *_ = bundle(tmp_path)
    n = synthesis.novelty
    n.comparisons[0].already_answers = True
    n.proposed_verdict = "GAP_NOT_SUPPORTED"
    n.surviving_contribution = "The old attractive claim must not survive refutation."
    n.revised_question = "Which boundary condition remains untested in the compared contexts?"
    result = challenge(n, sources, discovery_complete=True)
    assert result["verdict"] == "GAP_NOT_SUPPORTED" and result["status"] == "FAIL"
    assert result["surviving_contribution"] == ""
    assert result["revised_question"] == n.revised_question


def test_disconnected_construct_is_not_an_explanatory_framework(tmp_path):
    sources, synthesis, *_ = bundle(tmp_path)
    f = synthesis.framework
    added = f.constructs[0].model_copy(deep=True)
    added.id, added.name = "K_unconnected", "feasible opportunities"
    added.definition = "Options that can be enacted given specified constraints and resources"
    added.distinct_from = []
    f.constructs.append(added)
    result = audit_framework(f, sources, synthesis.claims)
    assert result["status"] == "FAIL"
    assert any("Disconnected" in issue and "K_unconnected" in issue for issue in result["issues"])


def test_required_nonusers_unavailable_forces_design_fallback():
    d = StudyDesign(
        kind="qualitative",
        purpose="Explain participation and informed non-use",
        qual=Strand(
            rq="How are opportunities interpreted?",
            purpose="Interpret accounts",
            sampling_logic="Purposively compare users and non-users",
            data_sources=["Interviews"],
            analysis="Thematic comparison",
            reflexivity="Reflective journal",
            negative_cases="Seek disconfirming accounts",
            audit_trail="Versioned codebook",
        ),
        construct_ids=["K1"],
        ethics_consent="Approval would be sought",
        storage="Private controlled storage",
        recruitment="Permission required",
        non_user_comparison="Compare informed non-users",
        requires_non_users=True,
        non_users_access="unavailable",
        go_conditions=["Permission to contact both groups"],
        no_go_conditions=["No non-user access"],
        fallback="Narrow to an honestly labelled user-only case and revise the question",
    )
    result = audit_design(d, required=True, construct_ids=["K1"])
    assert result["status"] == "FAIL"
    assert any("cannot be recruited" in issue for issue in result["issues"])
    assert result["fallback"] == d.fallback


def test_good_synthetic_fulltext_structure_never_becomes_real_research_pass(tmp_path):
    sources, synthesis, observations, logs = bundle(tmp_path)
    qa = evaluate_gates(
        Config(topic="library learning"),
        sources,
        synthesis,
        logs,
        observations,
        {"errors": [], "native_cli": True},
    )
    assert qa["synthetic"] is True
    assert qa["gates"]["G2"]["status"] == "PASS"
    assert qa["overall_status"] != "PASS"


def test_native_pdf_contains_each_counted_explanation_and_only_five_sections(tmp_path):
    output = tmp_path / "pack"
    inputs = output / "evidence" / "inputs"
    inputs.mkdir(parents=True)
    sources, synthesis, observations, _ = bundle(inputs / "corpus")
    exact_explanation_length(sources[0], 100)
    cfg = Config(topic="library learning", target_references=10)
    args = [
        "--topic",
        "library learning",
        "--target-references",
        "10",
        "--offline",
        "--output-dir",
        str(output),
    ]
    for flag, data in [
        ("sources", [s.model_dump() for s in sources]),
        ("synthesis", synthesis.model_dump()),
        ("protocol", provisional(cfg).model_dump()),
        ("discovery-records", [o.model_dump() for o in observations]),
    ]:
        path = inputs / (flag + ".json")
        path.write_text(json.dumps(data))
        args.extend(["--" + flag, str(path)])
    assert main(args) == 0
    view = json.loads((output / "evidence/Reader_View.json").read_text())
    assert view["sections"] == SECTIONS and len(view["sections"]) == 5
    assert view["papers"][0]["verified_original_words"] >= 100
    assert view["papers"][0]["explanation_words"] == 100
    with fitz.open(output / "Research_Roadmap.pdf") as pdf:
        text = re.sub(r"\s+", " ", " ".join(p.get_text() for p in pdf))
        for entry in evidence_anchors(sources[0].reading):
            assert re.sub(r"\s+", " ", entry.paraphrase) in text
        assert all(section in text for section in SECTIONS)
        for hidden in ["G1:", "G2:", "SHA-256", "search logs", "primary_evidence_words"]:
            assert hidden not in text
    assert validate(output) == []


def test_visible_html_anchors_do_not_require_pdf_conversion(tmp_path):
    from html import escape
    from pathlib import Path
    from educational_research.core.reading import sha256_file

    sources, *_ = bundle(tmp_path / "corpus")
    s = sources[0]
    # Browser-visible wording is unchanged; inline emphasis is normal full HTML.
    body = "".join(
        "<p>"
        + escape(segment.text).replace("reported study routines", "reported <em>study</em> routines")
        + "</p>"
        for segment in s.segments
    )
    document = Path(tmp_path / "lawful-source.html")
    document.write_text("<html><body><article>" + body + "</article></body></html>")
    s.reading.document.local_path = str(document)
    s.reading.document.sha256 = sha256_file(document)
    assert not reading_issues(s, reader_ready=True), (
        "Visible source spans must be matched against extracted HTML text, not markup"
    )
