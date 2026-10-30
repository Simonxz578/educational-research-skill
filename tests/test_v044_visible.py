"""Visible, legally scoped original text: requested A-H regressions (TEST ONLY)."""

import pytest
from educational_research.core.reading import reader_scope
from educational_research.core.visible import excerpts, count_display
from educational_research.core.evidence_depth import english_words
from .v3_factory import bundle
from .test_v043_evidence import abstract_work


def licensed(work):
    reader_scope(work)
    rights = work.abstract_evidence.rights if work.abstract_evidence else work.reading.document.rights
    rights.public_quotation = "allowed"
    rights.public_word_allowance = 150
    rights.quotation_basis = "Generated CC0 TEST ONLY fixture permission"
    return work


@pytest.mark.parametrize("count", [12, 15])
def test_a_b_private_inspection_and_ai_prose_do_not_fill_pdf_quota(tmp_path, count):
    source = licensed(bundle(tmp_path)[0][0])
    quotes = excerpts(source)
    q = quotes[0]
    from educational_research.core.visible import take

    q.text = take(q.text, count)
    audit = count_display(source, [q], "“" + q.text + "” " + "AI explanation " * 200)
    assert audit["shown"] == count and audit["status"] == "PROVISIONAL"


def test_c_one_hundred_actually_printed_original_words_pass(tmp_path):
    source = licensed(bundle(tmp_path)[0][0])
    quotes = excerpts(source)
    printed = " ".join("“" + q.text + "”" for q in quotes)
    audit = count_display(source, quotes, printed)
    assert audit["shown"] == 100 and audit["status"] == "PASS"
    assert count_display(source, quotes, "AI prose only")["shown"] == 0


@pytest.mark.parametrize("defect", ["fabricated", "foreign", "version", "overlap", "translated"])
def test_d_h_invalid_and_repeated_passages_cannot_inflate_pdf_words(tmp_path, defect):
    source = licensed(bundle(tmp_path)[0][0])
    quotes = excerpts(source)
    if defect in ("fabricated", "translated"):
        quotes[0].text = "This invented wording was never written in this source."
    elif defect == "foreign":
        quotes[0].evidence_id = "OTHER:claim"
    elif defect == "version":
        quotes[0].locator = "Unverified different version"
    else:
        quotes.append(quotes[0].model_copy())
    audit = count_display(source, quotes, " ".join("“" + q.text + "”" for q in quotes))
    assert audit["status"] != "PASS" and audit["issues"]
    assert audit["shown"] <= 100


@pytest.mark.parametrize("length,expected", [(85, "PROVISIONAL"), (120, "PASS")])
def test_e_f_actual_abstract_length_and_rights_do_not_grant_fulltext_credit(tmp_path, length, expected):
    source = bundle(tmp_path / "sources")[0][0]
    abstract_work(source, tmp_path / "abstract", length)
    licensed(source)
    quotes = excerpts(source)
    audit = count_display(source, quotes, " ".join("“" + q.text + "”" for q in quotes))
    assert audit["shown"] == min(length, 100) and audit["status"] == expected
    assert reader_scope(source) == "ABSTRACT_ONLY"


def test_g_protected_source_retains_only_permitted_words(tmp_path):
    source = bundle(tmp_path)[0][0]
    reader_scope(source)
    source.reading.document.rights.public_quotation = "not_checked"
    assert excerpts(source) == []
    assert count_display(source, [])["shown"] == 0
    source.reading.document.rights.public_quotation = "allowed"
    quotes = excerpts(source)
    assert sum(len(english_words(q.text)) for q in quotes) <= 20
    assert count_display(source, quotes)["status"] == "PROVISIONAL"


def test_native_finished_pdf_counts_and_tamper_detection(tmp_path):
    import json
    import fitz
    from educational_research.cli import main
    from educational_research.core.deliverables import validate_delivery, seal_receipt

    source = licensed(bundle(tmp_path / "corpus")[0][0])
    inputs = tmp_path / "sources.json"
    inputs.write_text(json.dumps([source.model_dump()]))
    output = tmp_path / "pack"
    assert (
        main(
            [
                "--topic",
                "library learning",
                "--sources",
                str(inputs),
                "--offline",
                "--output-dir",
                str(output),
            ]
        )
        == 0
    )
    result = validate_delivery(output)
    assert not result["errors"]
    assert result["visible_original_words"][source.id]["shown"] == 100
    view = json.loads((output / "evidence/Reader_View.json").read_text())
    quote = view["papers"][0]["display_excerpts"][0]["text"]
    pdf = output / "Research_Roadmap.pdf"
    with fitz.open(pdf) as doc:
        removed = False
        for page in doc:
            boxes = page.search_for(quote)
            for box in boxes:
                page.add_redact_annot(box, fill=(1, 1, 1))
                removed = True
            if boxes:
                page.apply_redactions()
        assert removed
        changed = output / "changed.pdf"
        doc.save(changed)
    changed.replace(pdf)
    evidence = output / "evidence"
    seal_receipt(evidence, json.loads((evidence / "Execution_Receipt.json").read_text()))
    errors = validate_delivery(output)["errors"]
    assert any("missing from finished PDF" in error for error in errors)
