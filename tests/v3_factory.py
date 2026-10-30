"""TEST ONLY primary-text-led v3 fixtures, generated under ignored output directories."""

from educational_research.models import Source
from .v2_factory import bundle as v2_bundle


def bundle(folder, count=10):
    records, synthesis, observations, logs = v2_bundle(folder, count)
    revised = []
    for n, s in enumerate(records, 1):
        row = s.model_dump()
        row["schema_version"] = "3.0"
        row["reading"]["quote_policy"] = "short_excerpts_permitted"
        texts = {e["id"]: e["text"] for e in row["segments"]}
        statements = {
            "claim": (
                "The illustrative authors distinguish accounts of study routines from independently documented outcomes; their argument concerns the kind of evidence needed for each construct.",
                "A routine account is evidence about experience, not direct evidence of attainment.",
            ),
            "method": (
                "Their synthetic design separates an account-based survey from a hypothetical task observation, allowing comparison between what learners describe and what a task records.",
                "Different instruments represent different constructs and should not be treated as interchangeable measures.",
            ),
            "result": (
                "The worked example shows a measurement boundary: reported regularity alone does not establish an observed learning change. It reports no actual population estimate or tested effect.",
                "An apparent correspondence would still need independent checks and an appropriate inference boundary.",
            ),
            "limitation": (
                "The example contains no real participants or findings. Selection, recall and contextual opportunity remain rival explanations that an actual study would need to examine.",
                "The stated limitations prohibit generalising the illustration as an educational intervention result.",
            ),
            "counterpoint": (
                "A contextual opportunity account could explain differences attributed to routines; the example keeps this rival explanation visible rather than treating distinct accounts as consensus.",
                "A negative case would refine the proposed explanation instead of being discarded.",
            ),
        }
        for e in row["reading"]["evidence"]:
            kind = e["content_type"]
            segment = texts[kind]
            # Verbatim spans are private anchors, never automatically reproduced in the reader.
            e["exact_span"] = segment.split(". ", 1)[1].split(". ")[0].rstrip(".") + "."
            e["paraphrase"] = statements[kind][0]
            e["context"] = (
                "TEST ONLY: read in the context of the complete synthetic section, not as an empirical result."
            )
            e["author_warrant"] = statements[kind][1]
            e["researcher_inference"] = (
                "Use separate measures for reported routines and observed outcomes, and test contextual rivals before making an effectiveness claim."
            )
        row["quotes"] = [
            {"text": "reported routine cannot establish an observed outcome", "segment_id": "result"},
            {"text": "no generalisability", "segment_id": "limitation"},
        ]
        # Exact casing/span follows the fixture's original text; no wording is invented.
        for q in row["quotes"]:
            assert q["text"] in texts[q["segment_id"]]
        row["quote_budget"] = 20
        revised.append(Source.model_validate(row))
    chain_texts = [
        (
            "TEST ONLY: Reported routines and observed learning outcomes warrant different kinds of claims.",
            "Both sources distinguish accounts from observations; the second also limits what a reported routine can establish.",
            "A measure of experience cannot alone establish an independently observed outcome.",
            "Separate the constructs before comparing their proposed relationship.",
            "After defining the constructs, examine explanations that could produce an apparent relationship.",
        ),
        (
            "TEST ONLY: Contextual opportunity is a plausible rival to an explanation centred only on learner routines.",
            "The authors retain opportunity and selection as alternatives; neither synthetic source establishes which mechanism operates.",
            "Different mechanisms may be compatible with the same reported pattern.",
            "Compare rival explanations and seek negative cases rather than assuming a routine caused an outcome.",
            "The rival accounts determine what the proposed design must be able to distinguish.",
        ),
        (
            "TEST ONLY: A proposed design needs separate measures and disconfirming cases to connect the argument to evidence.",
            "One source separates instruments; the other cautions that a correspondence would still need inference and context checks.",
            "Construct distinctions require matching observation and interpretation strategies.",
            "Use distinct measures or codes, then test the limits of the proposed explanation.",
            "Carry the qualified claims into a parsimonious framework and a feasible investigation.",
        ),
    ]
    for claim, (text, comparison, warrant, inference, transition) in zip(synthesis.claims, chain_texts):
        claim.text = text
        claim.comparison = comparison
        claim.warrant = warrant
        claim.own_inference = inference
        claim.transition_warrant = transition
        claim.author_positions = {
            sid: (
                "The illustrative authors distinguish accounts and observations."
                if i == 0
                else "The illustrative authors also preserve inference limits and contextual rivals."
            )
            for i, sid in enumerate(claim.source_ids)
        }
    synthesis.edges[0].kind = "qualifies"
    synthesis.edges[
        0
    ].rationale = "TEST ONLY: the contextual rival limits a routine-centred interpretation without claiming an empirical contradiction."
    return revised, synthesis, observations, logs
