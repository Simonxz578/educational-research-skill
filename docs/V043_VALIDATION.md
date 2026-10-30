# v0.4.3 observed validation

Executed on 30 October 2026 with Python 3.12. These are engineering checks, not a claim that an authentic ten- or twenty-paper review is complete or publishable.

## Automated checks

`python -m pytest -q`: **133 passed, 1 skipped**. The skip is the opt-in network check. Five upstream PyMuPDF/SWIG deprecation warnings remain. `RUN_LIVE_TESTS=1 python -m pytest -q -m live -rs`: **1 passed, 133 deselected**; actual public discovery responses were checked without inventing credentials. Ruff passes.

The new regression cases cover the requested T1–T16 behaviours:

| Requirement | Observed coverage |
| --- | --- |
| T1–T3: actual original words, not AI length | Long explanations cannot supply author words; short verified spans plus commentary fail; the real 100-word boundary is checked; concise explanations remain eligible. |
| T4–T5: authentic version and distinct passages | Wrong digest/version, invented/misattributed text, foreign-paper URLs, overlap, repetition, title/reference text and ambiguous spans cannot supply full-text credit. Unicode/whitespace normalisation remains exact at word level. |
| T6–T10: honest abstract fallback | Simulated blocked full text triggers native indexed-abstract retention. Genuine 95- and 130-word abstract fixtures remain ABSTRACT ONLY with a non-applicable full-text gate; an unverified string remains metadata; missing results stay missing. |
| T11–T12: argument scope and counts | Abstract comparisons require an explicit preliminary scope. Thirteen qualified full-text fixtures plus seven abstract fixtures give twenty reader entries/references, zero item shortfall and seven missing full-text readings. Essential abstract-only works are not displaced solely to raise the full-text score. |
| T13–T14: quotation rights | Exact quotation matching, separate abstract permissions, aggregate budgets and documented extended permission are checked. Private original-word inspection grants no public copying allowance. |
| T15: native reader and audit | Native CLI, G1–G5, fifteen evidence groups, receipt/hash validation and actual PDF wording/geometry are exercised. Abstracts never earn full-text/novelty acceptance. |
| T16: fresh context | A new run with only topic and target 20 uses mocked provider responses and native fallback to produce twenty correctly scoped abstract-only entries without prior chat or manual uploads. This deterministic case is not twenty live discoveries. |

Four older assertions were updated because the v0.4.2 AI-explanation word floor is deliberately superseded; their grounding and gate checks remain. Nested HTML cells and JATS abstract markup also have regressions against duplicate extracted words. Crossref verification no longer recursively embeds prior provenance.

## Native examples and visual inspection

Commands executed from the checkout:

```bash
python scripts/generate_quality_example.py --count 10 --output outputs/roadmap-v043-10
python scripts/generate_quality_example.py --count 20 --abstract-count 7 --output outputs/roadmap-v043-20
python scripts/validate_research_pack.py outputs/roadmap-v043-10
python scripts/validate_research_pack.py outputs/roadmap-v043-20
python scripts/validate_research_pack.py outputs/roadmap-v043-20 --strict
python scripts/generate_examples.py --count 100 --output outputs/regression-v043
python scripts/validate_research_pack.py outputs/regression-v043
```

Both quality examples pass ordinary native structural validation. The ten-item PDF has eight pages; the mixed twenty-item PDF has eleven. The mixed strict validator correctly exits **1** because substantive acceptance is incomplete; synthetic evidence never becomes an accepted scholarly review. The hundred-source legacy regression has 96 pages and passes structural validation.

The agent actually inspected final PNGs of the first, middle, densest, framework and final reference pages for both quality examples. The mixed sample's first ABSTRACT ONLY block was also visible on the inspected dense page. No clipping, overlapping prose, missing arrows or truncated references were observed. The five sections, A4 white/black serif design, readable paragraphs, paraphrase/original-word distinction and scope counters are preserved. Every page also passes the native geometry check. Private visual-review records retain image/PDF hashes and reviewer attestations; these attestations are not machine-proven visual judgements.

Only the two prominently **TEST ONLY / SYNTHETIC / NOT SCHOLARLY EVIDENCE** PDFs are copied to the public v0.4.3 examples. Public-file scanning separately checks those markers and rejects other protected/generated binaries and private paths.

## Genuine source checks, retained privately

An existing lawful CC BY OA reading, Ritchie and colleagues (2013), DOI `10.1371/journal.pone.0078976`, was revalidated against its retained original HTML. Four meaningful role spans match **435 distinct original English author-word positions**. Its 131-word explanation is a separate measure and does not provide those words. This is revalidation of a retained reading, not a claim of a fresh publisher download.

For Karpicke and Roediger's (2008) *The Critical Importance of Retrieval for Learning*, DOI `10.1126/science.1152408`, bounded acquisition returned `PAYWALL_OR_LOGIN_BLOCKED` after an access denial. Native fallback retained the actual **125-word Crossref-indexed published abstract**, and the agent read it and supplied a checked, faithful explanation. It remains ABSTRACT ONLY. No full-text methods or limitations were invented; no abstract quotation was emitted because quotation permission was not established. No login, CAPTCHA or paywall bypass was used.

The combined real-source run includes **one full-text-qualified source and one abstract-only source**. With the default ten-item target, its item shortfall is eight and strict full-text shortfall is nine. Ordinary native validation passes; strict CLI exits **3**, and strict validator exits **1**, as expected. These two sources do not demonstrate a complete real ten/twenty-paper corpus, Google Scholar coverage, novelty acceptance or journal publishability. Original artifacts, exact long spans, real provenance and private audit outputs are excluded from Git.

## Installed package checks

`python -m build --no-isolation` builds the 0.4.3 sdist and wheel. The wheel is installed with `--no-deps --target` into a temporary directory and imported from outside the checkout; its reported version is 0.4.3. Offline topic-only and explicit twenty-item runs preserve default/exact quantity intent, save provisional output and return strict exit **3**. A third installed-wheel run through the native CLI uses the mixed synthetic inputs and retains **20 included / 13 full texts / 7 abstracts**, with strict shortfall seven and exit **3**. Offline empty-corpus runs are quantity/error-path tests, not live discovery claims.

The GitHub workflow runs Python 3.11 and 3.12 tests, Ruff, public-file scanning and native example/validator checks. Its twenty-item job now exercises seven abstract fallbacks. The deployed commit's workflow result must be checked separately after pushing; a local test result is not a CI result.
