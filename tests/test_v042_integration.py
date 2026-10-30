"""Close migration and route-integration bypasses; all records remain TEST ONLY."""

from educational_research.config import Config
from educational_research.core.reading import reading_issues
from educational_research.core.gates import evaluate_gates
from educational_research.fulltext.providers import discover_locations
from tests.v3_factory import bundle
from tests.v2_factory import bundle as old_bundle
from tests.factories import source


def test_non_synthetic_roadmap_cannot_skip_acquisition(tmp_path):
    records, *_ = bundle(tmp_path)
    work = records[0].model_copy(deep=True)
    work.synthetic, work.identity = False, "VERIFIED"
    assert any(
        "requires validated acquisition" in issue for issue in reading_issues(work, reader_ready=True)
    )


def test_strict_legacy_layout_cannot_bypass_new_evidence_quality(tmp_path):
    records, synthesis, observations, logs = old_bundle(tmp_path)
    qa = evaluate_gates(
        Config(presentation="evidence-pack", strict_quality_gates=True),
        records,
        synthesis,
        logs,
        observations,
    )
    assert qa["gates"]["G2"]["status"] == "FAIL"
    assert qa["gates"]["G2"]["counts"]["qualified"] == 0


def test_eric_document_without_doi_never_calls_openalex():
    work = source(1)
    work.synthetic, work.identity, work.doi = False, "UNVERIFIED", None
    work.eric_id = "ED999999"
    work.provenance = [{"provider": "ERIC", "raw_metadata": {"e_fulltextauth": True}}]

    class Metadata:
        def get(self, *args, **kwargs):
            raise AssertionError("No DOI-based metadata request should be made")

    locations, _ = discover_locations(work, Metadata())
    assert any(
        loc.url == "https://files.eric.ed.gov/fulltext/ED999999.pdf" and loc.route == "eric"
        for loc in locations
    )
    assert work.acquisition is None and work.reading is None
