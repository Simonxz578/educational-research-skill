# Validation record — 2026-10-29

Checks executed locally with Python 3.12.14 on macOS. These are observed results, not claims about future CI runs or exhaustive scientific validity.

| Check | Observed result |
|---|---|
| Offline pytest suite | 24 passed; 1 live test intentionally skipped |
| Opt-in live pytest smoke | 1 passed (real ERIC + Crossref requests); 24 deselected |
| Ruff | Passed |
| Canonical Codex skill validator | Passed |
| Public-file hygiene scan | Passed; no source manuscript accessed or uploaded |
| 10-source synthetic pack | 13 A4 pages; all 10 matrix entries; one PDF; 20 exact short excerpts; no page-bound errors |
| 100-source synthetic pack | 95 A4 pages; all 100 matrix entries; one PDF; 200 exact short excerpts; no page-bound errors |
| Output pack validator | Passed for both synthetic loads |
| Editable install | Installed and ran the real CLI |
| sdist + wheel | Built; wheel installed in a separate temporary target and CLI ran outside the source checkout |
| Live end-to-end CLI | ERIC general/theory/recent queries, Crossref matching, OpenAlex citations/FWCI, 3 matched references; abstract-only evidence; Scholar explicitly not checked |

Visual review: actual first/dense/middle/last preview images were inspected for the 10-source and 100-source reports, including Times typography, matrix continuation headers, full compact arguments, quotation locators, hanging references and centred page numbers. All pages also underwent text-bounds/font/page checks. CJK source rendering and native PDF ingestion were exercised in the automated suite. Representative public reference PDF pages were inspected from the independently cloned style repository; no reference PDFs or fonts are redistributed.

Regression tests cover manuscript-length-to-quota mapping; exact spans, locators and copyright budgets; wrong quotes and abstract-only quote rejection; DOI metadata/year conflicts and deduplication; missing-metric redistribution; relevance-first ranking and protected counterarguments; attribution boundaries; cycle detection; overclaim/gap calibration; preserved contradiction edges; APA 21+ authors, organisation/book formatting, alphabetical ordering and DOI links; bidirectional citation checks; retry/cache/offline failure; genuine user-attested Scholar export provenance; compact 10/100-source pagination; no default draft; explicit drafting scaffold; private-text omission from ledgers; and complete matrix/bibliography source IDs.

The live integration encountered real rate limits and used the implemented retry logic. Crossref matching does not itself establish publisher/VoR authenticity, full-text validity or complete retraction coverage. Source interpretation, legal access, research design, novelty and complex citation disambiguation require agent/human review. PyMuPDF emitted upstream SWIG deprecation warnings; these did not fail tests. Google Scholar was not searched by the CLI, and JCR was not accessed. Synthetic fixtures cannot support real scholarly claims.
