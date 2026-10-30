# Educational Research Skill

Version **0.4.4** makes original author evidence the main body of the five-section `Research_Roadmap.pdf`. Each included work displays **at least 100 verified English author words wherever reproduction is justified**. Private inspection and AI explanation do not satisfy that display requirement.

Original passages appear first, with actual version and source-specific locators, followed by **OUR CRITICAL USE** in one or two sentences and a source link. The A4 monochrome Times/Liberation Serif layout, concise comparative arguments, closest-study challenge, conceptual framework and APA references remain. Technical evidence and the three typed original/explanation/inference layers stay private in `evidence/`.

## Begin

Python 3.11+ and Times New Roman or Liberation Serif are required (`fonts-liberation` on Ubuntu).

```bash
git clone https://github.com/Simonxz578/educational-research-skill.git
cd educational-research-skill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m educational_research.cli --topic "Your topic" --output-dir outputs/topic
python -m educational_research.cli --topic "Your topic" --target-references 20 --source-semantics exact --output-dir outputs/twenty
```

Open the repository in Codex and say “Use educational-research on [topic], 20 papers”. The [canonical skill](.agents/skills/educational-research/SKILL.md) works without this chat. The agent reads, assesses reproduction rights and prepares audited sources/synthesis; Python retrieves, checks and renders. A topic-only CLI run does not autonomously understand twenty papers. Resume real readings using private `--sources`, `--synthesis`, original `--protocol` and actual `--discovery-records`.

## Exact wording and lawful amounts

The finished-PDF validator independently matches printed quotations to source artifacts, identity/version, locators and distinct non-overlapping English word positions. An overall average, repeated quote, translation, title, reference, paraphrase or inference cannot make up a deficient source. Private full-text inspection remains a separate gate.

Access, processing, retention and public quotation require separate review. Record the actual licence or specific quotation basis, critical purpose, necessity/proportionality and acknowledgement. Reviewed open licences and explicit scoped permission can support larger excerpts; the old microquote ceiling is not imposed blindly. Without sufficient reproduction justification, show only permitted text and **Original words shown: X/100 - insufficient due to [reason]**. An honest shortfall is structurally valid but fails visible-word acceptance; strict CLI returns 3 after saving provisional outputs and strict validation rejects incomplete acceptance.

Lawful full-text acquisition precedes genuine publisher/indexed abstract fallback. Abstracts remain **ABSTRACT ONLY**: an allowed 85-word abstract displays 85/100; an allowed 120-word abstract can satisfy the display target while earning zero full-text deep-review credit. Unresolved reproduction rights yield no copied abstract wording. Metadata without a genuine abstract stays private. Twenty included works may be thirteen full texts plus seven abstracts; strict G2 still requires twenty independent full-text readings. No paywall bypass, inherited subscriptions, invented passages or publishability promises.

## Validation and previews

[Observed v0.4.4 checks](docs/V044_VALIDATION.md) distinguish engineering fixtures from genuine source checks. [Ten-source preview](examples/roadmap-v044-10.pdf) and [twenty-source mixed preview](examples/roadmap-v044-20.pdf) are prominently TEST ONLY synthetic sources. Private originals, student material, credentials and real audit artifacts are excluded from GitHub.

中文：每篇主 PDF 直接展示至少100个真实作者英文原文词，前提是引用许可或具体依据充分；不足时只展示合法数量，明示 X/100 和原因。原文在前，自己的批判性使用仅一两句。摘要标为 ABSTRACT ONLY，不能计入全文审读。私下核对或AI解释不满足可见原文字数要求。默认至少十篇，明确二十篇就按二十篇执行并如实报告覆盖缺口。
