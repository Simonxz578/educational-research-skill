# v0.4.2 observed validation — 30 October 2026

This is an engineering and evidence-status report, not a claim of publishability or journal endorsement. Baseline v0.3 was clean at commit `51981eb`: 62 tests passed and one opt-in live test skipped. The updated offline suite records **106 passed, one skipped**, with five upstream PyMuPDF/SWIG deprecation warnings. The separate network-enabled ERIC/Crossref check records **one passed, 106 deselected**. Synthetic test results are kept distinct from the actual single-work OA acquisition and reading below.

## Executed checks

Commands used the Python 3.12 project virtual environment. `python` denotes that interpreter.

| Executed command/check | Observed result |
|---|---|
| `python -m pytest -q` | 106 passed, one deliberate opt-in live skip |
| `python -m ruff check .` | Passed |
| `RUN_LIVE_TESTS=1 python -m pytest -q -m live -rs`, with network access | One passed; actual ERIC response and Crossref DOI identity smoke; not a Scholar search |
| `python scripts/generate_quality_example.py --count 10 --output outputs/roadmap-v042-10` | Native default reader, 8 pages, ten selected and ten qualifying fixture readings, twenty micro-excerpts |
| Same generator with `--count 20 --output outputs/roadmap-v042-20` | Native reader, 14 pages, twenty selected and twenty qualifying fixture readings, forty micro-excerpts |
| Native validator on both generated folders | Structurally valid with no errors; scientific status remains TEST ONLY/PARTIAL |
| `python scripts/generate_examples.py --count 100 --output outputs/regression-v042` and native validator | 100 records, 96-page explicit legacy layout, structural/layout checks passed |
| `python -m build --no-isolation` | Source distribution and wheel built at version 0.4.2 |
| Install wheel with `pip install --no-deps --upgrade --target /private/tmp/educational-v042-installed ...0.4.2-py3-none-any.whl`; import/run from `/private/tmp` | Installed module imported outside checkout; native default PDF and private access outputs saved; incomplete twenty-work request returned strict exit 3 |
| Canonical skill `quick_validate.py` | Passed |
| `python scripts/check_public_files.py` and `git diff --check` | Passed; public PDFs are explicitly permitted, generated synthetic previews only |

GitHub CI independently runs pytest, Ruff, public-file checks and native ten/twenty-source generation/validation on Python 3.11 and 3.12. The publication handoff reports the actual run result and commit; the local checks above do not stand in for remote CI.

## Adversarial coverage

Twenty-eight acquisition tests use deterministic `httpx.MockTransport` responses. They distinguish metadata/OA pointers from actual readable PDF/HTML/JATS, and those machine states from close reading. They exercise DOI/abstract-only content, fake PDF/login HTML, 403 denial, 429 Retry-After with no path retry and an independent fallback, readable generated PDF, full publisher HTML, repository AAM versus VoR, unknown version, broken/scanned or oversized resources, user permission uncertainty, robots denial, credential/private URLs, redirects, changed artifact/version, current DOI-only Unpaywall lookup and optional-provider non-execution. Generated test documents are TEST ONLY, not authentic scholarly full texts.

Thirteen evidence tests and three integration tests cover per-source 99 versus 100 English words; exclusion of quotes, metadata and our inference; repeated-word/phrase padding and duplicated boilerplate; cumulative fragments reused in argument prose; a refuted gap; disconnected diagram nodes; unavailable required non-users; actual native five-section PDF representation; HTML spans split by markup; non-synthetic acquisition omission; strict legacy-quality bypass; and ERIC-hosted pointers without a DOI. Existing v2/v3 quantity, source/quote/digest/locator, argument/novelty/framework/design, complete matrix/receipt and migration regressions also run.

Testing found and repaired real defects: an extended abstract could spoof completeness with body keywords; an unrelated article could mention the requested title in related work; JATS front matter initially lost authors; native HTML markup broke exact-span matching; repeated quoted fragments in integration were missing from per-work accounting; and a provider-loop indentation regression suppressed OpenAlex pointers. The regression fixtures now reject or correctly process these cases. A machine lexical/structure check still cannot certify truthful external ownership or scholarly interpretation.

