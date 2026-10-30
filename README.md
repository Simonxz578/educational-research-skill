# Educational Research Skill

Build an evidence-rich **research argument roadmap** and an explanatory conceptual framework. Version 0.4.2 keeps the approved plain A4 monochrome Times layout and simplifies the reader to five sections. The default delivery is one `Research_Roadmap.pdf` plus a short note; full texts, provenance, comparisons and technical audits stay privately under `evidence/`.

The native engine discovers lawful full-text routes, validates actual documents, checks evidence contracts and renders the roadmap. The agent must still read the original works and critically compare their arguments. A successful download, resolved DOI or fluent summary is never recorded as a completed paper reading.

## Install

Python 3.11+ and installed Times New Roman or Liberation Serif are required. On Debian/Ubuntu install `fonts-liberation`. No font files are distributed.

```bash
git clone https://github.com/Simonxz578/educational-research-skill.git
cd educational-research-skill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Open the repository in Codex to use [the canonical skill](.agents/skills/educational-research/SKILL.md). Copying the skill elsewhere also requires installing the companion Python package.

## What the reader receives

1. **Research logic:** one focused problem/question, a provisional contribution and a short argument route.
2. **What the authors actually establish:** every selected work, grouped by debate, in three connected parts: original position and source-specific reasoning; evidence and its boundary; our separate use of the source.
3. **Argument integration and closest-study challenge:** three to five linked comparisons, counterarguments and the strongest potentially gap-destroying work. Refuted gaps remain refuted.
4. **Theoretical/conceptual framework and roadmap:** a connected vector figure, precise construct distinctions, a compact writing/research sequence and an essential feasibility gate/fallback where applicable.
5. **APA 7 references:** all selected verified works, with DOI or source links.

The PDF preserves the measured serif geometry, readable source blocks and fine monochrome rules. Pagination adapts to the evidence; no fixed page cap or smaller type compensates for weak editing. Search errors, candidate lists, hashes, scores, gates and the 15-group matrix are kept out of the reader PDF.

## Quantity and evidence depth

- Topic alone: at least **10** independently reviewed, highly relevant scholarly works. Ten is a floor, not a hidden maximum.
- `--target-references 20`: exactly 20 selected works by default; substantive acceptance requires 20 deep readings. `--source-semantics at_least` permits additional qualifying works.
- Without explicit N, use `ceil(target_words/100)` with a floor of ten. Explicit N overrides the word-count heuristic. The reading requirement is `max(10,N,any higher requested minimum)`.
- Each work needs at least **four distinct checked primary-text anchors** and its own **100 English words of substantive evidence explanation** in the reader PDF, normally around 100–140 words. Titles, references, locators, quotes and our independent inference do not fill that explanation quota. Works cannot average their word counts.
- A genuine but short explanation stays short and provisional. For example, 99 words cannot be padded or offset by another paper: the work can remain visible, but it does not meet the substantive depth gate.

The skill interprets English/Chinese quantity requests and preserves the user's actual words through `--user-quantity-intent`; the CLI does not parse chat by itself. Selected works, qualified deep readings and public excerpts have separate counters. Ten full texts plus ten abstracts cannot satisfy a twenty-work request.

## Two-stage workflow

```bash
# Stage 1: prospective scope, actual discovery and bounded lawful public acquisition.
# This remains provisional until the primary texts have actually been read.
python -m educational_research.cli --topic 'Retrieval practice in primary education' --target-references 20 --mode discover --full-text-mode auto --full-text-limit 30 --full-text-max-routes 8 --output-dir outputs/discovery

# The agent reads the obtained lawful texts and prepares genuine private sources/synthesis.
# Preserve the original protocol and actual observations when resuming.
python -m educational_research.cli --topic 'Retrieval practice in primary education' --target-references 20 --source-semantics exact --user-quantity-intent 'Review exactly 20 papers' --mode full --offline --sources private/sources.json --synthesis private/synthesis.json --protocol outputs/discovery/evidence/search_protocol.json --discovery-records outputs/discovery/evidence/Discovery_Observations.json --strict-quality-gates --output-dir outputs/reviewed

