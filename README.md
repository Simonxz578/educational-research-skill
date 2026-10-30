# Educational Research Skill

Build a source-rich **research argument roadmap** and literature-led conceptual framework. The default is one plain A4 monochrome Times PDF, `Research_Roadmap.pdf`, plus a concise note. Complete evidence, provenance and quality audits stay in `evidence/`.

The agent performs lawful primary-text reading and critical interpretation. Python retrieves, validates, selects, formats and renders. A topic-only CLI call cannot magically complete a literature review: missing discovery or full text produces an honest provisional roadmap, not invented reading, quotes or novelty.

## Install

Python 3.11+ and installed Times New Roman or Liberation Serif are required. On Debian/Ubuntu install `fonts-liberation`. No font files are distributed.

```bash
git clone https://github.com/Simonxz578/educational-research-skill.git
cd educational-research-skill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Open the repository in Codex to use [the canonical skill](.agents/skills/educational-research/SKILL.md). Installing/copying the skill elsewhere also requires installing the companion package.

## Source quantity is an end-to-end contract

- Topic alone: at least 10 qualifying independent works; ten is a floor, not a hidden maximum.
- `--target-references 20`: exactly 20 selected works by default; strict G2 requires 20 deep readings.
- `--source-semantics at_least`: select at least N, including additional qualifying supplied works.
- Without explicit N, use `ceil(target_words/100)` with a floor of 10. Explicit N wins over word count.
- Substantive deep-review requirement is at least `max(10,N)`. Ten full texts plus ten abstracts cannot satisfy a twenty-work request. Missing sources are disclosed as K/N and a precise shortfall.

The skill interprets English/Chinese quantity requests and passes `--user-quantity-intent` to preserve the user's actual words. The CLI does not claim to parse natural-language chat.

## Two-stage workflow

```bash
# Stage 1: prospective scope and real discovery; provisional until primary texts are reviewed
python -m educational_research.cli --topic 'International students and university career-development support' --mode discover --output-dir outputs/discovery

# The agent obtains and critically reads lawful full texts, then prepares audited private inputs.
# Stage 2: exactly 20 sources, with original prospective protocol and actual discovery observations
python -m educational_research.cli --topic 'International students and career aspirations' --target-references 20 --source-semantics exact --user-quantity-intent 'Review 20 papers' --mode full --offline --sources private/sources.json --synthesis private/synthesis.json --protocol private/protocol.json --discovery-records private/observations.json --strict-quality-gates --output-dir outputs/reviewed

python scripts/validate_research_pack.py outputs/reviewed --strict
```

These are API usage examples, not claims that a genuine twenty-paper corpus exists. Source inputs need actual versioned/hashed lawful full text, reading provenance and at least four distinct checked anchors: author thesis/definition, method/mechanism, finding/reasoning, limitation/counterpoint. Each anchor includes an exact private span, contextual paraphrase, author warrant, own inference and precise locator. Abstracts remain follow-up candidates. The reader uses 1–2 authentic micro-excerpts where permitted, normally <=20 reproduced words per work across the entire PDF, plus close paraphrases. Full source text is not bundled or committed.

ERIC is the native discovery front door. Scholar uses lawful interactive/manual observations or actual exports; a query plan is not a completed search. [Import genuine observations](scripts/import_scholar_observation.py) with actual timestamps/artifacts; preserve the original protocol on resume. Adaptive candidate breadth is logged and bounded by `--search-candidate-budget`. Crossref/OpenAlex enrich identity/metrics; they do not substitute for Scholar or full-text reading. JIF, quartiles and article metrics remain null/unverified without provenance.

## Reader and audit layers

`Research_Roadmap.pdf` presents research logic, every selected author's checked original evidence, comparative chains, a narrow closest-study gap, the selected framework and a congruent writing/research plan, followed by all selected APA 7 references. Source blocks are open text with thin rules, not decorative cards. Pagination adapts to source count; it is not fixed to three pages. The private `evidence/` directory retains the full 15-group matrix, candidates, reading/quotation ledger, arguments, novelty challenge, framework and alignment, CSL, protocol/search receipts, G1–G5, QA and previews.

Five gates remain enforced: auditable discovery; required independent close readings; comparative arguments; closest-work novelty; and complete native outputs/QA. Strict mode saves diagnostics and exits 3 when acceptance is incomplete. Structural validation of synthetic examples never certifies genuine research or journal acceptance. The framework distinguishes source-grounded versus proposed relations and checks construct drift across title, problem, RQ, theory, measures/codes, analysis and contribution. Mixed methods needs defensible QUAN/QUAL purposes, integration and feasible access/fallback.

`--presentation evidence-pack` retains the v0.2 detailed PDF and root-level aliases. `--include-audit-pdf` explicitly adds it inside `evidence/` while retaining the reader PDF. Other modes (`search`, `synthesise`, `gap`, `outline`, `framework`, `audit`, `revise`, `full`) share the native architecture; audit/revise requires `--input`. Drafting remains explicit opt-in and never invents data.

## Synthetic previews and validation

Public examples are generated **TEST ONLY**, unrelated to user manuscripts, and cannot support scholarly claims:

- [Ten-source roadmap](examples/roadmap-v3-10.pdf)
- [Twenty-source roadmap](examples/roadmap-v3-20.pdf)

```bash
python scripts/generate_quality_example.py --count 10 --output outputs/roadmap-10
python scripts/generate_quality_example.py --count 20 --output outputs/roadmap-20
python scripts/validate_research_pack.py outputs/roadmap-20
python -m pytest -q
python -m ruff check .
RUN_LIVE_TESTS=1 python -m pytest -q -m live -rs
```

See [v3 design, quotas and migration](docs/READER_ROADMAP_V3.md), [observed validation results](docs/V3_VALIDATION.md) and [changelog](CHANGELOG.md). Original code is MIT; source content, CSL styles and fonts retain their applicable rights.

## 中文快速开始

默认交付精炼的研究路线图 PDF，完整审计保存在 `evidence/`。只给主题时至少十篇；明确“20篇”就以二十篇为目标并要求二十篇真正全文审读。“恰好N篇”用 exact，“至少N篇”用 at_least，保留用户原话。不能拿十篇全文加十篇摘要冒充二十篇已读文献。

先合法检索、取得全文、逐篇核对原文与论点，再构建作者间的比较论证、研究空白、理论框架和写作路径。原作者立场、实际证据和自己的推论分开标注。资料不足时显示 K/N 和缺口；不捏造引语、数据、全文访问、Scholar 检索或新颖性。默认不代写长篇文章，不公开私人文稿、学生材料或版权全文。