## Actual lawful OA retrieval and close reading

The native `Acquirer` fetched [Ritchie, Della Sala and McIntosh (2013)](https://doi.org/10.1371/journal.pone.0078976) from the public PLOS article HTML. Crossref title/authors/year/DOI matched. The publisher's open-access attribution notice and Crossref licence provenance were retained privately; the robots/content route check succeeded with HTTP 200. Actual HTML—not an abstract, DOI page alone or converted PDF—contained both experiments, methods/results, General Discussion and Conclusions. Native hierarchical locators distinguish repeated headings across experiments. The original HTML and extracted text have separate retained SHA-256 records.

An agent then read the actual article body and made **seven checked anchors**, not an automatically generated reading record. The four reader paraphrases supply **131 qualifying English words**; the separate inference, bibliographic metadata, locators and short quotes do not count. Two authentic fragments total **11 quotation units**, within the default twenty-word policy. The record preserves different allocation levels, adjusted findings, the initial covariate sensitivity, and a rival mechanism rather than converting the result into universal causal proof. Cited works and supplementary files were not independently reviewed or reanalysed.

The actual native CLI was run with that private reviewed source and `--offline --strict-quality-gates --output-dir outputs/v042-real-reviewed`. It saved the reader and complete evidence, selected **one** work, recorded **1/10** qualified coverage and a shortfall of **nine**, and exited **3**. The ordinary validator accepted its honest structural output; `python scripts/validate_research_pack.py outputs/v042-real-reviewed --strict` exited **1**, reporting that substantive acceptance was not achieved. This is the expected negative result. No authentic ten/twenty-work corpus, Phoenix study completion, Scholar observation, novel gap or publication-quality acceptance is claimed. The real article, private input records and actual observations are not committed.

## Actual PDF inspection

The house geometry and serif hierarchy remain unchanged: A4, white/black, fine grey rules, outer text bounds approximately 56.7–538.6 pt, 10.5 pt / 14 pt body, 12 pt sections, 18 pt title, >=9.5 pt analytical content/locators, 9 pt header and centred 8 pt folio. No decorative cards, colours, rating widgets, audit tables or source PDFs are introduced. The reader has exactly five sections; the framework and compact roadmap share the fourth section.

Native inspection checks every page for bounds, fonts, glyphs, links, source IDs and required sections. Tests independently check complete source blocks, all APA references and actual source paraphrases in the PDF. Every synthetic source independently supplies **128–136** qualifying evidence words. Twenty longer papers cannot compensate for one short paper. A 99-word genuine explanation remains visible and provisional, without padding.

Actual images were viewed for both samples:

| Sample | First | Dense | Framework | Middle | Final |
|---|---:|---:|---:|---:|---:|
| Ten-source, 8 pages | 1 | 6 | 7 | 5 | 8 |
| Twenty-source, 14 pages | 1 | 11 | 12 | 8 | 14 |

Final re-rendered image hashes matched the images actually inspected. The source blocks are open three-part analytical units, the diagram is legible, reference continuation is balanced and footers remain consistent. Private `Visual_Review.json` attestations and sealed native receipts record the actual PDF/image hashes. Public v0.4.2 sample PDFs are these inspected final synthetic outputs; older v3 previews remain historical examples.

## External limitations and scientific boundary

CORE and DOI-Unpaywall adapters are deterministically tested but were not live-executed with operator credentials/contact configuration. No credentials were solicited or invented. No Scholar automated access, institutional subscription, user library login, CAPTCHA workaround, shadow-library route or paid access is claimed. Provider terms, authentication, rate limits, available OA copies and version/licence metadata remain external constraints. Unknown rights/version and denied routes produce private actionable handoffs rather than abstract substitutions.

Online auto/revalidate checks actual resources again; static local hashes cannot detect an unobserved later remote change. Acquired files/extractions must still match the exact reading version. A validated acquisition never fabricates critical reading, interpretations or public excerpts. Structural tests, word floors, provenance and native gate results support traceability; research validity, semantic accuracy and journal suitability require real reading and expert review.
