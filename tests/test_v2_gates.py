"""Negative regression tests: appearance/metadata cannot earn research acceptance."""

import json
import pytest
from pathlib import Path
from educational_research.config import Config
from educational_research.core.gates import evaluate_gates
from educational_research.core.framework import audit_framework
from educational_research.core.design import StudyDesign, Strand, audit_design
from educational_research.core.novelty import challenge
from educational_research.core.discovery import discovery_status
from educational_research.core.graph import construct
from educational_research.core.reading import reading_issues
from educational_research.core.deliverables import validate_delivery
from educational_research.models import Source
from educational_research.cli import main
from scripts.validate_research_pack import validate
from .factories import source
from .v2_factory import bundle


def quality(records, synthesis, observations=(), logs=(), **config):
    return evaluate_gates(
        Config(topic="library learning", **config),
        records,
        synthesis,
        logs,
        observations,
        {"errors": [], "native_cli": True},
    )


def test_t01_zero_eric_logs_and_t02_plans_never_discovery_pass(tmp_path):
    records, syn, observations, logs = bundle(tmp_path)
    assert quality(records, syn, observations, [])["gates"]["G1"]["status"] != "PASS"
    no_scholar = [o for o in observations if o.provider == "ERIC"]
    qa = quality(
        records,
        syn,
        no_scholar,
        logs
        + [
            {
                "status": "SCHOLAR_MANUAL_PLAN_ONLY",
                "url": "https://scholar.google.com/scholar?q=learning",
            }
        ],
    )
    assert qa["gates"]["G1"]["status"] == "PARTIAL" and qa["overall_status"] != "PASS"


def test_t03_metadata_cannot_satisfy_fulltext_or_rendering_acceptance():
    records = [source(i) for i in range(1, 16)]
    for s in records:
        s.quotes = []
        s.access = "ABSTRACT_ONLY"
    qa = quality(records, construct(records))
    assert qa["gates"]["G2"]["counts"]["qualified"] == 0
    assert qa["gates"]["G2"]["status"] == "FAIL"


def test_t04_nine_and_reduced_threshold_fail_t05_ten_traceable_pass_structure(tmp_path):
    records, syn, observations, logs = bundle(tmp_path)
    qa = quality(records, syn, observations, logs)
    assert all(g["status"] == "PASS" for g in qa["gates"].values())
    assert (
        qa["synthetic"] and qa["overall_status"] == "PARTIAL"
    )  # fixtures never certify actual research
    assert quality(records[:9], syn, observations, logs)["gates"]["G2"]["status"] == "FAIL"
    assert (
        quality(records, syn, observations, logs, min_reviewed_fulltexts=9)["gates"]["G2"]["status"]
        == "FAIL"
    )


def test_t06_one_source_unresolved_and_duplicate_work_fail_argument(tmp_path):
    records, syn, obs, logs = bundle(tmp_path)
    syn.claims[0].source_ids = ["S001"]
    qa = quality(records, syn, obs, logs)
    assert qa["gates"]["G3"]["status"] == "FAIL"
    syn.claims[0].source_ids = ["S001", "S002"]
    syn.claims[0].evidence_ids = ["S001:missing"]
    assert quality(records, syn, obs, logs)["gates"]["G3"]["status"] == "FAIL"
    syn.claims[0].evidence_ids = ["S001:claim", "S002:claim"]
    records[0].work_id = records[1].work_id = "same-work"
    assert quality(records, syn, obs, logs)["gates"]["G3"]["status"] == "FAIL"


def test_t07_opposing_evidence_cannot_disappear(tmp_path):
    records, syn, obs, logs = bundle(tmp_path)
    syn.edges = []
    assert "opposing evidence" in quality(records, syn, obs, logs)["gates"]["G3"]["reason"]


def test_t08_closest_work_dissolves_gap(tmp_path):
    records, syn, _, _ = bundle(tmp_path)
    syn.novelty.comparisons[0].already_answers = True
    syn.novelty.surviving_contribution = ""
    assert challenge(syn.novelty, records, True)["verdict"] == "GAP_NOT_SUPPORTED"
    syn.novelty.basis = ["geography_only", "mixed_methods_only"]
    assert challenge(syn.novelty, records, True)["verdict"] == "GAP_NOT_SUPPORTED"


