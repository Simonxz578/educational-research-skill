"""Derived, source-linked reader view; no invented prose or abstract promotion."""

from pydantic import Field
from ..models_base import Record
from ..models import quotation_units
from .reading import reading_issues


class ReaderStatement(Record):
    text: str
    evidence_ids: list[str]
    locators: list[str]


class ReaderQuote(Record):
    text: str
    evidence_id: str
    locator: str
    url: str


class ReaderWork(Record):
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
    schema_version: str = "3.0"
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
        issues = reading_issues(source, reader_ready=True)
        if issues:
            raise ValueError(f"{source.id}: reader promotion blocked: " + "; ".join(issues))
        anchors = source.reading.evidence

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
                quotation_units=sum(quotation_units(q.text) for q in quotes),
                quotation_budget=min(source.quote_budget, 20)
                if not source.permissive_licence_url
                else source.quote_budget,
                permission=source.reading.quote_policy,
                evidence_kind=source.evidence_kind,
            )
        )
    registry = {f"{s.id}:{e.id}" for s in sources for e in s.segments}
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
        if synthesis.framework and qa["framework_audit"]["status"] == "PASS"
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
