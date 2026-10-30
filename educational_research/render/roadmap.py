"""Native reader-first academic roadmap; private audit machinery is never printed here."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    KeepTogether,
    PageBreak,
)
from .essentials_pdf import register_fonts, safe, apa_markup, STYLE
from .framework import drawing
from ..citations.format import bibliography

SECTIONS = [
    "THE RESEARCH LOGIC",
    "THE AUTHORS' ORIGINAL EVIDENCE",
    "FROM EVIDENCE TO ARGUMENT",
    "THEORETICAL / CONCEPTUAL FRAMEWORK",
    "RESEARCH / WRITING ROADMAP",
    "SELECTED APA 7 REFERENCES",
]


def render(path, config, sources, synthesis, view, qa):
    register_fonts()
    width = A4[0] - STYLE["left"] - STYLE["right"]
    body = ParagraphStyle(
        "reader-body", fontName="ResearchSerif", fontSize=10.5, leading=14, spaceAfter=5
    )
    small = ParagraphStyle("reader-locator", parent=body, fontSize=9.5, leading=12, spaceAfter=3)
    heading = ParagraphStyle(
        "reader-heading",
        parent=body,
        fontName="ResearchSerif-Bold",
        fontSize=12,
        leading=16,
        spaceBefore=13,
        spaceAfter=7,
        keepWithNext=True,
    )
    title = ParagraphStyle(
        "reader-title", parent=body, fontName="ResearchSerif-Bold", fontSize=18, leading=22, spaceAfter=7
    )
    identification = ParagraphStyle(
        "reader-paper",
        parent=body,
        fontName="ResearchSerif-Bold",
        fontSize=11,
        leading=14,
        spaceAfter=3,
        keepWithNext=True,
    )
    quotation = ParagraphStyle(
        "reader-quote",
        parent=body,
        fontName="ResearchSerif-Italic",
        leftIndent=10,
        fontSize=10.5,
        leading=14,
        spaceAfter=3,
    )
    reference = ParagraphStyle(
        "reader-reference",
        parent=body,
        leftIndent=18,
        firstLineIndent=-18,
        fontSize=10.5,
        leading=13.5,
        spaceAfter=7,
    )
    story = []

    def p(text, style=body, label=None):
        if len(str(text).split()) > 120:
            raise ValueError(
                "Reader cell exceeds 120 words; revise source-linked analysis rather than truncate it"
            )
        markup = (f"<b>{safe(label)}</b> " if label else "") + safe(text)
        return Paragraph(markup, style)

    def rule():
        return Table(
            [[""]],
            colWidths=[width],
            rowHeights=[0.2],
            style=[
                ("LINEABOVE", (0, 0), (-1, -1), 0.35, colors.HexColor("#888888")),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ],
        )

    def section(number):
        divider, gap = rule(), Spacer(1, 7)
        divider.keepWithNext = gap.keepWithNext = True
        story.extend([p(SECTIONS[number], heading), divider, gap])

    def linked(statement, marker):
        return statement.text + " [" + marker + "]"

    sel = view.source_selection
    status = (
        "PROVISIONAL - EVIDENCE INCOMPLETE"
        if qa["overall_status"] != "PASS"
        else "SOURCE-GROUNDED RESEARCH ROADMAP"
    )
    if sel["shortfall"] or sel["selected_shortfall"]:
        status += " | SOURCE SHORTFALL"
    story.extend([p(view.title.upper(), title), p(status, small)])
    if view.coverage["synthetic"]:
        story.append(p("TEST ONLY - SYNTHETIC SOURCES; NOT SCHOLARLY EVIDENCE", small))
    section(0)
    story.extend(
        [
            p(view.problem, label="The scholarly problem."),
            p(view.principal_question, label="Principal question."),
            p(view.thesis, label="Proposed argument."),
        ]
    )
    novelty = view.novelty
    story.append(
        p(
            novelty.get("surviving_contribution")
            or "A surviving closest-study gap has not yet been established.",
            label="Narrow gap.",
        )
    )
    story.append(p(novelty.get("boundary", "Bounded comparison is incomplete."), small))
    for n, c in enumerate(view.chains[:5], 1):
        story.append(
            p(c["text"] + " [" + ", ".join(c["source_ids"]) + "]", label=f"{n:02}  Argument step.")
        )
    if not view.chains:
        story.append(
            p(
                "Obtain and review the missing primary texts; compare their actual positions before claiming a synthesis or research gap."
            )
        )
    section(1)
    story.append(
        p(
            f"{len(view.papers)} selected of {sel['selection_target_N']} target; {sel['qualified_deep_read_K']} deeply reviewed works; {sel['quotation_count']} verified micro-excerpts.",
            small,
        )
    )
    if not view.papers:
        story.append(
            p(
                "No works currently meet the primary-text reader criteria. Unverified discoveries and access requests remain in the private follow-up candidates."
            )
        )
    # Group sources by the substantive debate while preserving the ranking inside each group.
    groups = {}
    for work in view.papers:
        groups.setdefault(work.debate_id, []).append(work)
    order = 0
    for debate, papers in groups.items():
        if len(groups) > 1:
            story.append(p(debate, identification))
        for work in papers:
            order += 1
            elems = [
                p(f"{order:02}  {work.in_text.strip('()')}  [{work.source_id}]", identification),
                p(work.title, small),
            ]
            for quote in work.original_microquotes:
                elems += [
                    p("“" + quote.text + "”", quotation),
                    p(f"{quote.evidence_id} · {quote.locator}", small),
                ]
            if not work.original_microquotes:
                elems.append(
                    p(
                        "Source permissions do not permit verbatim reproduction; close paraphrases follow.",
                        small,
                    )
                )
            elems.append(p(linked(work.source_author_position, "a"), label="Author's argument."))
            for i, statement in enumerate(work.source_reasoning_and_results):
                elems.append(
                    p(
                        linked(statement, "b" if i == 0 else "c"),
                        label="Method / mechanism." if i == 0 else "Evidence / reasoning.",
                    )
                )
            elems += [
                p(linked(work.source_limitations, "d"), label="Boundary / counterpoint."),
                p(linked(work.our_inference, "a; interpretation"), label="Our inference."),
            ]
            evidence_statements = [
                work.source_author_position,
                *work.source_reasoning_and_results,
                work.source_limitations,
            ]
            elems.append(
                p(
                    "Locators: "
                    + "; ".join(
                        f"{label}: " + ", ".join(statement.locators)
                        for label, statement in zip("abcd", evidence_statements)
                    ),
                    small,
                )
            )
            url = "https://doi.org/" + work.doi if work.doi else work.url
            if url.startswith(("https://", "http://")):
                elems.append(Paragraph('<link href="' + safe(url) + '">' + safe(url) + "</link>", small))
            elems += [Spacer(1, 4), rule(), Spacer(1, 8)]
            # No decorative card; preserve the source's quote/claim/context as one flow block.
            height = sum(e.wrap(width, 730)[1] for e in elems)
            if height > 690:
                raise ValueError(
                    f"{work.source_id}: source block is too long for one readable page; revise the reader paraphrases"
                )
            story.append(KeepTogether(elems))
    section(2)
    for i, c in enumerate(view.chains, 1):
        story.extend([p(f"{i:02}  " + c["text"], identification)])
        story.append(
            p(
                "; ".join(f"{sid}: {position}" for sid, position in c["author_positions"].items()),
                label="Source positions.",
            )
        )
        story.extend(
            [
                p(
                    c["comparison"] + " [" + ", ".join(c["evidence_ids"]) + "]",
                    label="Critical comparison.",
                ),
                p(c["warrant"], label="Warrant."),
                p(c["objection"] + " " + c["qualification"], label="Counterargument / limit."),
                p(c["own_inference"], label="Our synthesis."),
            ]
        )
    for edge in synthesis.edges:
        if edge.kind in {
            "contradicts",
            "qualifies",
            "method_incompatible",
            "same_construct_different_measure",
        } and {edge.source, edge.target} <= set(view.selected_source_ids):
            story.append(
                p(
                    f"{edge.source} / {edge.target}: {edge.rationale} ["
                    + ", ".join(edge.evidence_ids)
                    + "]",
                    label="Critical counterpoint.",
                )
            )
    story.append(
        p(
            novelty.get("sceptical_case") or "The strongest rival study has not yet been compared.",
            label="Closest-study challenge.",
        )
    )
    story.append(
        p(
            novelty.get("surviving_contribution") or "No novelty claim is warranted.",
            label="What remains.",
        )
    )
    section(3)
    framework = synthesis.framework
    if framework and view.framework:
        selected = [lens for lens in framework.candidates if lens.selected]
        for lens in selected:
            story.append(
                p(
                    lens.name + ": " + lens.selection_reason + " [" + ", ".join(lens.source_ids) + "]",
                    label="Primary explanatory lens.",
                )
            )
        if len(selected) > 1:
            story.append(p(framework.combination_justification, label="Reason for combining lenses."))
        story.append(drawing(framework, width))
        story.append(
            p(
                "Solid: source-grounded links. Dashed: proposed or sensitising links. Arrows express the stated analytical direction, not demonstrated causal effects.",
                small,
            )
        )
        for c in framework.constructs:
            story.extend(
                [
                    p(
                        c.definition + " " + c.boundaries + " [" + ", ".join(c.evidence_ids) + "]",
                        label=c.name + ".",
                    )
                ]
            )
        for relation in framework.relationships:
            story.append(
                p(
                    relation.mechanism
                    + " "
                    + relation.conditions
                    + " ["
                    + ", ".join(relation.evidence_ids)
                    + "]",
                    label=relation.id + " (" + relation.status + ").",
                )
            )
        story.append(
            p(framework.theory_failure + " " + framework.scope_limits, label="What theory cannot show.")
        )
    else:
        story.append(
            p(
                "A literature-led explanatory framework is not yet established. Candidate theories and unresolved alignment remain in the private audit."
            )
        )
    section(4)
    if not view.chains:
        story.append(
            p(
                "Complete the missing primary-text readings, compare independent source positions, and test the closest-study gap before planning the final literature-review paragraphs."
            )
        )
    for i, c in enumerate(view.chains, 1):
        story.extend(
            [
                p(f"{i:02}  {c['section']}", identification),
                p(c["text"], label="Paragraph purpose."),
                p(
                    c["comparison"] + " [" + ", ".join(c["source_ids"]) + "]",
                    label="Support / qualification.",
                ),
                p(", ".join(c["source_ids"]) + "; " + c["warrant"], label="Evidence and warrant."),
                p(
                    ", ".join(c["theory_ids"])
                    + " → "
                    + ", ".join(c["rq_ids"])
                    + "; "
                    + c["transition_warrant"],
                    label="Congruence and transition.",
                ),
            ]
        )
    if framework and view.framework:
        for c in framework.constructs:
            story.append(
                p(
                    c.operationalisation
                    + "; "
                    + c.analysis_use
                    + "; disconfirming pattern: "
                    + c.disconfirming_pattern,
                    label=c.name + ".",
                )
            )
    if synthesis.study_design:
        d = synthesis.study_design
        for label, strand in [("QUAN", d.quan), ("QUAL", d.qual)]:
            if strand:
                story.append(
                    p(
                        strand.rq + " " + strand.sampling_logic + " " + strand.analysis,
                        label=label + " (proposed).",
                    )
                )
        if d.integration:
            story.append(
                p(
                    d.integration.connection
                    + " "
                    + d.integration.joint_display
                    + " "
                    + d.integration.discordance,
                    label="Integration.",
                )
            )
        story.append(
            p(
                d.access_status + "; " + d.ethics_consent + "; " + d.fallback,
                label="Access, ethics and fallback.",
            )
        )
    elif config.empirical_proposal:
        story.append(
            p(
                "Access and an appropriate study design are not established; no recruitment or institutional records are assumed."
            )
        )
    entries = []
    for source_id, entry in bibliography(sources):
        block = [p(source_id, small), Paragraph(apa_markup(entry), reference)]
        entries.append((block, sum(e.wrap(width, 730)[1] for e in block)))
    disclosure = p(
        f"Selected {len(sources)} of {sel['selection_target_N']} target; deep-reviewed {sel['qualified_deep_read_K']} of {sel['deep_review_requirement_N']} required; "
        f"micro-excerpts {sel['quotation_count']}; Scholar {view.coverage['scholar']}. "
        "Source access, novelty limits and complete verification records remain in evidence/.",
        small,
    )
    # Balance reference continuations instead of stranding a final reference on a blank page.
    import math

    total = sum(height for _, height in entries) + 75
    pages = max(1, math.ceil(total / 650))
    per_page = max(1, math.ceil(len(entries) / pages))
    for start in range(0, max(1, len(entries)), per_page):
        if start:
            story.append(PageBreak())
        block = [p(SECTIONS[5] + (" (continued)" if start else ""), heading), rule(), Spacer(1, 7)]
        for elements, _ in entries[start : start + per_page]:
            block.extend(elements)
        if start + per_page >= len(entries):
            block.extend([Spacer(1, 6), rule(), Spacer(1, 5), disclosure])
        story.append(KeepTogether(block))

    def frame(canvas, doc):
        canvas.saveState()
        canvas.setFont("ResearchSerif", 9)
        canvas.drawString(STYLE["left"], A4[1] - 33, "EDUCATIONAL RESEARCH")
        canvas.drawRightString(
            A4[0] - STYLE["right"],
            A4[1] - 33,
            "ROADMAP | TEST ONLY" if view.coverage["synthetic"] else "ROADMAP",
        )
        canvas.setStrokeColor(colors.HexColor("#888888"))
        canvas.setLineWidth(0.4)
        canvas.line(STYLE["left"], A4[1] - 42.5, A4[0] - STYLE["right"], A4[1] - 42.5)
        canvas.line(STYLE["left"], 41, A4[0] - STYLE["right"], 41)
        canvas.setFont("ResearchSerif", 8)
        canvas.drawCentredString(A4[0] / 2, 27, str(doc.page))
        canvas.restoreState()

    # SimpleDocTemplate frames add 6 pt padding; compensate so text and diagrams
    # use the inspected 56.7–538.6 pt outer bounds exactly.
    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=STYLE["left"] - 6,
        rightMargin=STYLE["right"] - 6,
        topMargin=STYLE["top"] - 6,
        bottomMargin=STYLE["bottom"] - 6,
        title="Research Argument Roadmap",
        author="Educational Research Skill",
        pageCompression=1,
    )
    document.build(story, onFirstPage=frame, onLaterPages=frame)