def test_t09_title_rq_measure_drift_with_realistic_feasibility_benchmark(tmp_path):
    records, syn, _, _ = bundle(tmp_path)
    c = syn.framework.constructs[0]
    c.name = "career goal clarity"
    c.distinct_from = ["career aspirations"]
    result = audit_framework(
        syn.framework,
        records,
        syn.claims,
        "From Career Aspirations to Participation: Institutional Barriers in UK Higher Education",
        "How do career aspirations shape participation?",
    )
    assert result["status"] == "FAIL"
    assert any(d["location"] == "title" for d in result["drift"])
    assert any(d["location"] == "rq" for d in result["drift"])


def test_t10_access_capability_participation_are_not_interchangeable(tmp_path):
    records, syn, _, _ = bundle(tmp_path)
    a, b = syn.framework.constructs
    a.name = "formal access"
    b.name = "actual participation"
    a.distinct_from = ["actual participation", "capability"]
    b.distinct_from = ["formal access", "capability"]
    b.operationalisation = a.operationalisation
    result = audit_framework(syn.framework, records, syn.claims)
    assert result["status"] == "FAIL"
    assert any(d["kind"] == "DISTINCT_CONSTRUCTS_CONFLATED" for d in result["drift"])


def test_t11_theoretical_stacking_and_t12_counterfeit_mixed_methods_fail(tmp_path):
    records, syn, _, _ = bundle(tmp_path)
    for lens in syn.framework.candidates:
        lens.selected = True
        lens.used_in = []
    assert audit_framework(syn.framework, records, syn.claims)["status"] == "FAIL"
    study = StudyDesign(
        kind="mixed_methods",
        purpose="Proposed explanatory sequential study",
        qual=Strand(rq="Interview accounts", analysis="Thematic analysis"),
        quan=Strand(analysis="Some descriptive survey numbers"),
    )
    audit = audit_design(study, True, ["K1", "K2"])
    assert audit["status"] == "FAIL"
    assert any("QUAN: missing rq" in i for i in audit["issues"])
    assert any("INTEGRATION" in i for i in audit["issues"])


def test_t13_partial_matrix_and_handwritten_shortcut_fail_g5(tmp_path):
    tmp_path.joinpath("Evidence_Matrix.json").write_text('[{"id":"S001"}]')
    tmp_path.joinpath("Educational_Research_Essentials.pdf").write_text("custom report, not native")
    result = validate_delivery(tmp_path)
    assert result["errors"]
    assert any("Missing native deliverable" in e for e in result["errors"])


def test_t19_doi_identity_does_not_upgrade_reading_and_t20_provider_blocked(tmp_path):
    records, syn, _, _ = bundle(tmp_path)
    row = records[0].model_dump()
    row["identity"] = "VERIFIED"
    row["synthetic"] = False
    row["reading"] = None
    s = Source.model_validate(row)
    assert reading_issues(s)
    qa = quality([s] + records[1:], syn, logs=[{"provider": "ERIC", "status": "ERIC_UNAVAILABLE"}])
    assert qa["gates"]["G1"]["status"] == "BLOCKED"
    assert qa["gates"]["G2"]["status"] == "FAIL"


def test_fragment_and_missing_fulltext_digest_fail(tmp_path):
    records, _, _, _ = bundle(tmp_path)
    s = records[0]
    s.reading.coverage = "fragment"
    assert any("Fragment" in i for i in reading_issues(s))
    s.reading.coverage = "whole_work"
    Path(s.reading.document.local_path).write_text("changed")
    assert any("digest" in i for i in reading_issues(s))


def test_export_artifact_must_match_observed_results(tmp_path):
    _, _, observations, logs = bundle(tmp_path)
    observations[1].results[0]["title"] = "Not in the actual export"
    assert discovery_status(logs, observations)["status"] != "PASS"


