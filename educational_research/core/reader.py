"""Derived, source-linked reader view; no invented prose or abstract promotion."""

from pydantic import Field
from ..models_base import Record
from .reading import reading_issues, reader_scope
from .evidence_depth import primary_depth_audit, quotation_usage, reader_extra_texts, english_words
from .verification import verbatim_audit
from .evidence_types import TextLayer

SECTIONS = [
    "RESEARCH LOGIC",
    "ORIGINAL AUTHOR EVIDENCE",
    "ARGUMENT INTEGRATION + CLOSEST-STUDY CHALLENGE",
    "THEORETICAL / CONCEPTUAL FRAMEWORK + ROADMAP",
    "APA 7 REFERENCES",
]


class ReaderStatement(Record):
    text: str
    evidence_ids: list[str]
    locators: list[str]


class ReaderQuote(Record):
    omitted_after: bool = False
    text: str
    evidence_id: str
    locator: str
    url: str


class ReaderWork(Record):
    display_excerpts: list[ReaderQuote] = Field(default_factory=list)
    original_words_shown: int = 0
    display_status: str = "PROVISIONAL"
    display_reason: str = "Not checked"
    evidence_status: str = "FULL_TEXT"
    verified_original_words: int = 0
    explanation_words: int = 0
    interpretation_words: int = 0
    inspection_gate: str = "FULL_TEXT_INSPECTION"
    layers: list[TextLayer] = Field(default_factory=list)
    primary_evidence_words: int
    primary_evidence_shortfall: int
    primary_evidence_issues: list[str]
    source_id: str
    title: str
    in_text: str
    doi: str | None
    url: str
    debate_id: str
    argument_ids: list[str]
    source_author_position: ReaderStatement
    source_reasoning_and_results: list[ReaderStatement]
    source_limitations: ReaderStatement
    our_inference: ReaderStatement
    original_microquotes: list[ReaderQuote]
    quotation_units: int
    quotation_budget: int
    permission: str
    evidence_kind: str


class ReaderView(Record):
    schema_version: str = "4.4"
    sections: list[str] = Field(default_factory=lambda: list(SECTIONS), min_length=5, max_length=5)
    title: str
    problem: str
    principal_question: str
    thesis: str
    selected_source_ids: list[str]
    papers: list[ReaderWork]
    chains: list[dict] = Field(default_factory=list)
    novelty: dict
    framework: dict | None
    source_selection: dict
    coverage: dict
    withheld_claims: list[str] = Field(default_factory=list)


