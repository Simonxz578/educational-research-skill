"""Five-section native reader; approved v3 geometry with less visible machinery."""

import math
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, KeepTogether, PageBreak
from .essentials_pdf import register_fonts, safe, apa_markup, STYLE
from .framework import drawing
from ..citations.format import bibliography
from ..core.reader import SECTIONS


def render(path, config, sources, synthesis, view, qa):
    register_fonts()
    width = A4[0] - STYLE["left"] - STYLE["right"]
    body = ParagraphStyle(
        "reader-body", fontName="ResearchSerif", fontSize=10.5, leading=14, spaceAfter=6
    )
    small = ParagraphStyle("reader-locator", parent=body, fontSize=9.5, leading=12, spaceAfter=4)
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
        spaceAfter=4,
        keepWithNext=True,
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
        if len(str(text).split()) > 140:
            raise ValueError(
                "Reader paragraph exceeds 140 words; revise its source-linked prose rather than truncate it"
            )
        return Paragraph(("<b>" + safe(label) + "</b> " if label else "") + safe(text), style)

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

    def section(index):
        divider, gap = rule(), Spacer(1, 7)
        divider.keepWithNext = gap.keepWithNext = True
        story.extend(
            [p(f"{['I', 'II', 'III', 'IV', 'V'][index]}. " + SECTIONS[index], heading), divider, gap]
        )

    def citations(ids):
        works = {w.source_id: w for w in view.papers}
        return "; ".join(works[i].in_text.strip("()") for i in ids if i in works)

    sel, novelty = view.source_selection, view.novelty
    status = (
        "PROVISIONAL - EVIDENCE INCOMPLETE"
        if qa["overall_status"] != "PASS"
        else "SOURCE-GROUNDED RESEARCH ROADMAP"
    )
    if sel["shortfall"] or sel["selected_shortfall"]:
        status += " | SOURCE SHORTFALL"
    if sel.get("abstract_only_A"):
        status = (
            f"PROVISIONAL - {sel['full_text_verified_K']} FULL TEXTS, {sel['abstract_only_A']} ABSTRACTS"
        )
    story.extend([p(view.title.upper(), title), p(status, small)])
    if view.coverage["synthetic"]:
        story.append(p("TEST ONLY - SYNTHETIC SOURCES; NOT SCHOLARLY EVIDENCE", small))
    section(0)
    story.extend([p(view.problem, label="Problem."), p(view.principal_question, label="Question.")])
    verdict = novelty.get("verdict", "INSUFFICIENT_EVIDENCE")
    if verdict in {"GAP_SUPPORTED", "GAP_NARROW_BUT_DEFENSIBLE"}:
        contribution = novelty.get("surviving_contribution") or "The contribution remains provisional."
    elif verdict == "GAP_NOT_SUPPORTED":
        contribution = "The closest work pre-empts the proposed gap. Revise the question before claiming a contribution."
    else:
        contribution = (
            "A defensible contribution has not yet been established from the available primary evidence."
        )
    story.append(p(contribution, label="Provisional contribution."))
    for n, c in enumerate(view.chains[:4], 1):
        story.append(p(c["text"] + " (" + citations(c["source_ids"]) + ")", label=f"{n:02}."))
    if not view.chains:
        story.append(
            p(
                "Obtain the missing primary texts, compare their positions, challenge the closest-study gap, then connect the surviving question to a feasible design."
            )
        )
    section(1)
    story.append(
        p(
            f"{len(view.papers)} included of {sel['selection_target_N']} target; {sel['full_text_verified_K']} full-text verified; {sel['abstract_only_A']} abstract only; {sum(len(p.display_excerpts) for p in view.papers)} original extracts.",
            small,
        )
    )
    if not view.papers:
        story.append(
            p(
                "No work currently meets the primary-text reader criteria. Complete lawful access and close reading before making source-specific claims."
            )
        )
    groups = {}
    for work in view.papers:
        groups.setdefault(work.debate_id, []).append(work)
    number = 0
    for debate, works in groups.items():
        if len(groups) > 1:
            story.append(p(debate, identification))
        for work in works:
            number += 1
            elems = [
                p(
                    f"{number:02}  {work.in_text.strip('()')}  [{work.source_id}] - {work.evidence_status.replace('_', ' ')}",
                    identification,
                ),
                p(work.title, small),
            ]
            elems.append(p("ORIGINAL AUTHOR TEXT", identification))
            for quote in work.display_excerpts:
                elems.append(
                    Paragraph(
                        "<i>“"
                        + safe(quote.text)
                        + (" [...]" if quote.omitted_after else "")
                        + "”</i> ("
                        + safe(quote.locator)
                        + ")",
                        body,
                    )
                )
            if work.display_status != "PASS":
                elems.append(
                    p(
                        f"Original words shown: {work.original_words_shown}/100 - insufficient due to {work.display_reason}.",
                        small,
                    )
                )
            elems.append(p(work.our_inference.text, label="OUR CRITICAL USE."))
            url = "https://doi.org/" + work.doi if work.doi else work.url
            if url.startswith(("http://", "https://")):
                elems.append(Paragraph('<link href="' + safe(url) + '">' + safe(url) + "</link>", small))
            elems.extend([Spacer(1, 3), rule(), Spacer(1, 8)])
            if sum(e.wrap(width, 730)[1] for e in elems) > 690:
                raise ValueError(
                    f"{work.source_id}: source block cannot fit at readable size; revise its explanation"
                )
            story.append(KeepTogether(elems))
    section(2)
    for n, c in enumerate(view.chains, 1):
        if c.get("evidence_scope") == "PRELIMINARY_ABSTRACT":
            story.append(
                p(
                    "Preliminary abstract-level comparison; not a full-text or originality conclusion.",
                    small,
                )
            )
        story.append(
            p(
                c["comparison"] + " (" + citations(c["source_ids"]) + "). " + c["warrant"],
                label=f"{n:02}.",
            )
        )
        story.append(p(c["objection"] + "; " + c["qualification"], label="Counterargument."))
        story.append(p(c["own_inference"], label="Our synthesis."))
    if not view.chains:
        story.append(
            p(
                "Independent primary-text comparisons and counterarguments remain incomplete; no integrated conclusion is warranted."
            )
        )
    rival = novelty.get("strongest_rival_id")
    rival_name = citations([rival]) if rival else "Not yet established"
    story.append(
        p(
            rival_name
            + ": "
            + (novelty.get("sceptical_case") or "The nearest works require content comparison."),
            label="Strongest closest-study challenge.",
        )
    )
    story.append(
        p(
            contribution
            + " "
            + novelty.get("boundary", "Comparison remains bounded to available evidence."),
            label="What survives.",
        )
    )
    if verdict == "GAP_NOT_SUPPORTED" and synthesis.novelty and synthesis.novelty.revised_question:
        story.append(p(synthesis.novelty.revised_question, label="Revised question to investigate."))
    section(3)
    framework = synthesis.framework if view.framework else None
    if framework:
        for lens in [x for x in framework.candidates if x.selected]:
            story.append(
                p(
                    lens.name + ": " + lens.selection_reason + " (" + citations(lens.source_ids) + ").",
                    label="Explanatory lens.",
                )
            )
        story.append(drawing(framework, width))
        story.append(
            p(
                "Solid: source-grounded links. Dashed: proposed or sensitising links. Arrows express the stated analytical direction, not demonstrated causal effects.",
                small,
            )
        )
        for construct in framework.constructs:
            story.append(
                p(
                    construct.definition
                    + "; "
                    + construct.boundaries
                    + " ("
                    + citations(construct.source_ids)
                    + ").",
                    label=construct.name + ".",
                )
            )
        story.append(
            p(framework.theory_failure + " " + framework.scope_limits, label="Explanatory boundary.")
        )
        story.append(
            p(
                "; ".join(
                    c.name + ": " + c.operationalisation + ", " + c.analysis_use
                    for c in framework.constructs
                ),
                label="Proposed observables and analysis.",
            )
        )
    else:
        story.append(
            p(
                "An explanatory framework is not yet established. Resolve source evidence, construct distinctions and connected mechanisms before selecting a lens or implying causality."
            )
        )
    for n, c in enumerate(view.chains[:4], 1):
        story.append(
            p(
                c["transition_warrant"] + " (" + citations(c["source_ids"]) + ").",
                label=f"Writing step {n}.",
            )
        )
    if not view.chains:
        story.append(
            p(
                "Complete the missing readings, compare independent authors, challenge novelty and align the surviving question with constructs before writing the review."
            )
        )
    design = synthesis.study_design
    if design:
        strands = [
            label + ": " + strand.rq + "; " + strand.analysis
            for label, strand in [("QUAN", design.quan), ("QUAL", design.qual)]
            if strand
        ]
        if design.integration:
            strands += [
                "Integration: "
                + design.integration.connection
                + "; "
                + design.integration.meta_inference
            ]
        if strands:
            story.append(p(". ".join(strands), label="Proposed research sequence."))
        story.append(
            p(
                "Proceed only if "
                + "; ".join(design.go_conditions)
                + ". Access: "
                + design.access_status
                + ". Fallback: "
                + design.fallback,
                label="Feasibility gate.",
            )
        )
    elif config.empirical_proposal:
        story.append(
            p(
                "Recruitment, non-user access and ethics permissions are unconfirmed. Proceed only after a feasible access plan; otherwise narrow to an honestly labelled accessible case study.",
                label="Feasibility gate.",
            )
        )
    else:
        story.append(
            p(
                "Proceed to the review only when primary readings and the closest-study challenge support its claims; otherwise narrow the question and resolve the missing sources.",
                label="Next step.",
            )
        )
    entries = []
    for source_id, entry in bibliography(sources):
        block = [p(source_id, small), Paragraph(apa_markup(entry), reference)]
        entries.append((block, sum(e.wrap(width, 730)[1] for e in block)))
    disclosure = p(
        f"Included {len(sources)} of {sel['selection_target_N']} target; full-text verified {sel['full_text_verified_K']}; abstract only {sel['abstract_only_A']}; deep-reviewed {sel['qualified_deep_read_K']} of {sel['deep_review_requirement_N']} required; original extracts {sum(len(p.display_excerpts) for p in view.papers)}; Scholar {view.coverage['scholar']}.",
        small,
    )
    total = sum(height for _, height in entries) + 75
    pages = max(1, math.ceil(total / 650))
    per_page = max(1, math.ceil(len(entries) / pages))
    for start in range(0, max(1, len(entries)), per_page):
        if start:
            story.append(PageBreak())
        block = [
            p("V. " + SECTIONS[4] + (" (continued)" if start else ""), heading),
            rule(),
            Spacer(1, 7),
        ]
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