def test_strict_native_cli_saves_provisional_diagnostics_and_full_matrix(tmp_path):
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps([source(i).model_dump() for i in range(1, 11)]))
    result = main(
        [
            "--topic",
            "library learning",
            "--offline",
            "--strict-quality-gates",
            "--sources",
            str(sources),
            "--output-dir",
            str(tmp_path / "pack"),
        ]
    )
    assert result == 3
    gates = json.loads((tmp_path / "pack/Research_Quality_Gates.json").read_text())
    assert gates["overall_status"] == "PARTIAL" and gates["gates"]["G5"]["status"] == "PASS"
    assert validate(tmp_path / "pack") == []
    assert validate(tmp_path / "pack", strict=True)
    import fitz

    with fitz.open(tmp_path / "pack/Educational_Research_Essentials.pdf") as pdf:
        assert "PROVISIONAL - NOT FULLY VERIFIED" in pdf[0].get_text()


def test_prospective_protocol_cannot_be_invented_after_observation(tmp_path):
    records, syn, observations, logs = bundle(tmp_path)
    logs[0]["prepared_at"] = "2999-01-01T00:00:00+00:00"
    assert quality(records, syn, observations, logs)["gates"]["G1"]["status"] != "PASS"


def test_editorial_critical_scores_and_no_automatic_endorsement(tmp_path):
    from educational_research.core.editorial import EditorialReview, editorial_audit, DIMENSIONS

    records, syn, obs, logs = bundle(tmp_path)
    qa = quality(records, syn, obs, logs)
    review = EditorialReview(
        reviewer="TEST ONLY reviewer",
        reviewer_kind="agent",
        reviewed_at="2026-10-29",
        scores={
            d: {
                "score": 4,
                "rationale": "TEST ONLY judgement",
                "evidence_ids": ["S001:claim"],
                "remaining_judgement": "Not journal acceptance",
            }
            for d in DIMENSIONS
        },
    )
    review.scores["theory_fit"].score = 2
    result = editorial_audit(
        review, qa["gates"], qa["framework_audit"], qa["design_audit"], ["S001:claim"]
    )
    assert result["label"] == "NOT_EDITORIALLY_READY"
    result = editorial_audit(
        None, qa["gates"], qa["framework_audit"], qa["design_audit"], ["S001:claim"]
    )
    assert (
        result["assessment_kind"] == "AUTOMATIC_PROVISIONAL"
        and result["label"] == "NOT_EDITORIALLY_READY"
    )


def test_t16_pdf_inspection_rejects_tiny_type_and_bad_links(tmp_path):
    from reportlab.pdfgen import canvas
    from educational_research.render.inspect import inspect

    path = tmp_path / "bad.pdf"
    c = canvas.Canvas(str(path), pagesize=(595.28, 841.89))
    c.setFont("Times-Roman", 5)
    c.drawString(60, 700, "Unreadable analytical table")
    c.linkURL("broken://missing", (60, 690, 200, 710))
    c.save()
    result = inspect(path)
    assert any("too small" in e for e in result["errors"])
    assert any("hyperlink" in e for e in result["errors"])
    assert any("framework section" in e for e in result["errors"])


def test_attached_file_cannot_justify_fabricated_passage(tmp_path):
    records, _, _, _ = bundle(tmp_path)
    s = records[0]
    next(
        seg for seg in s.segments if seg.id == "result"
    ).text = "A fabricated result absent from the actual artifact"
    assert any("passage absent" in i for i in reading_issues(s))


def test_native_receipt_detects_posthoc_gate_tampering(tmp_path):
    file = tmp_path / "sources.json"
    file.write_text(json.dumps([source().model_dump()]))
    folder = tmp_path / "pack"
    main(
        ["--topic", "library learning", "--offline", "--sources", str(file), "--output-dir", str(folder)]
    )
    gates = json.loads((folder / "Research_Quality_Gates.json").read_text())
    gates["overall_status"] = "PASS"
    for value in gates["gates"].values():
        value["status"] = "PASS"
    (folder / "Research_Quality_Gates.json").write_text(json.dumps(gates))
    issues = validate(folder)
    assert any("changed after native validation" in i or "not supported" in i for i in issues)


