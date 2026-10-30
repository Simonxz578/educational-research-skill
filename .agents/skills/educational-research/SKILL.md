---
name: educational-research
description: Research education through checked original texts, retain genuine abstract-only fallbacks, compare authors, challenge gaps and build explanatory frameworks. Produces a readable research roadmap with private evidence audits. Use for substantive research and manuscript evidence work, not simple proofreading.
---

# Educational Research / 教育研究

Deliver one native `Research_Roadmap.pdf` and a one-paragraph note. Keep technical records private in `evidence/`. Preserve the approved A4 white/black Times layout and five sections: research logic; what authors establish; argument integration/closest-study challenge; framework/roadmap; APA references. Do not print audits, search errors, matrices or word-count dashboards. Use the installed companion Python package. Follow the user's language; default scholarly prose is British English.

## A topic and quantity are enough to begin

Interpret “20 papers/20篇” as `--target-references 20` (exact by default), “at least/至少” as `--source-semantics at_least`, and preserve original intent with `--user-quantity-intent`. Topic alone targets at least ten works; word-count discovery sizing has a floor of ten and explicit N wins. Select relevant independent works, preferring genuine full texts where equally relevant without discarding an essential paywalled work. Do not ask the user to repair every access gap manually.

Distinguish requested/included N, qualified FULL_TEXT_VERIFIED K, ABSTRACT_ONLY A and unfilled item shortfall. Abstracts are useful reader sources but never satisfy strict deep-reading requirements `max(10,N,any higher expressly required minimum)`. Twenty items with thirteen full texts and seven abstracts is twenty included, thirteen deep reviews and a strict full-text shortfall of seven. Never pad with unrelated or invented papers.

## Original wording, explanation and our inference

Read [verbatim inspection and abstract fallback](references/verbatim-and-abstract-policy.md). Maintain separate typed `VERBATIM_PRIMARY_TEXT`, `SOURCE_ANCHORED_EXPLANATION` and `OUR_INTERPRETATION` layers and counts. For each full-text-qualified work inspect at least 100 actual English author-word positions across four distinct meaningful anchors: thesis/definition, method/mechanism, findings/reasoning, limitation/counterevidence. Theoretical works use conceptual roles, not fictional samples. Count only exact checked original spans in the attached version; exclude title/metadata/references, duplicated/overlapping spans, other papers, explanation and our inference. There is NO second 100-word AI-writing quota. Keep explanations concise and article-specific.

Persist source ID/DOI, lawful route and URL, actual version, artifact/extraction digests, exact locators and canonical offsets, matching original text, attributed role/claim, reader/date/scope and separately assessed access, processing, private retention and public quotation rights. Unicode/whitespace normalisation may reconcile typography but never invent words. A download is not a reading. Machine checks cannot certify external truthfulness or interpretation.

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

Verification of 100 author words privately never licences their public reproduction. Use 1–2 short authentic fragments only when public quotation is reviewed/permitted, normally <=20 words per work across the entire PDF including repetition. Otherwise use faithful clearly labelled explanation plus a link. Verified CC BY/explicit permission can support a larger documented allowance, while still keeping the reader concise. Access, processing, retention and onward distribution are separate. Do not publish protected originals, private ledgers, observations, credentials or student records. Synthetic examples never establish real scholarship, Scholar discovery, novelty, journal endorsement or automatic publishability.

中文：只给主题和数量即可开始。默认至少十篇；“20篇”就纳入二十篇相关作品并如实区分全文与摘要。合法全文不可得时自动保留真实、可核对的摘要，不让用户逐篇补材料；摘要只能支持受限的初步判断，不能冒充全文审读。全文门槛是私下核对四类原文锚点、合计至少100个不重复位置的作者英文词；不是要求AI写100词，更不是准许公开复制100词。原文、来源知情的解释和自己的推论分别标记。主 PDF 保持五部分与黑白衬线排版，完整核查和权限记录留在 evidence/。
