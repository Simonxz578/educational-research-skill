# v0.3.0 observed validation — 30 October 2026

This report records executed checks, not scholarly acceptance. Baseline v0.2: 47 passed, one deliberately skipped live check. Final v3 offline suite: **62 passed, one skipped**, with five upstream PyMuPDF/SWIG deprecation warnings. The skip is the opt-in live test. The separate network-enabled live run passed: **one passed, 62 deselected**. Its initial sandbox-only attempt skipped with ERIC ConnectError; that skip was not relabelled as a pass. No live Google Scholar search or ten/twenty authentic full-text research corpus is claimed.

## Commands and outcomes

Commands below used Python 3.12 from the local virtual environment; `python` denotes that interpreter.

| Executed command/check | Observed result |
|---|---|
| `python -m pytest -q` | 62 passed, 1 opt-in live skip |
| `python -m ruff check .` | Passed |
| `RUN_LIVE_TESTS=1 python -m pytest -q -m live -rs` with network access | 1 passed; actual ERIC receipt and Crossref DOI smoke |
| `python scripts/generate_quality_example.py --count 10 --output outputs/roadmap-v3-10` | Native roadmap, 9 pages, 10 selected, 10 qualified fixture readings, 20 checked fixture micro-excerpts |
| Same generator with `--count 20 --output outputs/roadmap-v3-20` | Native roadmap, 15 pages, 20 selected, 20 qualified fixture readings, 40 checked fixture micro-excerpts |
| `python scripts/validate_research_pack.py outputs/roadmap-v3-10` and twenty-source counterpart | Both structurally valid, no errors; synthetic overall status remains PARTIAL |
| `python scripts/generate_examples.py --count 100 --output outputs/regression-v3` and native validator | 100 entries, 96-page explicit legacy evidence-pack, layout/structural checks passed |
| `python -m educational_research.cli --topic 'Reading comprehension in secondary education' --target-references 20 --offline --strict-quality-gates --output-dir outputs/incomplete-v3-real` | Exit **3** after saving provisional PDF/evidence; zero selected, zero readings, shortfall 20; structural validator passed |
| Twenty requested, ten qualifying full-text fixtures plus ten abstracts | Strict exit **3**, G2 FAIL, exactly ten selected and ten-work deep-review shortfall; ten abstract-only candidates retained |
| Exact 12 / at least 12 from 20 qualifying fixtures / exact 25 from 30 | 12 / 20 / 25 selected, no truncation at ten |
| `python -m build --no-isolation` | Wheel and source distribution built at version 0.3.0 |
| Install wheel with `pip install --no-deps --upgrade --target /private/tmp/educational-v3-installed ...0.3.0-py3-none-any.whl`; run CLI from `/private/tmp` | Imported installed module outside checkout; version 0.3.0; default roadmap saved; strict incomplete request exited 3 |
| Canonical skill `quick_validate.py` | Passed |
| `python scripts/check_public_files.py` and `git diff --check` | Passed; only the two explicitly permitted generated synthetic PDFs are public |

## Actual PDF review

Automated native inspection checked **every page** for fonts, geometry, glyphs, links, overflow, required sections and source identities. Tests independently require black text, Times/Liberation Serif, >=9.5 pt content/locators, canonical 56.7–538.6 pt horizontal bounds and complete N source blocks plus N references. Body uses 10.5 pt / 14 pt leading; section headings 12 pt; title 18 pt; running header 9 pt and centred folio 8 pt. No raster pictures, decorative cards or audit tables appear in the reader layer. Page count is adaptive, not fixed to the private three-page reference.

Actual rendered images were viewed, not merely generated:

| Sample | First | Densest | Framework | Middle | Last |
|---|---:|---:|---:|---:|---:|
| Ten-source (9 pages) | 1 | 6 | 7 | 5 | 9 |
| Twenty-source (15 pages) | 1 | 11 | 12 | 8 | 15 |

Visual review found and repaired stranded argument/section headings and a final-reference orphan. Final views show readable open source blocks, matching black/white serif geometry, intact diagram labels, consistent footers and balanced complete references. Tests now check that a section heading is followed by substantive same-page text. The reviewer attestations, PDF hashes and actual image hashes are retained privately in each native evidence/Visual_Review.json and sealed receipt. The public samples are the inspected final PDFs. No user PDF, private topic text or proprietary font is distributed.

## Coverage and limits

The v3 tests cover dynamic quotas and word-count precedence; exact/at-least semantics; candidate exclusion; four independent primary-text anchors; wrong/repeated spans and quote limits; theoretical anchors; low relevance; complete references; monochrome geometry; honest discovery; reader wording tampering; consistent counters; optional audit PDF; and originating Chinese quantity intent with preserved protocol amendments. Existing v2 semantic regressions retain independent comparisons, negative evidence, closest-study challenges, construct drift, theory fit, mixed-methods validity, metadata provenance, native receipts and migration. Existing output-path tests explicitly choose the documented `evidence-pack` compatibility mode because the default root layout intentionally changes in v3.

These tests establish executable contracts and rendering behaviour. Synthetic sources and observations do not establish genuine scholarly evidence, comprehension, lawful external ownership, complete literature coverage, verified Scholar discovery, novelty, expert interpretation or journal acceptance. Real substantive use still requires lawful full texts, authentic discovery observations, critical reading, source-grounded inputs and expert review. Computational provenance protects consistency and traceability; it cannot independently certify human truthfulness or semantic judgement. Public examples remain prominently TEST ONLY and PROVISIONAL.
