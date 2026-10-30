"""TEST ONLY primary-text-led v3 fixtures, generated under ignored output directories."""

from educational_research.models import Source
from .v2_factory import bundle as v2_bundle


def bundle(folder, count=10):
    records, synthesis, observations, logs = v2_bundle(folder, count)
    revised = []
    for n, s in enumerate(records, 1):
        row = s.model_dump()
        row["schema_version"] = "4.2"
        row["reading"]["quote_policy"] = "short_excerpts_permitted"
        texts = {e["id"]: e["text"] for e in row["segments"]}
        contexts = [
            "urban reading club",
            "rural mathematics workshop",
            "bilingual science class",
            "adult evening seminar",
            "library enquiry group",
            "primary geography lesson",
            "secondary history course",
            "distance writing module",
            "vocational design studio",
            "inclusive music workshop",
            "community language programme",
            "university laboratory class",
            "early numeracy group",
            "peer tutoring seminar",
            "outdoor ecology session",
            "museum learning visit",
            "digital literacy course",
            "apprenticeship workshop",
            "teacher education tutorial",
            "after school chess club",
        ]
        activities = [
            "text rehearsal",
            "number exercises",
            "diagram revision",
            "seminar preparation",
            "catalogue enquiries",
            "map practice",
            "chronology revision",
            "draft review",
            "prototype sketches",
            "rhythm practice",
            "vocabulary revision",
            "laboratory preparation",
            "counting games",
            "tutorial preparation",
            "fieldwork planning",
            "exhibit exploration",
            "software exercises",
            "tool rehearsal",
            "lesson planning",
            "position analysis",
        ]
        outcomes = [
            "delayed word recall",
            "arithmetic accuracy",
            "concept explanation",
            "argument reconstruction",
            "search accuracy",
            "location recall",
            "event sequencing",
            "writing coherence",
            "design accuracy",
            "rhythm recognition",
            "word recognition",
            "procedure accuracy",
            "quantity comparison",
            "explanation accuracy",
            "species recognition",
            "historical recall",
            "task completion",
            "tool selection",
            "teaching decisions",
            "move prediction",
        ]
        contexts += [
            "doctoral research retreat",
            "clinical skills seminar",
            "financial literacy class",
            "agricultural training group",
            "public speaking course",
            "engineering drawing class",
            "civic education workshop",
            "robotics summer school",
            "sports coaching module",
            "culinary arts demonstration",
        ]
        activities += [
            "literature searching",
            "diagnostic rehearsal",
            "budget rehearsal",
            "crop planning",
            "speech rehearsal",
            "drawing exercises",
            "policy discussion",
            "circuit construction",
            "movement rehearsal",
            "recipe planning",
        ]
        outcomes += [
            "citation accuracy",
            "diagnostic accuracy",
            "budget accuracy",
            "crop identification",
            "speech coherence",
            "spatial accuracy",
            "policy reasoning",
            "circuit accuracy",
            "movement accuracy",
            "ingredient selection",
        ]
        context, activity, outcome = (
            contexts[(n - 1) % 30],
            activities[(n - 1) % 30],
            outcomes[(n - 1) % 30],
        )
        statements = {
            "claim": (
                f"For the {context}, the fictional authors distinguish learners' accounts of {activity} from independent {outcome}. Their measurement boundary separates reported study routines from observed learning outcomes.",
                "Reports concern experience rather than independent attainment.",
            ),
            "method": (
                f"The synthetic {context} design pairs a survey about {activity} with separate hypothetical task observations after {n + 2} days. Separate reported routines and task records illustrate evidence types without real data or recruitment.",
                "The two instruments represent different constructs.",
            ),
            "result": (
                f"In the {context} example, an apparent relation between {activity} and {outcome} remains illustrative rather than an observed effect. The authors reason that a reported routine cannot establish an observed outcome, so this invented comparison warrants no statistical or causal conclusion.",
                "An account of regular practice cannot establish independent change.",
            ),
            "limitation": (
                f"The {context} illustration contains no real participants, tested intervention or population finding. Recall, selection and contextual opportunity could alter the relation between {activity} and {outcome}; measurement differences prevent generalisability.",
                "The stated limitations prohibit real population generalisation.",
            ),
            "counterpoint": (
                f"Contextual opportunity in the {context} could explain differences attributed to {activity}; this rival explanation constrains interpretation of {outcome} without inventing contrary empirical results.",
                "A rival explanation requires investigation.",
            ),
        }
        for e in row["reading"]["evidence"]:
            kind = e["content_type"]
            segment = (
                texts[kind]
                + f" The worked context is {context}, with {activity} and {outcome} considered over {n + 2} days."
            )
            texts[kind] = segment
            next(seg for seg in row["segments"] if seg["id"] == kind)["text"] = segment
            e["exact_span"] = segment
            e["paraphrase"] = statements[kind][0]
            e["context"] = "TEST ONLY: complete synthetic section; no real study or data."
            e["author_warrant"] = statements[kind][1]
            e["researcher_inference"] = (
                f"Use separate measures for {activity} and {outcome}, then test contextual rivals before making an effectiveness claim."
            )
            e["qualification"] = (
                f"The {context} worked example is synthetic and supports no empirical generalisation."
            )
        from pathlib import Path
        from educational_research.core.reading import sha256_file

        document = Path(row["reading"]["document"]["local_path"])
        document.write_text("\n\n".join(seg["text"] for seg in row["segments"]))
        row["reading"]["document"].update(
            sha256=sha256_file(document),
            processing_permission="allowed",
            permission_evidence="Generated TEST ONLY CC0 fixture; all processing permitted",
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