def build_reader(config, protocol, sources, synthesis, selection, qa):
    from ..citations.format import in_text

    papers = []
    known = {s.id for s in sources}
    for source in sources:
        if reader_scope(source) == "ABSTRACT_ONLY":
            from ..fulltext.abstracts import abstract_explanation
            from ..models import quotation_units

            a = source.abstract_evidence
            eid = f"{source.id}:published_abstract"
            explanation = abstract_explanation(a)

            def linked(value):
                return ReaderStatement(text=value, evidence_ids=[eid], locators=["Published abstract"])

            quotes = (
                [
                    ReaderQuote(
                        text=a.quotation, evidence_id=eid, locator=a.quotation_locator, url=a.source_url
                    )
                ]
                if a.quotation
                else []
            )
            used = (
                quotation_units(a.quotation)
                * (
                    1
                    + (
                        explanation
                        + " "
                        + a.interpretation
                        + " ".join(reader_extra_texts(source, synthesis))
                    ).count(a.quotation)
                )
                if a.quotation
                else 0
            )
            if used > source.quote_budget:
                raise ValueError(f"{source.id}: abstract cumulative quotation budget exceeded")
            papers.append(
                ReaderWork(
                    source_id=source.id,
                    title=source.title,
                    in_text=in_text(source),
                    doi=source.doi,
                    url=source.url or a.source_url,
                    debate_id=source.cluster,
                    argument_ids=[c.id for c in synthesis.claims if source.id in c.source_ids],
                    source_author_position=linked(explanation),
                    source_reasoning_and_results=[],
                    source_limitations=linked(
                        "The published abstract does not establish unreported full-text details."
                    ),
                    our_inference=linked(a.interpretation),
                    original_microquotes=quotes,
                    quotation_units=used,
                    quotation_budget=source.quote_budget,
                    permission=a.rights.public_quotation,
                    evidence_kind="published abstract",
                    evidence_status="ABSTRACT_ONLY",
                    primary_evidence_words=len(english_words(a.text)),
                    primary_evidence_shortfall=0,
                    primary_evidence_issues=[],
                    verified_original_words=0,
                    explanation_words=len(english_words(explanation)),
                    interpretation_words=len(english_words(a.interpretation)),
                    inspection_gate="NOT_APPLICABLE_TO_ABSTRACT / NOT_FULL_TEXT_VERIFIED",
                    layers=[
                        TextLayer(
                            kind="VERBATIM_PRIMARY_TEXT",
                            text=a.text,
                            word_count=len(english_words(a.text)),
                            evidence_ids=[eid],
                            scope="ABSTRACT_ONLY",
                        ),
                        TextLayer(
                            kind="SOURCE_ANCHORED_EXPLANATION",
                            text=explanation,
                            word_count=len(english_words(explanation)),
                            evidence_ids=[eid],
                            scope="ABSTRACT_ONLY",
                        ),
                        TextLayer(
                            kind="OUR_INTERPRETATION",
                            text=a.interpretation,
                            word_count=len(english_words(a.interpretation)),
                            evidence_ids=[eid],
                            scope="ABSTRACT_ONLY",
                        ),
                    ],
                )
            )
            continue
        issues = reading_issues(source, reader_ready=True, require_depth=False)
        if issues:
            raise ValueError(f"{source.id}: reader promotion blocked: " + "; ".join(issues))
        used = quotation_usage(source, reader_extra_texts(source, synthesis))
        if used > source.quote_budget:
            raise ValueError(
                f"{source.id}: cumulative reader quotation budget exceeded; revise the repeated source fragments before rendering"
            )
        anchors = source.reading.evidence
        inspection = verbatim_audit(source)

        def anchor(kinds):
            return next(e for e in anchors if e.content_type in kinds)

        def statement(entry, text=None):
            return ReaderStatement(
                text=text or entry.paraphrase, evidence_ids=[entry.evidence_id], locators=[entry.locator]
            )

        claim = anchor({"claim", "definition"})
        method = anchor({"method", "mechanism"})
        result = anchor({"result", "reasoning"})
        limit = anchor({"limitation", "boundary", "counterpoint"})
        quotes = []
        for quote in source.quotes:
            segment = next(s for s in source.segments if s.id == quote.segment_id)
            quotes.append(
                ReaderQuote(
                    text=quote.text,
                    evidence_id=f"{source.id}:{segment.id}",
                    locator=segment.locator,
                    url=segment.url,
                )
            )
        papers.append(
            ReaderWork(
                primary_evidence_words=inspection["verified_original_words"],
                primary_evidence_shortfall=inspection["original_word_shortfall"],
                primary_evidence_issues=inspection["issues"]
                + primary_depth_audit(source.reading, source.quotes)["issues"],
                verified_original_words=inspection["verified_original_words"],
                explanation_words=primary_depth_audit(source.reading, source.quotes)[
                    "explanation_words"
                ],
                interpretation_words=len(english_words(claim.researcher_inference)),
                layers=[
                    TextLayer(
                        kind="VERBATIM_PRIMARY_TEXT",
                        text=span["exact_text"],
                        word_count=len(english_words(span["exact_text"])),
                        evidence_ids=[span["evidence_id"]],
                    )
                    for span in inspection["spans"]
                ]
                + [
                    TextLayer(
                        kind="SOURCE_ANCHORED_EXPLANATION",
                        text=e.paraphrase,
                        word_count=len(english_words(e.paraphrase)),
                        evidence_ids=[e.evidence_id],
                    )
                    for e in [claim, method, result, limit]
                ]
                + [
                    TextLayer(
                        kind="OUR_INTERPRETATION",
                        text=claim.researcher_inference,
                        word_count=len(english_words(claim.researcher_inference)),
                        evidence_ids=[claim.evidence_id],
                    )
                ],
                source_id=source.id,
                title=source.title,
                in_text=in_text(source),
                doi=source.doi,
                url=source.url,
                debate_id=source.cluster,
                argument_ids=[c.id for c in synthesis.claims if source.id in c.source_ids],
                source_author_position=statement(claim),
                source_reasoning_and_results=[statement(method), statement(result)],
                source_limitations=statement(limit),
                our_inference=statement(claim, claim.researcher_inference),
                original_microquotes=quotes,
                quotation_units=used,
                quotation_budget=min(source.quote_budget, 20)
                if not source.permissive_licence_url
                else source.quote_budget,
                permission=source.reading.quote_policy,
                evidence_kind=source.evidence_kind,
            )
        )
    from .visible import project
    for source, paper in zip(sources, papers):
        project(source, paper)
    from .reading import evidence_registry

    registry = set(evidence_registry(sources))
    chains = []
    withheld = []
    for c in synthesis.claims:
        if (
            len(set(c.source_ids)) >= 2
            and set(c.source_ids) <= known
            and c.evidence_ids
            and set(c.evidence_ids) <= registry
            and c.comparison
            and c.own_inference
            and (
                c.evidence_scope == "PRELIMINARY_ABSTRACT"
                or all(reader_scope(s) == "FULL_TEXT" for s in sources if s.id in c.source_ids)
            )
        ):
            chains.append(c.model_dump())
        else:
            withheld.append(c.id)
    return ReaderView(
        title=config.topic,
        problem=protocol.problem,
        principal_question=config.rq or protocol.focal_rq,
        thesis=synthesis.thesis if chains else "A source-grounded thesis is not yet established.",
        selected_source_ids=[s.id for s in sources],
        papers=papers,
        chains=chains,
        novelty=qa["novelty_audit"],
        framework=synthesis.framework.model_dump()
        if synthesis.framework
        and qa["framework_audit"]["status"] == "PASS"
        and all(
            sid in {row["source_id"] for row in qa["reading_audit"] if row["qualified"]}
            for lens in synthesis.framework.candidates
            if lens.selected
            for sid in lens.source_ids
        )
        else None,
        source_selection=selection.model_dump(),
        coverage={
            "scholar": "TEST ONLY fixture; not searched"
            if qa["synthetic"]
            else "observed"
            if qa["gates"]["G1"]["counts"].get("scholar")
            else "not checked",
            "discovery_status": qa["gates"]["G1"]["status"],
            "synthetic": qa["synthetic"],
            "full_text_verified_K": selection.full_text_verified_K,
            "abstract_only_A": selection.abstract_only_A,
            "included_N": len(sources),
        },
        withheld_claims=withheld,
    )


