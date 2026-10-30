---
name: educational-research
description: Research education through checked original texts, retain genuine abstract-only fallbacks, compare authors, challenge gaps and build explanatory frameworks. Produces a readable research roadmap with private evidence audits. Use for substantive research and manuscript evidence work, not simple proofreading.
---

# Educational Research / 教育研究

Deliver one native `Research_Roadmap.pdf` and a one-paragraph note. Keep technical records private in `evidence/`. Preserve the approved A4 white/black Times layout and five sections: research logic; original author evidence; argument integration/closest-study challenge; framework/roadmap; APA references. Do not print audits, search errors, matrices or word-count dashboards. Use the installed companion Python package. Follow the user's language; default scholarly prose is British English.

## A topic and quantity are enough to begin

Interpret “20 papers/20篇” as `--target-references 20` (exact by default), “at least/至少” as `--source-semantics at_least`, and preserve original intent with `--user-quantity-intent`. Topic alone targets at least ten works; word-count discovery sizing has a floor of ten and explicit N wins. Select relevant independent works, preferring genuine full texts where equally relevant without discarding an essential paywalled work. Do not ask the user to repair every access gap manually.

Distinguish requested/included N, qualified FULL_TEXT_VERIFIED K, ABSTRACT_ONLY A and unfilled item shortfall. Abstracts are useful reader sources but never satisfy strict deep-reading requirements `max(10,N,any higher expressly required minimum)`. Twenty items with thirteen full texts and seven abstracts is twenty included, thirteen deep reviews and a strict full-text shortfall of seven. Never pad with unrelated or invented papers.

## Visible original author evidence (v0.4.4)

Read [the current source-first display contract](references/visible-original-v044.md). Each included work must visibly display at least 100 English words of verified verbatim author text in the main PDF wherever reproduction is justified. This replaces the v0.4.3 private-only 100-word/microquote reader policy. Private inspection, explanations, inference, titles, translations and references cannot satisfy visible original words. Lead with ORIGINAL AUTHOR TEXT, version-specific locators, then OUR CRITICAL USE in one or two sentences and a DOI/link. Omit bulky per-paper AI summaries.

Keep distinct typed original/explanation/inference fields privately. Select useful original passages from approximately four roles where available. Count distinct non-overlapping positions in the actual version printed in the finished PDF. Repeated fragments cannot increase the count. Preserve exact wording, mark omissions and retain hashes/positions/reader/scope privately. Machine exactness cannot certify interpretation.

## Native workflow without a history-dependent negotiation

1. Scope and discover using [prospective protocol](references/research-protocol.md) and [ERIC/Scholar](references/eric-and-google-scholar-search.md). Preserve actual receipts; a Scholar plan is not a completed search.
2. Attempt bounded lawful full-text routes with [native acquisition](references/full-text-access.md): publisher OA, ERIC, repositories and configured OA pointers. Stop denied/CAPTCHA/uncertain-rights paths. Never assume an institutional subscription or request passwords.
3. If usable full text/processing is unavailable, automatically retrieve and identity-check the genuine publisher/indexed abstract. Native fallback retains its artifact and provenance. Read that actual abstract and, where useful, supply a checked faithful explanation in `abstract_evidence`; do not infer unseen full-text details. A default native projection only reports safe literal topical mentions/link, never manufactured findings. Mark ABSTRACT ONLY visibly. An abstract of 95 or 130 words is still not a full-text review; its full-text word gate is NOT APPLICABLE / NOT FULL-TEXT VERIFIED. If no real abstract is available, retain METADATA ONLY privately.
4. Continue actual critical reading of accessible primary texts using [reading policy](references/full-text-reading.md). Keep authentic abstract fallbacks while obtaining the feasible full-text set. No fabricated quotes/pages, findings, limitations or four-anchor readings for abstracts.
5. Build 3–5 connected comparisons and a strongest-rival [novelty challenge](references/gap-and-argument-method.md). Abstracts can support explicitly `PRELIMINARY_ABSTRACT` comparisons, never unqualified full-text or originality claims. Strict G3/G4 still require adequate genuine full-text evidence. Revise a refuted question rather than invent novelty.
6. Build a parsimonious, connected [framework](references/framework-builder.md) and congruent [feasibility plan](references/study-design-feasibility.md). Preserve construct distinctions, disconfirmation and honest access/fallback conditions. Unsupported theory remains provisional/private.
7. Run the native pipeline/validator and view actual first, dense, framework/middle and final previews. Preserve all 15 audit dimensions privately; keep the reader simple. Legacy `--presentation evidence-pack` remains explicit, and strict mode cannot bypass evidence requirements through layout selection.

```bash
python -m educational_research.cli --topic "your topic" --output-dir outputs/topic
python -m educational_research.cli --topic "your topic" --target-references 20 --source-semantics exact --output-dir outputs/twenty
# After actual reading/abstract review, resume with audited private sources, synthesis,
# original protocol and actual observations; the agent prepares these, not the user by hand.
python scripts/validate_research_pack.py outputs/twenty --strict
```

The Python CLI retrieves, validates and renders; the agent performs critical reading and prepares honest source/synthesis records. Do not claim a topic-only CLI downloads and understands twenty full papers automatically. External access limits may leave a useful provisional PDF. Strict CLI exits 3 after saving diagnostics; strict validator also rejects incomplete substantive acceptance.

A 100-word request gives no copying permission. Assess access, processing, retention and public reproduction separately. Record an actual licence or specific quotation basis addressing purpose, necessity, amount and acknowledgement. Verified open licences or documented permission can allow >=100 words; do not impose a blind 20-word ceiling. Without sufficient justification print only permitted original words and “Original words shown: X/100 - insufficient due to [specific reason]”. Such a source is PROVISIONAL and fails its display gate. Never fabricate the rest or claim an overall PASS. Abstracts of 85 words remain 85/100; an allowed 120-word abstract can pass the display gate while remaining ABSTRACT ONLY and never a deep full-text reading. The independent PDF validator must verify actual printed quotations, identity/version and rights for each source. Publish no protected originals, student documents or private audits.

中文：主 PDF 每篇须直接展示至少100个可核对的作者原文英文词，前提是许可或具体引用依据充分；不足则只展示合法数量并明示 X/100 与原因。私下核对、AI解释及推论不算。原文在前，自己的批判性使用仅一两句。摘要始终标明 ABSTRACT ONLY，不冒充全文审读。保持五部分、黑白衬线排版与原生验证流程。
