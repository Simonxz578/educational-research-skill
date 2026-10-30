---
name: educational-research
description: Research education topics and theory, compare original source arguments, develop bounded gaps and literature-led frameworks, plan studies, and audit substantive manuscripts. Produces a source-rich research roadmap with private evidence audits. Use for research and evidence work, not simple proofreading or isolated reference formatting.
---

# Educational Research / 教育研究

Deliver a concise `Research_Roadmap.pdf` plus a short note; complete editable provenance and audits live in `evidence/`. Use the companion Python package (`python -m pip install -e .`). Default academic prose is British English; follow the user's language. A target manuscript word count sizes discovery, never a generated essay.

## Interpret quantity before research

A topic alone targets **at least ten** distinct highly relevant scholarly works. Explicit N overrides the word-count heuristic. “20 papers/use 20 references/20篇文献” maps to `--target-references 20` (exact by default); “exactly 12” adds `--source-semantics exact`; “at least 25/至少25篇” adds `--source-semantics at_least`. Preserve the original request with `--user-quantity-intent`. These are agent interpretation duties; the CLI does not parse chat magically. Without an explicit N, use ceil(target_words/100) with a floor of ten. Ten is not a hidden maximum.

Substantive acceptance needs max(10, effective target N, any higher expressly required reading threshold) independent deep readings. Twenty requested with ten genuine full texts and ten abstracts is a **ten-work shortfall**, never a pass or twenty selected works. Do not pad. Count selected works, qualified readings and public micro-excerpts separately.

## Native two-stage workflow

1. **Scope and discover.** Follow [research protocol](references/research-protocol.md) and [ERIC/Scholar](references/eric-and-google-scholar-search.md). Write prospective RQs, population/stage/context, constructs/outcomes, rival explanations, eligibility, synonyms/descriptors and quantity intent. Run actual ERIC searches and lawful Scholar observations/exports. Preserve exact dated receipts. Search broader than N; expand adaptively within a declared budget. Plans and Crossref/OpenAlex enrichment are not Scholar searches.
2. **Obtain and read the required primary texts.** Use [full-text reading](references/full-text-reading.md) and [quotation policy](references/source-evidence-and-quotation-policy.md). Read the actual lawful work/relevant theoretical chapter, not an abstract or one paragraph. For each selected source prepare at least four meaningful checked anchors: author thesis/definition; method/mechanism; finding/reasoning; limitation/counterpoint. Each records an exact private span, precise locator, contextual paraphrase, author warrant and distinct researcher inference. Use `assets/source.schema.json`. Abstract/metadata-only discoveries remain private candidates, not selected reader entries.
3. **Construct a connected argument.** Use [gap/argument method](references/gap-and-argument-method.md). Each main chain compares two independent reviewed works, explains agreement/qualification/tension, gives a warrant and counterargument, and states our qualified inference separately. Challenge the gap against the closest work. Make a paragraph roadmap connecting claims, sources, theory, RQ and methods; do not generate a long review by default.
4. **Build explanatory theory and congruent methods.** Read [framework builder](references/framework-builder.md), and [feasibility](references/study-design-feasibility.md) for empirical proposals. Compare candidate lenses privately; show the selected parsimonious framework in the reader PDF. Define distinct constructs, proposed/source-grounded relations, disconfirming evidence and measure/code/analysis alignment. Audit drift bidirectionally through title, problem, RQ, author claims, gap, theory, measures, analysis and contribution.
5. **Run and inspect the native roadmap.** Re-run with reviewed `--sources`, `--synthesis`, original `--protocol` and `--discovery-records`. Read [reader model](references/roadmap-reader-view.md), [reader output contract](references/compact-pdf-output-contract.md) and [quality gates](references/research-quality-gates.md). Run the native validator and inspect actual first/dense/framework/middle/last previews. Repair findings, not font sizes. The default is plain A4 monochrome Times: reader logic, original evidence blocks, comparative synthesis, framework, writing roadmap and all selected APA references. No internal score/QA dump. Use `--presentation evidence-pack` for legacy output; `--include-audit-pdf` explicitly adds the detailed PDF under evidence/.

```bash
python -m educational_research.cli --topic "your topic" --mode discover --output-dir outputs/discovery
python -m educational_research.cli --topic "your scoped topic" --target-references 20 --source-semantics exact --user-quantity-intent "Review 20 papers" --offline --sources private/sources.json --synthesis private/synthesis.json --protocol private/protocol.json --discovery-records private/observations.json --strict-quality-gates --output-dir outputs/reviewed
python scripts/validate_research_pack.py outputs/reviewed --strict
```

An initial metadata-only discovery is not task completion: continue lawful access and close reading where possible. If blocked, return a useful provisional roadmap with factual K/N and explicit access/search shortfalls, never fabricated quotations or novelty. Source-rich micro-excerpts reproduce at most 20 words per copyrighted work across the entire reader PDF unless verified rights explicitly permit more. One or two authentic fragments plus close paraphrases suffice; private exact spans are not automatically publishable.

G1–G5, APA verification, nullable bibliometrics and editorial limits remain in force. Strict mode saves diagnostics and exits 3 when acceptance is incomplete. Source author position, observed/tested/reported evidence and our inference remain distinct. Synthetic fixtures can test structure but never establish real reading, Scholar discovery or originality. `audit/revise` adds source-traced surgical repair preserving voice. `draft`/`--include-draft` permits a separate scaffold; substantive writing requires an explicit request and no invented data.

中文：默认至少十篇；明确“20篇”就以二十篇为目标，并要求二十篇真正全文审读，不能用十篇摘要凑数。“至少N篇”与“恰好N篇”分别映射 at_least / exact，保留用户原话。先合法检索、取得全文并逐篇核对，再产出研究路线图；资料不足就如实显示 K/N 和缺口。主 PDF 展示原文微引语、细读解释、作者间的论证关系、理论框架与写作路径，完整审计保存在 evidence/。不默认代写长文，不公开私人文稿、学生材料或版权全文。