python scripts/validate_research_pack.py outputs/reviewed --strict
```

These are API usage examples, not claims that a twenty-paper corpus already exists. Stage two needs actual reviewed input records and their retained lawful artifacts. A source record includes validated acquisition, version/hash, reader/date, processing permission, precise source spans and locators, contextual paraphrases, the author's warrant, qualifications and our separate inference. Missing access, discovery or evidence remains a factual shortfall. Strict mode saves the useful provisional PDF and diagnostics before returning exit code **3**.

The default online `--full-text-mode auto` checks permitted publisher HTML/PDF/XML/JATS, actual ERIC-hosted files and identified repository versions. Crossref, OpenAlex, DOI-based Unpaywall and optional CORE provide metadata or lawful pointers; the underlying document must still pass content, identity, version and rights checks. Native HTML retains section/paragraph anchors without artificial PDF pagination. Repository AAM/preprint wording is kept distinct from unavailable VoR wording. `--full-text-mode revalidate` makes renewed route checks explicit; `--full-text-mode off` disables new acquisition and does not relax evidence requirements. Offline mode opens no network socket and can validate explicitly permitted local supplied documents.

Optional provider configuration stays in environment variables: `OPENALEX_API_KEY`, `UNPAYWALL_EMAIL`, and `CORE_API_KEY` together with `CORE_API_TERMS_ACCEPTED=1`. Never put actual values, passwords or authenticated links in Git. CORE remains unqueried without its configured key and explicit terms acknowledgement. Unpaywall uses DOI lookup; its retired search endpoint is not used. See [full-text access, permissions and migration](docs/FULL_TEXT_ACCESS_V042.md) for route limits, machine statuses and blocked-access handoffs.

Scholar observations remain lawful interactive/manual access or genuine exports; there is no Scholar scraper. A search plan is not a completed search. Preserve [actual observations](scripts/import_scholar_observation.py) and the original prospective protocol. Crossref/OpenAlex enrichment does not substitute for Scholar work or close reading. Impact factors, quartiles and citation metrics stay null/unverified without provenance.

## Private evidence and compatibility

`evidence/` retains `Full_Text_Access.json`, permitted local artifacts/extractions, `Full_Text_Access_Handoff.md`, source candidates, the full 15-group matrix, reading/quotation ledger, comparative arguments, novelty challenge, framework/alignment, CSL, discovery receipts, G1–G5, QA and native execution receipts. Blocked handoffs identify the work, attempted lawful routes, version/rights issues and a practical next action. No paper copy or real observation log belongs in the public repository.

The conservative public-output policy normally permits at most **20 verbatim source words per work in aggregate**, including a fragment repeated elsewhere in the reader. Verified permission is needed for a larger allowance. This is an internal policy, not a universal legal entitlement. User access to a PDF does not itself permit hosted AI processing or onward distribution. Private exact spans are not automatically publishable.

`--presentation evidence-pack` retains the detailed legacy PDF and root aliases; `--include-audit-pdf` explicitly adds that report inside `evidence/`. Strict quality checks remain substantive and do not become an acquisition/depth exemption through a legacy presentation flag. Older source schemas still load, but missing acquisition, permissions or richer anchors require real validation/rereading before native v0.4.2 reader acceptance. Other modes remain available; `audit`/`revise` requires `--input`, and drafting is explicit opt-in.

## Examples and validation

Public samples contain generated **SYNTHETIC / TEST ONLY** works, never private user research:

- [Ten-source roadmap](examples/roadmap-v042-10.pdf): 8 pages.
- [Twenty-source roadmap](examples/roadmap-v042-20.pdf): 14 pages.

Each sample source supplies 128–136 qualifying evidence words. Those fixtures test software behaviour, not real scholarship. Separately, the actual [Ritchie, Della Sala and McIntosh article](https://doi.org/10.1371/journal.pone.0078976) was retrieved as lawful publisher HTML and closely read for a one-work exemplar. That remains **1/10 and provisional**, with strict exit 3; it does not establish a ten/twenty-paper corpus, Scholar search or a defensible new gap.

```bash
python scripts/generate_quality_example.py --count 10 --output outputs/roadmap-10
python scripts/generate_quality_example.py --count 20 --output outputs/roadmap-20
python scripts/validate_research_pack.py outputs/roadmap-20
python -m pytest -q
python -m ruff check .
python -m build --no-isolation
RUN_LIVE_TESTS=1 python -m pytest -q -m live -rs
```

See the [observed v0.4.2 validation report](docs/V042_VALIDATION.md), [access architecture and migration](docs/FULL_TEXT_ACCESS_V042.md), [earlier quota design](docs/READER_ROADMAP_V3.md) and [changelog](CHANGELOG.md). Code checks supplement critical reading and expert review; they never establish automatic publishability, journal endorsement or research validity. Original code is MIT; source content, CSL styles and fonts retain their applicable rights.

## 中文快速开始

默认交付一份黑白衬线体研究路线图 PDF 和简短说明，全文、检索记录、完整矩阵及技术审计保存在私有 `evidence/`。正文只有五个部分：研究逻辑、作者实际建立的证据、比较论证与最近研究挑战、理论框架及研究/写作路径、完整 APA 参考文献。

只给主题时至少十篇；明确“20篇”就要求二十篇真正深读。“恰好N篇”用 exact，“至少N篇”用 at_least，并保留用户原话。每篇至少四个核实的原文锚点，且主 PDF 中逐篇至少一百个英文词解释真实证据；标题、引语和自己的推论不凑字数，篇间不能平均。内容不足就如实保留并显示暂定状态，不能拿十篇全文加十篇摘要冒充二十篇已读。

先合法检索和获取实际全文，再逐篇核对原文、方法、结果及限制，最后比较论证、挑战研究空白、构建解释性框架和可行路径。下载成功不等于读过；DOI、摘要、登录页和假 PDF 不等于全文。机构登录、个人阅读、AI 处理和再分发权限必须区分；不索取密码，不绕过付费墙或验证码。访问受阻时保留私有交接说明和真实 K/N，不捏造引语、数据、Scholar 检索或新颖性。