def test_complete_synthetic_cli_validates_all_five_structural_gates(tmp_path):
    from educational_research.core.protocol import provisional

    protocol = provisional(Config(topic="library learning"))
    records, syn, obs, _ = bundle(tmp_path / "corpus")
    inputs = {
        "sources": [s.model_dump() for s in records],
        "synthesis": syn.model_dump(),
        "discovery-records": [o.model_dump() for o in obs],
        "protocol": protocol.model_dump(),
    }
    args = ["--topic", "library learning", "--offline", "--output-dir", str(tmp_path / "pack")]
    for key, value in inputs.items():
        file = tmp_path / (key + ".json")
        file.write_text(json.dumps(value))
        args += ["--" + key, str(file)]
    assert main(args) == 0
    qa = json.loads((tmp_path / "pack/Research_Quality_Gates.json").read_text())
    assert all(g["status"] == "PASS" for g in qa["gates"].values())
    assert qa["overall_status"] == "PARTIAL" and qa["synthetic"]
    assert validate(tmp_path / "pack") == []


def test_schema_cannot_mark_incomplete_gates_as_overall_pass(tmp_path):
    from educational_research.core.gates import QualityGates
    from pydantic import ValidationError

    records, syn, _, _ = bundle(tmp_path)
    qa = quality(records, syn)
    qa["overall_status"] = "PASS"
    with pytest.raises(ValidationError, match="Overall PASS"):
        QualityGates.model_validate(qa)


def test_valid_mixed_method_plan_needs_no_equal_sample_size_rule(tmp_path):
    records, syn, _, _ = bundle(tmp_path)
    plan = StudyDesign(
        kind="mixed_methods",
        purpose="Proposed routines/outcomes comparison",
        quan=Strand(
            rq="How do routine and outcome measures covary?",
            purpose="Estimate an association",
            estimand="Conditional association, not causal effect",
            outcome="Observed task outcome",
            measures={"K1": "reported routine scale", "K2": "observed task record"},
            sampling_frame="Proposed eligible users and non-users",
            sampling_logic="Probability sampling conditional on access",
            data_sources=["Proposed survey and permitted records"],
            analysis="Descriptives and appropriately specified association model",
            sample_rationale="Precision rationale pending event-rate/access pilot, not arbitrary N",
            missingness_bias="Audit selection, missingness and construct validity",
        ),
        qual=Strand(
            rq="How do learners explain discrepancies between reports and outcomes?",
            purpose="Explain mechanisms",
            sampling_logic="Purposive discrepant and negative cases",
            data_sources=["Proposed interviews and documents"],
            analysis="Framework-linked comparative coding",
            reflexivity="Researcher position log",
            negative_cases="Search disconfirming accounts",
            audit_trail="Version coding decisions",
        ),
        integration={
            "rq": "How do accounts explain patterns?",
            "design": "explanatory sequential",
            "timing": "QUAN then QUAL",
            "connection": "Select discrepant cases from QUAN",
            "joint_display": "Measures and explanations side by side",
            "discordance": "Retain conflicting cases",
            "meta_inference": "Qualified mechanism interpretation",
            "weighting": "QUAN descriptive breadth; QUAL explanation, different samples",
        },
        construct_ids=["K1", "K2"],
        ethics_consent="Seek approval and informed consent",
        storage="Private access-controlled storage",
        recruitment="Recruit users and non-users if feasible",
        requires_non_users=True,
        non_user_comparison="Invite non-users with consent",
        go_conditions=["Access and sufficient precision feasibility established"],
        no_go_conditions=["Records/recruitment unavailable"],
        fallback="Narrow to a qualitative case study with appropriate claims",
    )
    assert audit_design(plan, True, ["K1", "K2"])["status"] == "PASS"


def test_visual_review_is_versioned_and_does_not_upgrade_research(tmp_path):
    from scripts.record_visual_review import record

    file = tmp_path / "sources.json"
    file.write_text(json.dumps([source().model_dump()]))
    folder = tmp_path / "pack"
    args = [
        "--topic",
        "library learning",
        "--offline",
        "--sources",
        str(file),
        "--output-dir",
        str(folder),
    ]
    main(args)
    image = next((folder / "previews").glob("*.png"))
    record(
        folder,
        [image],
        "TEST ONLY recorded reviewer",
        "needs_revision",
        "Synthetic bookkeeping test, not an actual visual judgement",
    )
    assert validate(folder) == []
    qa = json.loads((folder / "Research_Quality_Gates.json").read_text())
    assert qa["overall_status"] == "PARTIAL"
    main(args)
    assert not (folder / "Visual_Review.json").exists()
    assert list(folder.glob("Visual_Review.previous.*.json"))