def alignment_map(config, protocol, synthesis):
    framework = synthesis.framework
    if not framework:
        return {"by_construct": {}, "by_stage": {}, "status": "NOT_ESTABLISHED"}
    by_construct = {}
    stages = {}
    for c in framework.constructs:
        row = {
            "title": config.topic,
            "problem": protocol.problem,
            "rq_ids": c.rq_ids,
            "source_evidence_ids": c.evidence_ids,
            "claim_ids": c.claim_ids,
            "gap": synthesis.novelty.surviving_contribution if synthesis.novelty else "not established",
            "theory_ids": c.lens_ids,
            "definition": c.definition,
            "measure_or_code": c.operationalisation,
            "analysis": c.analysis_use,
            "interpretation": [
                claim.own_inference for claim in synthesis.claims if claim.id in c.claim_ids
            ],
            "proposed_contribution": framework.modest_contribution,
            "uses": [u.model_dump() for u in framework.uses if u.construct_id == c.id],
        }
        by_construct[c.id] = row
        for stage in row:
            stages.setdefault(stage, []).append(c.id)
    return {
        "by_construct": by_construct,
        "by_stage": stages,
        "status": "SOURCE_LINKED_STRUCTURAL_MAP",
        "notice": "Semantic congruence requires close reading and expert review",
    }
