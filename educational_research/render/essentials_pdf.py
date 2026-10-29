"""Flow-based A4 report renderer; wide records are readable labelled subrows."""

import html
import json
import os
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from ..citations.format import bibliography, in_text
from ..core.quality import validate_compact, warnings
from ..core.score import score

STYLE = json.loads(Path(__file__).with_name("style.json").read_text())
SECTIONS = [
    "A. Research Focus",
    "B. Research Gap Evidence",
    "C. Key Debates & Author Argument Chains",
    "F. Ranked Evidence & Argument Matrix",
    "G. APA 7 References",
    "H. Search & Verification Notes",
]


def register_fonts():
    override = os.getenv("RESEARCH_FONT_DIR")
    candidates = [Path(override)] if override else []
    candidates += [
        Path("/System/Library/Fonts/Supplemental"),
        Path("/usr/share/fonts/truetype/liberation2"),
        Path("/usr/share/fonts/truetype/liberation"),
    ]
    for directory in candidates:
        for base, files in [
            (
                "Times New Roman",
                [
                    "Times New Roman.ttf",
                    "Times New Roman Bold.ttf",
                    "Times New Roman Italic.ttf",
                    "Times New Roman Bold Italic.ttf",
                ],
            ),
            (
                "LiberationSerif",
                [
                    "LiberationSerif-Regular.ttf",
                    "LiberationSerif-Bold.ttf",
                    "LiberationSerif-Italic.ttf",
                    "LiberationSerif-BoldItalic.ttf",
                ],
            ),
        ]:
            if all((directory / f).exists() for f in files):
                for name, file in zip(
                    [
                        "ResearchSerif",
                        "ResearchSerif-Bold",
                        "ResearchSerif-Italic",
                        "ResearchSerif-BoldItalic",
                    ],
                    files,
                ):
                    if name not in pdfmetrics.getRegisteredFontNames():
                        pdfmetrics.registerFont(TTFont(name, str(directory / file)))
                pdfmetrics.registerFontFamily(
                    "ResearchSerif",
                    normal="ResearchSerif",
                    bold="ResearchSerif-Bold",
                    italic="ResearchSerif-Italic",
                    boldItalic="ResearchSerif-BoldItalic",
                )
                if "STSong-Light" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
                return base
    raise RuntimeError(
        "Install Liberation Serif or set RESEARCH_FONT_DIR to licensed Times-compatible fonts"
    )


def safe(value):
    text = str(value)
    cmap = pdfmetrics.getFont("ResearchSerif").face.charToGlyph
    for c in text:
        if (
            ord(c) > 127
            and ord(c) not in cmap
            and not ("\u2e80" <= c <= "\u9fff" or "\uff00" <= c <= "\uffef")
        ):
            raise ValueError(
                f"Unsupported font character U+{ord(c):04X}; supply compatible font or transliteration"
            )
    text = html.escape(text).replace("\n", "<br/>")
    text = re.sub(r"([\u2e80-\u9fff\uff00-\uffef]+)", r'<font name="STSong-Light">\1</font>', text)
    return text


def apa_markup(value):
    # CSL HTML uses inline formatting; permit only the small PDF-safe subset.
    value = re.sub(r"<span[^>]*>|</span>", "", value)
    value = re.sub(r'<a href="([^"]+)"[^>]*>', r'<link href="\1">', value).replace("</a>", "</link>")
    value = value.replace("<em>", "<i>").replace("</em>", "</i>")
    value = (
        re.sub(r"(https://doi\.org/[^\s<]+)", r'<link href="\1">\1</link>', value)
        if "<link" not in value
        else value
    )
    value = re.sub(r"([\u2e80-\u9fff\uff00-\uffef]+)", r'<font name="STSong-Light">\1</font>', value)
    return value


