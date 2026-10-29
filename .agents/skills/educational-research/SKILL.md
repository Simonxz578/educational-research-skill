---
name: educational-research
description: Research education topics and theory, search literature, critically compare source arguments, build bounded gaps and literature-led frameworks, plan studies, and audit or revise substantive manuscripts with traceable evidence. Use for research and evidence audits, not simple proofreading or isolated reference formatting.
---

# Educational Research / 教育研究

Produce a compact evidence pack, not a manuscript-length essay. British English is the academic default; follow the user's language. A proposed paper's word count sizes discovery only: ceil(words/100). This skill requires the companion Python package (`python -m pip install -e .` from its repository). Keep real texts, observations and outputs private.

## Native workflow

1. **Scope before search.** Use [research-protocol](references/research-protocol.md). Record 1–3 competing RQs, focal constructs/population/stage/context, rival explanations, eligibility, synonyms/descriptors and a prospective timestamp. `--protocol` supplies the agent-refined record. Do not silently substitute a near-synonym outcome or assume institutional access.
2. **Discover honestly.** Follow [ERIC/Scholar](references/eric-and-google-scholar-search.md). Run the real CLI. Preserve actual ERIC response receipts; use lawful Scholar UI/manual observations or genuine exports with exact queries, UTC timestamps, filters, results and hashed artifacts. A plan/legacy CSV alone is not a verified search. On resume supply the original protocol and `--discovery-records`. Missing access stays provisional.
3. **Read primary content.** Follow [close-reading](references/full-text-reading.md) and [quotation policy](references/source-evidence-and-quotation-policy.md). Create private source JSON against `assets/source.schema.json`. Full-text status needs a hashed, lawful, versioned document plus substantive claim/method/result/limitation passages where applicable. Read the actual work/relevant theoretical chapter; one paragraph or an abstract is insufficient. Preserve source-author claim, source evidence and target-author inference as different layers.
4. **Construct an argument and challenge novelty.** Use [gap/argument method](references/gap-and-argument-method.md). Compare at least two independent deeply reviewed works per major claim; preserve negative/opposing findings. Challenge the contribution against the 5–10 closest works when available. Reject cosmetic novelty or an already-answered question. Use `assets/argument.schema.json`; never invent synthesis to fill a template.
5. **Build explanatory theory and matched methods.** Read [framework construction](references/framework-builder.md) and, for empirical proposals, [method fit](references/study-design-feasibility.md). Compare plausible lenses, select a parsimonious explanation, define distinct constructs and source-linked relationships, and map theory → RQ → evidence → measures/coding → analysis. Use `assets/framework.schema.json`. Proposed associations and sensitising concepts are not identified causal effects.
6. **Run native acceptance and review.** Re-run the CLI with the reviewed sources, synthesis, original protocol and discovery receipts. Read [quality gates](references/research-quality-gates.md), [output contract](references/compact-pdf-output-contract.md), [APA](references/apa7-verification-policy.md) and [metrics](references/responsible-bibliometrics.md) as needed. Use the native renderer; a custom attractive PDF cannot substitute. Run the validator and inspect actual first/dense/framework/middle/last PNGs; repair findings before delivery. State blocked services, reading shortfall and remaining interpretive judgements.

```bash
python -m educational_research.cli --topic "your topic" --mode discover --output-dir outputs/discovery
python -m educational_research.cli --topic "your scoped topic" --mode full --offline --sources private/sources.json --synthesis private/synthesis.json --protocol private/protocol.json --discovery-records private/observations.json --strict-quality-gates --output-dir outputs/reviewed
python scripts/validate_research_pack.py outputs/reviewed --strict
```

## Completion boundaries

`full`, `synthesise`, `gap`, `outline`, `framework`, and substantive `audit/revise` require G1–G5: real ERIC + auditable Scholar discovery; at least ten relevant deeply reviewed full texts; comparative author arguments; a closest-work novelty challenge; and native complete deliverables/QA. Missing evidence produces `PROVISIONAL - NOT FULLY VERIFIED`. `--strict-quality-gates` saves diagnostics and exits 3 when acceptance is incomplete. Reducing the full-text threshold or selecting exploratory quality cannot bypass strict substantive requirements.

`discover/search` deliver provisional candidates, not completed substantive research. `framework` develops/audits the same native schema and pack. `audit/revise` additionally use `--input` for a surgical line-addressed edit map; the agent performs actual source/theory/citation repair while preserving author voice. `draft`/`--include-draft` permits a separate scaffold; write substantive prose only after an explicit writing request, with no invented data/methods.

Automatic editorial scores are provisional. `EDITORIALLY_READY_FOR_EXPERT_REVIEW` requires documented assessment, all applicable gates, and critical scores >=3/4; it never means published, publishable or peer reviewed. Python checks structure, provenance and consistency; the agent must actually read, compare and judge. Never relabel a declared reading or a hashed human observation as independently authenticated fact.

中文：默认交付精炼研究资料包。全文不足十篇、Scholar 未核验、论证缺少独立来源、研究空白被最接近的论文覆盖、理论未用于测量或分析时，必须保留未完成状态。区分原作者论点、证据与自己的推论；识别题目—构念—问卷/编码的漂移。混合方法须有独立 QUAN/QUAL 问题和明确整合，不能用“访谈加一些数字”冒充。所有真实全文、学生材料、检索观察与输出保存在忽略目录，不提交公开仓库。
