# Educational Research Skill

An education-first Codex skill and Python toolkit for traceable literature research. Deliver one compact evidence PDF with editable records: scoped questions, bounded research gaps, opposing arguments, a ranked source/evidence/author-argument matrix and APA 7 references. A potential paper's word count sets the discovery target, never an essay quota.

The toolkit performs real ERIC retrieval, conservative Crossref matching, optional OpenAlex/Semantic Scholar citation enrichment, safe Scholar query planning/import, validated extraction, ranking and PDF rendering. The agent performs critical reading and prepares source-linked interpretations. Without reviewed source content, outputs remain qualified metadata/abstract candidates; it never invents quotations or gaps.

## Install

Python 3.11+ and installed Times New Roman or Liberation Serif are required. On Debian/Ubuntu install `fonts-liberation`; on macOS Times New Roman is normally available. Set `RESEARCH_FONT_DIR` if fonts live elsewhere. No fonts are bundled.

```bash
git clone https://github.com/Simonxz578/educational-research-skill.git
cd educational-research-skill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Open the repository in Codex. The discoverable skill is [`.agents/skills/educational-research/SKILL.md`](.agents/skills/educational-research/SKILL.md), following [official skill conventions](https://learn.chatgpt.com/docs/build-skills). For use from another project, install the Python package and copy that skill folder into your discoverable skills directory; copying the skill alone does not install the Python runtime.

## Run

```bash
# Live research: 10-reference verification target; actual shortfall disclosed
python -m educational_research.cli --topic "library learning" --target-words 1000 --mode full --output-dir outputs/live

# Larger prospective dissertation: target 100 references, not 10,000 words of AI prose
python -m educational_research.cli --topic "library learning" --target-words 10000 --mode full --output-dir outputs/dissertation

# Deterministic TEST ONLY example: no actual scholarly references
python -m educational_research.cli --topic "library learning" --offline --sources tests/fixtures/verified_fixture.json --output-dir outputs/example

# Critical reading done by the agent: validated extraction and synthesis inputs
python -m educational_research.cli --topic "your topic" --offline --sources private/sources.json --synthesis private/synthesis.json --output-dir outputs/reviewed

# Surgical audit map for an existing draft
python -m educational_research.cli --input private/draft.md --mode audit --offline --sources private/sources.json --output-dir outputs/audit

python scripts/validate_research_pack.py outputs/example
python scripts/inspect_pdf.py outputs/example/Educational_Research_Essentials.pdf --previews outputs/example/previews
```

`--target-references` overrides `ceil(target_words/100)`. Additional scope flags include `--rq`, `--descriptor` (repeatable), `--education-level`, `--context`, `--geography`, `--methodology`, `--framework`, `--author-thesis`, date bounds, inclusion/exclusion rules and language. `--providers eric,google-scholar` selects default discovery routes without enrichment. `--metrics jif,quartile,article-citations` expresses requested fields; unavailable metrics remain unverified, never guessed.

ERIC's documented API uses subject descriptors and explicit context filters. Query logs include actual results and failed expansions. Scholar has no bulk scraper: query plans are `GOOGLE_SCHOLAR_NOT_CHECKED`; use permitted interactive/manual searches or `--scholar-csv`. [CSV format](examples/scholar_observations.csv) requires observation provenance and marks imports as user-attested. For substantive reasoning, follow the canonical skill and prepare private JSON against its source/argument schemas. [A synthetic source example](tests/fixtures/verified_fixture.json) demonstrates the shape; all example citations are fictional and TEST ONLY.

Modes `discover`, `search`, `synthesise`, `gap`, `outline`, `audit`, `revise`, `full` share the concise pack contract. Analysis depth depends on the source/synthesis inputs and the agent's reading; changing a mode flag cannot manufacture analysis. `draft` or `--include-draft` explicitly enables a separate source-linked Markdown scaffold. The skill directs the agent to write substantive prose only when expressly requested. The CLI does not manufacture a completed manuscript.

## Outputs

- `Educational_Research_Essentials.pdf`: A–F focus, gaps, debate chains, full compact matrix, APA bibliography, verification notes.
- Matrix CSV/JSON, verified CSL, unresolved references, evidence ledger, argument graph, gap comparisons and metrics.
- Prospective protocol, exact search/HTTP logs, provenance, exclusions, Scholar plan, revision map, `audit.json`, `QA_Report.md` and preview images.

The default renderer rejects overlong analytical cells, repeats source headers across page breaks and uses readable 9.5 pt multi-line records. Protected source text is not reproduced in ledgers. Outputs/caches/private inputs are ignored by git. Automatic layout checks do not replace visual inspection or critical scientific review.

Scores use relevance 45 / evidence quality 20 / journal influence 15 / article impact 10 / argumentative value 10. Missing categories are null, with the available denominator and rescaling disclosed. Method and argument scores require reviewed assessments; journal/article metrics require named provenance. Journal JIF is never an article impact factor. Null/contrary/foundation work is deliberately retained. Source claims, evidence and researcher interpretation occupy distinct fields.

## 中文快速开始

本技能用于教育研究、文献检索、研究空白、理论框架、作者论证与文稿证据审计。默认产出一份精炼 PDF 和可编辑的证据记录，不按目标论文的字数代写文章。1000 字对应 10 篇参考文献的检索目标；10000 字对应 100 篇，数量不足或未核验会如实说明。

在 Codex 中打开仓库后，可说：“使用 educational-research，研究图书馆学习，目标论文 1000 字，检索 10 篇文献，提供研究空白与证据/论证矩阵。”英文研究文本默认英式英语；可要求中文。先运行检索，再由智能体阅读合法全文或摘要并建立可追溯记录。无法访问 Scholar 时会提供手动查询计划，不冒称已检索；无全文时不捏造原文引语。真实文稿与运行输出不要提交到公开仓库。

## Validation and limits

```bash
python -m pytest -q                  # offline tests; live smoke explicitly skipped
python -m ruff check .
RUN_LIVE_TESTS=1 python -m pytest -q -m live
python scripts/generate_examples.py --count 100 --output outputs/synthetic-100
```

Live tests can skip on actual service/network unavailability; a skip is not a pass. Public examples use synthetic unrelated library-learning material and never constitute scholarly evidence. [Architecture](docs/ARCHITECTURE.md) explains the agent/Python boundary; [provenance and limitations](docs/PROVENANCE_AND_LIMITATIONS.md) covers publisher checks, copyright, metrics, citation-audit limits and font support. [Validation report](docs/VALIDATION.md) records actual release checks. Original code is MIT; third-party styles, quotations and fonts retain their licences.