def render(path, config, sources, synthesis, gaps, logs, audit):
    errors = validate_compact(sources)
    if errors:
        raise ValueError("; ".join(errors))
    register_fonts()
    body = ParagraphStyle(
        "body", fontName="ResearchSerif", fontSize=STYLE["body"], leading=14, spaceAfter=5
    )
    dense = ParagraphStyle("dense", parent=body, fontSize=9.5, leading=12, spaceAfter=0)
    heading = ParagraphStyle(
        "heading",
        parent=body,
        fontName="ResearchSerif-Bold",
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=8,
        keepWithNext=True,
    )
    title = ParagraphStyle(
        "title", parent=body, fontName="ResearchSerif-Bold", fontSize=18, leading=23, spaceAfter=8
    )
    refstyle = ParagraphStyle("reference", parent=body, leftIndent=18, firstLineIndent=-18, spaceAfter=9)
    width = A4[0] - STYLE["left"] - STYLE["right"]
    story = []

    def p(text, style=body):
        # Each analytical cell stays below the default continuous-prose ceiling.
        if len(str(text).split()) > 120:
            raise ValueError(
                "Default PDF cell exceeds 120 words; edit compact analysis before rendering"
            )
        return Paragraph(safe(text), style)

    def rows_table(rows, header=None, widths=None):
        data = ([[p(header, dense), ""]] if header else []) + [
            [p(a, dense), p(b, dense)] for a, b in rows
        ]
        table = Table(
            data,
            colWidths=widths or [106, width - 106],
            repeatRows=1 if header else 0,
            hAlign="LEFT",
            splitByRow=1,
        )
        styles = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.grey),
        ]
        if header:
            styles += [
                ("SPAN", (0, 0), (-1, 0)),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.black),
            ]
        table.setStyle(TableStyle(styles))
        story.extend([table, Spacer(1, 8)])

    synthetic = any(s.synthetic for s in sources)
    research_quality = audit.get("research_quality", {})
    provisional = research_quality.get("overall_status") != "PASS"
    story += [p("Educational Research Essentials", title)]
    if provisional:
        story.append(p("PROVISIONAL - NOT FULLY VERIFIED"))
    if synthetic:
        story.append(p("TEST ONLY - SYNTHETIC SOURCES; NOT SCHOLARLY EVIDENCE"))
    story += [p(SECTIONS[0], heading)]
    rq = config.rq or f"What evidence explains {config.topic} within a specified educational context?"
    rows_table(
        [
            ("Topic / RQ", config.topic + "\n" + rq),
            ("Context / method", config.context + "\n" + config.methodology),
            (
                "Scope / assumptions",
                "Provisional topic scoping. Fix population, stage, mechanism, outcomes and transfer boundaries before drawing conclusions.",
            ),
            (
                "Alternative RQs",
                f"How is {config.topic} conceptualised?\nUnder which conditions does evidence converge or conflict?",
            ),
            (
                "Definitions",
                "; ".join(f"{k}: {v}" for k, v in synthesis.definitions.items())
                or "Concept definitions require explicit theoretical and empirical source comparison.",
            ),
            ("Proposed thesis", synthesis.thesis),
            ("Protocol", config.inclusion + "\nExclude: " + config.exclusion),
            (
                "Search / quota",
                f"{config.search_date}; {config.quota} requested references for a potential {config.target_words}-word manuscript. Included {len(sources)}; shortfall {audit['reference_shortfall']}.",
            ),
        ]
    )
    story.append(p(SECTIONS[1], heading))
    novelty = research_quality.get("novelty_audit", {})
    rows_table(
        [
            ("Novelty verdict", novelty.get("verdict", "INSUFFICIENT_EVIDENCE")),
            (
                "Strongest rival",
                novelty.get("strongest_rival_id", "not established")
                + "\n"
                + novelty.get("sceptical_case", "Closest-work challenge incomplete"),
            ),
            (
                "Surviving contribution",
                novelty.get("surviving_contribution", "No novelty claim warranted"),
            ),
            ("Boundary", novelty.get("boundary", "Bounded comparison not established")),
        ]
    )
    for comparison in novelty.get("comparisons", []):
        rows_table(
            [(k, ", ".join(v) if isinstance(v, list) else str(v)) for k, v in comparison.items()],
            "Closest study: " + comparison["source_id"],
        )
    for gap in gaps:
        rows_table(
            [
                ("Closest work", ", ".join(gap.get("closest_source_ids", [])) or "Insufficient sources"),
                ("Missing dimension", gap.get("missing_dimension", "Not established")),
                (
                    "Evidence / boundary",
                    str(gap.get("evidence", "not established"))
                    + "\n"
                    + str(gap.get("search_boundary", "search boundary incomplete")),
                ),
                (
                    "Confidence / novelty",
                    gap["confidence"] + "; " + gap.get("novelty_boundary", "No originality guarantee"),
                ),
                ("Method fit", gap.get("method_fit", "not assessed")),
            ]
        )
    if sources:
        rows_table(
            [(s.id, s.source_argument + "\nLimitation: " + s.limitations) for s in sources[:10]],
            "Closest-work comparison (candidate records; evaluate content access)",
        )
    story.append(p(SECTIONS[2], heading))
    if not synthesis.claims:
        story.append(
            p(
                "No evidence-grounded target claims supplied. Read source content and record attributed extractions before constructing author argument chains."
            )
        )
    for c in synthesis.claims:
        rows_table(
            [
                ("Author claim / sources", c.text + "\n" + ", ".join(c.source_ids)),
                ("Evidence / warrant", ", ".join(c.evidence_ids) + "\n" + c.warrant),
                ("Objection / boundary", c.objection + "\n" + c.qualification),
            ],
            c.id,
        )
        if c.comparison or c.own_inference or c.paragraph_plan:
            rows_table(
                [
                    ("Source positions", "; ".join(k + ": " + v for k, v in c.author_positions.items())),
                    ("Critical comparison", c.comparison),
                    ("Own inference / scope", c.own_inference + "\n" + c.scope),
                    ("Paragraph plan", "\n".join(c.paragraph_plan)),
                    ("Transition warrant", c.transition_warrant),
                ]
            )
    for edge in synthesis.edges:
        rows_table([("Relationship", f"{edge.source} {edge.kind} {edge.target}: {edge.rationale}")])
    if synthesis.alignment:
        rows_table(
            [(k, ", ".join(v)) for k, v in synthesis.alignment.items()],
            "Outline and manuscript alignment",
        )
    story.append(p("D. Theoretical / Conceptual Framework", heading))
    framework = synthesis.framework
    from .framework import drawing

    if framework:
        rows_table(
            [
                ("Phenomenon / outcomes", framework.phenomenon + "; " + "; ".join(framework.outcomes)),
                (
                    "Selection / contribution",
                    framework.combination_justification
                    or framework.no_single_theory_rationale
                    or "One primary lens; compare alternatives below",
                ),
                (
                    "Theory limit / contribution",
                    framework.theory_failure + "\n" + framework.modest_contribution,
                ),
                (
                    "Scope / revision triggers",
                    framework.scope_limits + "\n" + "; ".join(framework.revision_triggers),
                ),
            ]
        )
        for lens in framework.candidates:
            rows_table(
                [
                    (
                        "Evidence / position",
                        lens.name
                        + "; "
                        + ("PRIMARY" if lens.selected else "ALTERNATIVE")
                        + "\n"
                        + ", ".join(lens.source_ids + lens.evidence_ids),
                    ),
                    ("Explanatory fit", lens.explanatory_power + "\nEpistemology: " + lens.epistemology),
                    ("Scope / decision", lens.scope_conditions + "\n" + lens.selection_reason),
                    (
                        "Method use",
                        lens.method_fit
                        + "; "
                        + lens.operationalisation
                        + "; used in: "
                        + ", ".join(lens.used_in),
                    ),
                ],
                lens.id,
            )
        story.append(drawing(framework, width))
        story.append(
            p(
                "Solid links: source-verified. Dashed links: proposed hypotheses or sensitising concepts. Direction does not establish causality.",
                dense,
            )
        )
        for construct in framework.constructs:
            rows_table(
                [
                    (
                        "Definition / boundary",
                        construct.name + ": " + construct.definition + "\n" + construct.boundaries,
                    ),
                    (
                        "Theory / RQ / evidence",
                        ", ".join(
                            construct.lens_ids
                            + construct.rq_ids
                            + construct.claim_ids
                            + construct.evidence_ids
                        ),
                    ),
                    ("Measure / analysis", construct.operationalisation + "\n" + construct.analysis_use),
                    (
                        "Expected / disconfirming",
                        construct.expected_pattern + "\n" + construct.disconfirming_pattern,
                    ),
                ],
                construct.id,
            )
        for relation in framework.relationships:
            rows_table(
                [
                    (
                        "Relationship",
                        f"{relation.source} -> {relation.target}; {relation.status}; {relation.relation_type}",
                    ),
                    (
                        "Mechanism / evidence",
                        relation.mechanism + "\n" + ", ".join(relation.evidence_ids),
                    ),
                    (
                        "Conditions / rival",
                        relation.conditions
                        + "\n"
                        + relation.rival_mechanism
                        + "\nNegative case: "
                        + relation.negative_case,
                    ),
                ],
                relation.id,
            )
    else:
        story.append(
            p(
                "Framework not established: compare literature-led explanatory lenses, define constructs and link them to the RQ, evidence and method before substantive acceptance."
            )
        )
    framework_audit = research_quality.get("framework_audit", {})
    for drift in framework_audit.get("drift", []):
        rows_table([("Construct drift", str(drift))])
    if synthesis.study_design or config.empirical_proposal:
        story.append(p("E. Study Design / Feasibility", heading))
        design = synthesis.study_design
        if design:
            rows_table(
                [
                    ("Proposed design", design.kind + ": " + design.purpose),
                    (
                        "Access / ethics",
                        design.access_status
                        + "; "
                        + design.access_evidence
                        + "\n"
                        + design.ethics_consent,
                    ),
                    ("Recruitment / storage", design.recruitment + "\n" + design.storage),
                    (
                        "Go / no-go / fallback",
                        "; ".join(design.go_conditions)
                        + "\n"
                        + "; ".join(design.no_go_conditions)
                        + "\n"
                        + design.fallback,
                    ),
                ]
            )
            for label, strand in [
                ("QUAN", design.quan),
                ("QUAL", design.qual),
                ("INTEGRATION", design.integration),
            ]:
                if strand:
                    rows_table([(k, str(v)) for k, v in strand.model_dump().items() if v], label)
        else:
            story.append(
                p(
                    "Empirical design and feasibility not established. No data, access or recruitment is assumed."
                )
            )
    story += [PageBreak(), p(SECTIONS[3], heading)]
    citations = dict(bibliography([s for s in sources if s.identity in {"VERIFIED", "SYNTHETIC"}]))
    for index, s in enumerate(sources, 1):
        priority = score(s, config.topic)
        metric_text = "; ".join(
            f"{m.name}={m.value:g}; index/source {m.source}; checked {m.checked_at}; year {m.year or 'N/A'}; category {m.category or 'N/A'}; quartile {m.quartile or 'not verified'}"
            for m in s.metrics
        )
        if not any(m.name in {"JIF", "SJR", "CiteScore", "h5-index"} for m in s.metrics):
            metric_text = "JIF: NOT VERIFIED; quartile: not verified; " + metric_text
        if not any(m.name in {"article_citations", "FWCI"} for m in s.metrics):
            metric_text += " Article citations/FWCI: not verified"
        quotes = []
        for q in s.quotes:
            seg = next(seg for seg in s.segments if seg.id == q.segment_id)
            quotes.append(
                f'"{q.text}" [{seg.locator}; PDF page {seg.pdf_page or "unknown"}; printed page {seg.printed_page or "unknown"}]; {seg.url}; {seg.licence}; checked {seg.checked_at}'
            )
            if q.translation:
                quotes.append(f"Translation ({q.translation_kind}; not verbatim): {q.translation}")
        rows_table(
            [
                (
                    "1. Identity",
                    html.unescape(re.sub(r"<[^>]+>", "", citations.get(s.id, s.title)))
                    + f"\n{in_text(s)}; {s.identity}; {s.cluster}\n{s.url or 'landing page not verified'}",
                ),
                (
                    "2. Objective / context",
                    f"{s.objective}\nStage: {s.education_level}; geography: {s.country}; participants: {s.participants}; design: {s.design}",
                ),
                (
                    "3. Content core",
                    s.summary + "\nTheory: " + s.theory + "; limitation: " + s.limitations,
                ),
                ("4. Source authors", s.source_argument),
                ("5. Original excerpts", "\n".join(quotes) or "NO VERIFIED QUOTE"),
                (
                    "6. Study relevance",
                    f"{priority['relevance_score']}/45 (lexical if unassessed). {s.relevance_explanation}",
                ),
                ("7. Target author", s.target_argument),
                (
                    "8. Cross-paper relation",
                    s.relationship
                    + "; compared sources: "
                    + (", ".join(s.comparison_ids) or "not assessed"),
                ),
                (
                    "9. Argument role / IDs",
                    s.role
                    + "; "
                    + "; ".join(
                        f"{c.id} / {c.warrant_id or 'warrant unnumbered'} / {', '.join(c.evidence_ids)}"
                        for c in synthesis.claims
                        if s.id in c.source_ids
                    ),
                ),
                (
                    "10. Strength / access",
                    s.evidence_strength + "; " + s.evidence_kind + "; " + s.access,
                ),
                (
                    "11-12. Influence",
                    (
                        metric_text
                        or "JIF: NOT VERIFIED; journal quartile: not verified; article citations/FWCI: not verified"
                    )
                    + "\nJournal influence is not article evidence quality.",
                ),
                (
                    "13. Priority",
                    "; ".join(
                        f"{label}: {priority[key] if priority[key] is not None else 'not assessed'}"
                        for key, label in [
                            ("relevance_score", "Relevance /45"),
                            ("study_quality_score", "Evidence /20"),
                            ("journal_influence_score", "Journal /15"),
                            ("article_impact_score", "Article /10"),
                            ("argument_value_score", "Argument /10"),
                        ]
                    )
                    + f"\nRescaled priority: {priority['total_priority_score']}/100; available weight {priority['available_weight']}/100; {priority['priority_status']}. "
                    + priority["why_included"],
                ),
                (
                    "14-15. Verification",
                    f"{s.identity}; checked {s.checked_at}; observed providers: {', '.join(s.providers) or 'none (offline input)'}; publication status: {s.publication_status}\n"
                    + "; ".join(warnings(s)),
                ),
            ],
            f"{s.id} | {index}/{len(sources)} | {s.cluster} | {s.identity}",
        )
        if s.doi:
            url = "https://doi.org/" + s.doi
            story.append(
                Paragraph(
                    f'<link href="{html.escape(url, quote=True)}">{html.escape(url)}</link>', dense
                )
            )
    story += [PageBreak(), p(SECTIONS[4], heading)]
    for sid, reference in citations.items():
        story.append(p(sid, dense))
        story.append(Paragraph(apa_markup(reference), refstyle))
    for s in sources:
        if s.id not in citations:
            story.append(
                p(
                    f"UNRESOLVED {s.id}: {s.title}. Identity {s.identity}; verify against publisher before citing."
                )
            )
    notes_start = len(story)
    story.append(p(SECTIONS[5], heading))
    statuses = sorted({e.get("status", "unknown") for e in logs})
    rows_table(
        [
            ("Coverage", ", ".join(statuses)),
            (
                "Counts",
                "; ".join(
                    f"{k}: {audit[k]}"
                    for k in (
                        "found",
                        "deduplicated",
                        "screened",
                        "excluded",
                        "included",
                        "full_text_verified",
                        "abstract_only",
                        "verified_quotes",
                        "reference_shortfall",
                    )
                ),
            ),
            (
                "Evidence limits",
                "No automatic originality guarantee. Metadata or abstract access cannot verify full-text details. Quote checks establish exact spans within supplied material; source authenticity and licence require review.",
            ),
            (
                "Metrics",
                "Missing metrics remain unverified; available scoring categories are rescaled and disclosed. Journal metrics do not establish individual article quality.",
            ),
        ]
    )

    # Keep each short note table together; gate explanations may legitimately span pages.
    story[notes_start:] = [KeepTogether(story[notes_start:])]
    story.append(p("Research Quality Gates", heading))
    for key, gate in research_quality.get("gates", {}).items():
        # Reasons are separate diagnostic fragments, not a generated continuous essay.
        reasons = gate["reason"].split("; ")
        rows_table(
            [("Status / counts", gate["status"] + "; " + str(gate.get("counts", {})))]
            + [("Finding", r) for r in reasons],
            key,
        )
    story.append(
        p("Structural checks do not certify comprehension, originality or journal acceptance.", dense)
    )

    def frame(canvas, doc):
        canvas.saveState()
        canvas.setFont("ResearchSerif", 9)
        canvas.drawString(STYLE["left"], A4[1] - 33, "Educational Research")
        canvas.drawRightString(
            A4[0] - STYLE["right"],
            A4[1] - 33,
            "TEST ONLY | PROVISIONAL"
            if synthetic
            else "PROVISIONAL"
            if provisional
            else "Evidence Essentials",
        )
        canvas.setLineWidth(0.45)
        canvas.line(STYLE["left"], A4[1] - 42.5, A4[0] - STYLE["right"], A4[1] - 42.5)
        canvas.setFont("ResearchSerif", 8)
        canvas.drawCentredString(A4[0] / 2, 27, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=STYLE["left"],
        rightMargin=STYLE["right"],
        topMargin=STYLE["top"],
        bottomMargin=STYLE["bottom"],
        title="Educational Research Essentials",
        author="Educational Research Skill",
        pageCompression=1,
    )
    doc.build(story, onFirstPage=frame, onLaterPages=frame)
