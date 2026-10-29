---
name: educational-research
description: Research education topics, educational theory and policy, learning sciences, pedagogy and teacher development; search literature, compare source arguments, establish bounded gaps, plan papers, audit evidence and revise manuscripts with traceability. Use for substantial research or evidence audits, not simple proofreading or isolated reference formatting.
---

# Educational Research / 教育研究

Turn a topic or reading pack into a concise, traceable research pack. Default academic language is British English; follow the user's requested language. A proposed manuscript word count sizes the reference search (ceil(words/100)), never the length of generated prose. `full` is a research pack. Write a separate paper only when explicitly requested.

## Operate

Locate the repository root containing `pyproject.toml`; install `python -m pip install -e .` in a Python 3.11+ environment. This skill depends on the companion package: copying this folder alone requires installing the repository package separately.

1. Scope the topic using [research-protocol](references/research-protocol.md). A topic alone is enough to start: propose up to three competing RQs, choose a provisional one, record assumptions and prospective inclusion criteria before searching. Distinguish practical problem, scholarly puzzle, conceptual tension, gap and contribution.
2. Read [ERIC and Scholar](references/eric-and-google-scholar-search.md). ERIC and permitted manual/interactive Google Scholar are the default discovery routes. Run the CLI to retrieve candidates and write logs. Inspect output, expand synonyms/descriptors and scope filters, preserve search boundaries. Do not call Scholar searched unless dated observations exist. Metadata indexes enrich identity; they do not replace Scholar.
3. Critically read lawfully accessible source content. Use [quotation policy](references/source-evidence-and-quotation-policy.md) and `assets/source.schema.json`. Build private source JSON with evidence segments and attributed extractions. A source author's claim, its evidential warrant and the target author's independent interpretation are separate fields. An ERIC abstract is not full text. Review quotations and licensing yourself; exact-span checks cannot establish external authenticity.
4. Compare actual methods, contexts, populations, stages, theories and rival explanations. Apply [gap and argument method](references/gap-and-argument-method.md), [bibliometrics](references/responsible-bibliometrics.md) and [APA verification](references/apa7-verification-policy.md). Build a private synthesis JSON against `assets/argument.schema.json`. Never infer consensus, causal effectiveness or originality from search absence, journal prestige or self-reported perceptions.
5. Re-run with `--sources private/sources.json --synthesis private/synthesis.json`. Use `--offline` only to disable retrieval; it never claims a live search. Supply `--rq`, context, framework and criteria once scoped. Do not overwrite a careful extraction with speculative source summaries.
6. Deliver `Educational_Research_Essentials.pdf`, CSV/JSON matrix and the external evidence/search/audit files. Read [output contract](references/compact-pdf-output-contract.md) and [house style](references/pdf-house-style.md). Run `python scripts/validate_research_pack.py outputs/run`; inspect representative preview PNGs and every programmatic page finding. Correct compact text rather than shrink type or clip arguments.

```bash
python -m educational_research.cli --topic "library learning" --target-words 1000 --mode full --output-dir outputs/run
python -m educational_research.cli --topic "library learning" --offline --sources private/sources.json --synthesis private/synthesis.json --output-dir outputs/reviewed
python -m educational_research.cli --input private/draft.md --mode audit --offline --sources private/sources.json --output-dir outputs/audit
```

## Modes and honest handoff

- `discover/search`: scope and retrieve; report candidates and verification shortfall. Do not imply complete critical synthesis.
- `synthesise/gap/outline`: read source records and author a source-linked synthesis input; the deterministic CLI validates and renders it. Missing analysis is labelled unconstructed.
- `audit/revise`: inspect actual draft and sources; use the line-addressed revision map, then propose/apply surgical, source-linked edits preserving author voice. The CLI does not silently rewrite prose. Check obsolete RQs, theoretical overload, construct drift, uncited arguments and source-author attribution beyond lexical flags.
- `full`: all research essentials, one PDF, no essay. `draft` or `--include-draft` permits a separate Markdown scaffold; the agent writes substantive prose only after an explicit writing request, using verified evidence without invented methods/data.

中文：默认交付研究资料包，不代写论文。先界定问题，检索 ERIC 与合规的 Scholar 渠道，再逐篇核对论点、证据与自己的推论。无法核验的全文、引文、指标和研究空白必须标明；不凑参考文献数量。所有真实文稿、全文和检索运行文件保存在私有输出目录，不提交到公开仓库。
