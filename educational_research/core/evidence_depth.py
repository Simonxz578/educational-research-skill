"""Conservative evidence-word accounting; grounded interpretation still needs expert review."""

import re

ROLES = [
    {"claim", "definition"},
    {"method", "mechanism"},
    {"result", "reasoning"},
    {"limitation", "boundary", "counterpoint"},
]
STOP = set(
    "a an the this that these those and or but of in on at to for from with by is are was were be as it its their they we our author authors study studies research paper evidence result results method methods finding findings test only synthetic example not no can could may would should".split()
)


def english_words(text):
    return re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", text)


def evidence_anchors(reading):
    return [next((e for e in reading.evidence if e.content_type in role), None) for role in ROLES]


def sentences(text):
    return [
        re.sub(r"\s+", " ", s).strip().casefold() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()
    ]


def primary_depth_audit(reading, quotes=()):
    issues, seen, count = [], set(), 0
    if reading is None:
        return {
            "primary_evidence_words": 0,
            "shortfall": 100,
            "issues": ["No primary-text reading"],
            "threshold": 100,
        }
    for entry in evidence_anchors(reading):
        if entry is None:
            issues.append("Missing primary evidence role")
            continue
        grounded = {w.casefold() for w in english_words(entry.exact_span)} - STOP
        paraphrased = {w.casefold() for w in english_words(entry.paraphrase)} - STOP
        words = [w.casefold() for w in english_words(entry.paraphrase)]
        content_words = [w for w in words if w not in STOP]
        if len(content_words) >= 15 and len(set(content_words)) < max(6, len(content_words) / 4):
            issues.append(f"{entry.evidence_id}: repeated-word padding is not substantive evidence")
        grams = [tuple(words[i : i + 5]) for i in range(max(0, len(words) - 4))]
        if any(grams.count(gram) >= 3 for gram in set(grams)):
            issues.append(f"{entry.evidence_id}: repeated phrase padding is not substantive evidence")
        if len(grounded & paraphrased) < min(3, len(grounded)) or len(grounded) < 3:
            issues.append(f"{entry.evidence_id}: paraphrase/source-span matching needs review")
        for sentence in sentences(entry.paraphrase):
            if sentence in seen:
                issues.append(f"{entry.evidence_id}: duplicated evidence prose cannot count twice")
            elif re.search(
                r"\b(this study highlights|provides valuable insights|important contribution to the literature|further research is needed|sheds light on)\b",
                sentence,
            ):
                issues.append(f"{entry.evidence_id}: generic filler is not primary-evidence explanation")
            else:
                explanation = sentence
                for quote in quotes:
                    explanation = explanation.replace(quote.text.casefold(), " ")
                count += len(english_words(explanation))
                seen.add(sentence)
        if (
            entry.finding_kind == "reported"
            and re.search(
                r"\b(proves?|causes?|caused|causal effect|improves?)\b", entry.paraphrase, re.I
            )
            and not re.search(r"\b(no|not|cannot|doesn.t|without)\b", entry.paraphrase, re.I)
        ):
            issues.append(f"{entry.evidence_id}: participant reports cannot establish causal effects")
    if count < 100:
        issues.append(f"Primary-evidence explanation shortfall: {count}/100 English words; no padding")
    return {
        "primary_evidence_words": count,
        "shortfall": max(0, 100 - count),
        "threshold": 100,
        "issues": sorted(set(issues)),
        "notice": "Only the four rendered source paraphrases count; title, locators, metadata, quotes and our inference are excluded. Lexical checks do not certify semantic accuracy.",
    }


def cross_source_boilerplate(sources):
    duplicates, seen = {}, {}
    for s in sources:
        if not s.reading:
            continue
        values = {
            sentence
            for e in evidence_anchors(s.reading)
            if e
            for sentence in sentences(e.paraphrase)
            if len(english_words(sentence)) >= 8
        }
        prior = {}
        for sentence in values:
            for other in seen.get(sentence, []):
                prior[other] = prior.get(other, 0) + 1
        for other, count in prior.items():
            if count >= 2 and count / max(1, len(values)) >= 0.5:
                duplicates.setdefault(s.id, []).append(other)
                duplicates.setdefault(other, []).append(s.id)
        for sentence in values:
            seen.setdefault(sentence, []).append(s.id)
    return duplicates


def quotation_usage(source, extra_texts=()):
    """Count declared source fragments wherever repeated in that source's reader prose."""
    from ..models import quotation_units

    anchors = [e for e in evidence_anchors(source.reading) if e] if source.reading else []
    prose = "\n".join(
        [e.paraphrase for e in anchors]
        + ([anchors[0].researcher_inference] if anchors else [])
        + list(extra_texts)
    )
    return sum(quotation_units(q.text) * (1 + prose.count(q.text)) for q in source.quotes)


def reader_extra_texts(source, synthesis):
    texts = []
    for chain in synthesis.claims:
        texts += [
            chain.text,
            chain.comparison,
            chain.warrant,
            chain.objection,
            chain.qualification,
            chain.own_inference,
            chain.transition_warrant,
        ]
    f = synthesis.framework
    if f:
        texts += [lens.name + " " + lens.selection_reason for lens in f.candidates if lens.selected]
        texts += [
            " ".join([c.definition, c.boundaries, c.operationalisation, c.analysis_use])
            for c in f.constructs
        ]
        texts += [f.theory_failure, f.scope_limits]
    n = synthesis.novelty
    if n:
        texts += [n.surviving_contribution, n.surviving_contribution, n.search_boundary]
        texts += [n.sceptical_case, n.revised_question]
    design = synthesis.study_design
    if design:
        texts += design.go_conditions + [design.fallback]
        texts += [strand.rq + " " + strand.analysis for strand in [design.quan, design.qual] if strand]
        if design.integration:
            texts += [design.integration.connection, design.integration.meta_inference]
    return texts
