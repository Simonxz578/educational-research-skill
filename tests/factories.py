"""Entirely synthetic, public-safe records. Never empirical research evidence."""

from educational_research.models import Source, Author, Segment, Quote, Extraction, Assessment


def source(n=1):
    argument = (
        "TEST ONLY: synthetic authors associate library retrieval prompts with reported study routines."
    )
    target = f"TEST ONLY: proposed claim {n} distinguishes perceived study routines from demonstrated learning outcomes."
    text = "TEST ONLY. Learners reported more regular study routines. No observed attainment effect was established. "
    text += argument
    fields = {
        "summary": "TEST ONLY: a fictional library-learning survey illustrates how to distinguish self-reported routines from measured attainment. No empirical findings are asserted.",
        "source_argument": argument,
        "target_argument": target,
    }
    return Source(
        id=f"S{n:03}",
        title=f"TEST ONLY: library learning evidence record {n:03}",
        authors=[Author(family=f"Fictional{n:03}", given="Avery")],
        year=2024,
        journal="TEST ONLY Synthetic Methods Journal",
        volume="1",
        issue="2",
        pages=f"{n}-{n + 1}",
        url=f"https://example.test/library/{n}",
        identity="SYNTHETIC",
        synthetic=True,
        access="USER_SUPPLIED",
        education_level="TEST ONLY adult learners",
        country="fictional context",
        participants="fictional; no real participants",
        design="synthetic survey illustration",
        evidence_kind="self-report",
        objective="TEST ONLY: compare perceived routines and outcome evidence",
        theory="TEST ONLY: retrieval practice as a proposed lens",
        limitations="Synthetic; cannot support scholarly findings",
        evidence_strength="TEST ONLY; not real evidence",
        role="counterargument" if n % 3 == 0 else "empirical support",
        cluster="Routines and outcome evidence",
        relevance_explanation="TEST ONLY: relevant concepts; fictional evidence must never inform real claims",
        relationship="Illustrative tension between perceptions and outcomes",
        segments=[
            Segment(
                id="body",
                text=text,
                url=f"https://example.test/library/{n}",
                locator="Synthetic section 1",
                licence="CC0 synthetic fixture",
            )
        ],
        quotes=[
            Quote(text="Learners reported more regular study routines.", segment_id="body"),
            Quote(text="No observed attainment effect was established.", segment_id="body"),
        ],
        extractions={
            k: Extraction(
                text=v,
                segment_ids=["body"],
                basis="source-author claim"
                if k == "source_argument"
                else "researcher interpretation"
                if k == "target_argument"
                else "source evidence",
            )
            for k, v in fields.items()
        },
        assessments={
            "relevance": Assessment(
                value=95,
                rationale="TEST ONLY: direct fictional conceptual overlap",
                checked_at="2026-10-29",
            ),
            "study_quality": Assessment(
                value=60,
                rationale="TEST ONLY: synthetic survey, perception-only warrant",
                checked_at="2026-10-29",
            ),
            "argument_value": Assessment(
                value=80,
                rationale="TEST ONLY: exposes outcome inference boundary",
                checked_at="2026-10-29",
            ),
        },
        **fields,
    )
