# Educational Research Skill

Version **0.4.3** builds one readable, source-traceable `Research_Roadmap.pdf`. It preserves the approved A4 monochrome Times/Liberation Serif design and five sections: research logic; what authors establish; argument integration/closest-study challenge; framework/roadmap; APA references. Technical records stay privately in `evidence/`.

The agent reads and critically compares actual sources. Python discovers lawful routes, verifies documents and source spans, retains honest abstract fallbacks, enforces gates and renders. A successful download or fluent explanation is never proof of a completed reading or publication quality.

## Install and begin

Use Python 3.11+ and installed Times New Roman or Liberation Serif (`fonts-liberation` on Debian/Ubuntu). No font files are redistributed.

```bash
git clone https://github.com/Simonxz578/educational-research-skill.git
cd educational-research-skill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'

# Topic alone: at least ten relevant works, with honest evidence tiers
python -m educational_research.cli --topic 'Retrieval practice in education' --output-dir outputs/topic

# Exactly twenty relevant works; no abstract-to-full-text promotion
python -m educational_research.cli --topic 'Retrieval practice in education' --target-references 20 --source-semantics exact --output-dir outputs/twenty
```

Open this repository in Codex to use [the canonical skill](.agents/skills/educational-research/SKILL.md). “Use educational-research on [topic], 20 papers” gives the agent the scope and quantity; a prior chat or extra prompt template is unnecessary. The CLI itself does not understand chat or critically read twenty papers. The agent continues acquisition/reading and supplies audited private `--sources`/`--synthesis`, preserving original `--protocol` and `--discovery-records`, rather than asking the user to repair every paper manually.

## Original author words are different from explanation

Each full-text-qualified source needs at least **100 actual English author-word positions**, privately verified across four independently meaningful spans: thesis/definition, method/mechanism, finding/reasoning and limitation/counterpoint. Native verification matches the retained version, hashes, URL/identity, precise locator and canonical start/end offsets. Title, metadata, references, repeated/overlapping spans, other papers, explanations and our inference cannot inflate that count.

`VERBATIM_PRIMARY_TEXT`, `SOURCE_ANCHORED_EXPLANATION` and `OUR_INTERPRETATION` have separate typed fields/counts. There is **no second 100-word AI-writing quota**. The reader shows concise explanation explicitly labelled as paraphrase, only authentic permitted short excerpts as original words, and a distinct use/boundary. Private inspection never authorises reproduction of those hundred words.

## Genuine abstracts remain useful

Bounded lawful publisher/ERIC/repository/OA routes are tried first. When full text or permitted processing is unavailable, the native pipeline retrieves and identity-checks the actual publisher or authentic indexed abstract. It retains a relevant paper as **ABSTRACT ONLY**, with provenance and a link; metadata without a real verified abstract stays private. It never invents unseen methods, findings, limitations, pages or four deep-reading anchors.

The agent can supply a checked faithful abstract explanation. Without one, the native projection conservatively reports only literal topical mentions/link, never manufactured outcomes. Public quotation is separately reviewed; an unreviewed copyright scope means no quote. The abstract's actual length is recorded, while its full-text inspection gate is **NOT APPLICABLE / NOT FULL-TEXT VERIFIED**.

Count included N, qualified full texts K, abstracts A and unfilled requested items separately. A request for twenty can produce **13 full texts + 7 abstracts, 20 items and references**; strict G2 still fails with seven missing deep reviews. Default N is at least ten; explicit N overrides word-count sizing, and `--source-semantics at_least` permits more. Essential/landmark works are not discarded solely to improve the full-text score. Abstracts may support explicitly preliminary comparisons, never unqualified full-text or originality claims.

## Rights, validation and compatibility

Access, processing, private retention and public quotation are separately recorded. The conservative public budget normally remains <=20 source words per work in aggregate, including repeated fragments. Verified licence/explicit permission can support a larger documented allowance. There is no universal hundred-word copying entitlement. No institutional login is inherited; denied/CAPTCHA/uncertain-rights routes stop. Optional provider credentials remain in environment variables, and no Scholar scraper is provided. [Access architecture](docs/FULL_TEXT_ACCESS_V042.md) remains applicable with the [v0.4.3 policy changes](docs/VERBATIM_ABSTRACT_V043.md).

G1–G5, all fifteen evidence dimensions, native receipts, full-text inspection, complete references, argument/novelty/framework checks and every-page PDF QA remain operational. Strict CLI saves honest provisional outputs then exits **3**; `python scripts/validate_research_pack.py outputs/twenty --strict` rejects incomplete acceptance. `--presentation evidence-pack` preserves explicit legacy output; `--include-audit-pdf` adds the detailed PDF only when requested. Missing access or abstract evidence remains a shortfall, never padding.

Synthetic previews: [ten full-text fixtures](examples/roadmap-v043-10.pdf) and [twenty works: thirteen full-text plus seven abstract fixtures](examples/roadmap-v043-20.pdf). All are prominently TEST ONLY, not real scholarship. See [observed validation](docs/V043_VALIDATION.md) and [changelog](CHANGELOG.md).

## 中文

只给主题和数量即可开始。默认至少十篇；“20篇”就纳入二十篇相关作品，并分别报告全文、真实摘要和数量缺口。合法全文不可得时自动保留可核对的摘要，不让用户逐篇补材料；摘要绝不冒充全文审读。全文门槛是私下核对四类真实原文锚点、至少100个不重复位置的作者英文词，不是要求AI写100词，更不是准许公开复制100词。原文、来源知情的解释与自己的推论分开标记，摘要只能支持受限初步判断。主 PDF 保持五部分和黑白衬线排版，完整审计与权限记录留在 evidence/。程序测试不等于学术有效性、期刊背书或保证发表。
