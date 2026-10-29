# v0.2.0 validation — 2026-10-29

Observed local checks, Python 3.12.14 on macOS. Synthetic structural results are not real scholarly research, and neither code nor editorial scores guarantee publication.

| Executed check | Result |
|---|---|
| Before implementation: existing pytest + native baseline example | 24 passed, 1 live test skipped; baseline example rendered |
| Final offline regression suite | 47 passed, 1 live test intentionally skipped |
| Separate opt-in live ERIC/Crossref smoke | 1 passed, 47 deselected |
| Ruff | Passed |
| Canonical skill validator | Passed |
| Public-file hygiene scan / git whitespace check | Passed; no private manuscripts, student records, real full texts or credentials included |
| Native v2 synthetic close-reading pack | 19 A4 pages, 10 fully traceable TEST ONLY works; G1–G5 structurally PASS; overall PARTIAL because synthetic |
| Native 100-source regression pack | 96 A4 pages; all sources/matrix/reference IDs retained; provisional, incomplete substantive analysis |
| Real native CLI demonstration | ERIC general/theory/recent queries actually executed, Crossref matched identities, OpenAlex metrics observed; 3 abstract-only matched works; strict exit 3 and overall PARTIAL |
| Pack validator | Structurally valid synthetic and real provisional packs; strict validation rejects incomplete/synthetic acceptance |
| Build/install | sdist and wheel built; wheel installed separately and CLI exercised outside source checkout; strict mode saved provisional diagnostics and exited 3 |

Real run gates: G1 PARTIAL (Google Scholar not checked), G2 FAIL (0 qualified deep full-text reviews against 10 required), G3 FAIL (no comparative source-grounded argument/framework), G4 FAIL (no warranted closest-study novelty claim), G5 PASS (native complete deliverables and automated QA). This is evidence that a legitimate metadata search cannot masquerade as completed substantive research. No actual ten-paper research corpus or genuine Scholar observation was invented.

Synthetic full-text test gates are explicitly TEST ONLY. Their source files, fake observations and timestamps are generated under ignored output/test directories with synthetic flags; all production acceptance remains blocked for these fixtures. They test eligibility logic, document hashes, exact passage checks and schema/graph consistency, not scientific comprehension, authentic database searches or originality.

Regression coverage includes T01–T20: absent ERIC logs; Scholar plans/legacy imports without actual artifacts; 15 metadata records; 9 vs 10 full texts; lowered-threshold non-bypass; wrong/missing full-text passages/digests; independent-work attribution; preserved opposing findings; novelty dissolved by closest work; cosmetic novelty; title/RQ/measurement drift; access/capability/participation boundaries; decorative/stacked lenses; counterfeit mixed methods and a conditionally valid unequal-sample mixed plan; partial custom PDF/CSV rejection; inherited APA/DOI/author/year/conflict/metric tests; small type/bad links; versioned visual-review attestations; legacy migrations; synthetic guards; post hoc edited gate reports; schema-level rejection of unsupported overall PASS; editorial critical-score/readiness limits; complete 10/100-source flow pagination and no default essay.

Visual QA inspected actual first, framework, dense matrix, middle and last images of the 19-page synthetic pack, representative pages of the 96-page regression pack and the seven-page real provisional pack. Readable 9.5 pt matrix text, hypothesis dash style, construct alignment, continuation headers, provisional/test-only labels, APA reference layout and page numbering were reviewed. Every page also received automated geometry/bounds/glyph/font/section/source checks. External links were checked for valid syntax/internal destinations; general external URL reachability was NOT claimed offline. Full-text access/legal provenance and editorial interpretations still require genuine agent/expert review.

Methodological references: Jabareen publisher full text was accessible; SAGE verified Creswell/Plano Clark's third edition and September 2017 date, without a claim to reading the complete book. Fetters/Curry/Creswell DOI metadata and an open repository copy were identified; publisher/PMC pages encountered access/CAPTCHA restrictions and were not represented as successfully read. No CAPTCHA or paywall was bypassed. JCR was not accessed. Upstream PyMuPDF SWIG deprecation warnings did not fail the checks.

Exact representative commands executed:

```bash
python -m pytest -q
python -m ruff check .
RUN_LIVE_TESTS=1 python -m pytest -q -m live -rs
python scripts/generate_quality_example.py --output outputs/v2-quality
python scripts/generate_examples.py --count 100 --output outputs/v2-synthetic-100
python scripts/validate_research_pack.py outputs/v2-quality
python scripts/validate_research_pack.py outputs/v2-synthetic-100
python -m educational_research.cli --topic 'reading comprehension' --target-references 3 --descriptor 'Reading Comprehension' --peer-reviewed --providers eric,google-scholar,crossref,openalex --strict-quality-gates --output-dir outputs/v2-live
python scripts/validate_research_pack.py outputs/v2-live
python scripts/check_public_files.py
python -m build --no-isolation
```

Actual native CLI commands and Python QA calls/results are also recorded in each private Execution_Receipt.json. Visual_Review.json preserves inspected image/PDF digests and reviewer notes; rereunning the engine archives stale reviews. Repository output files remain ignored and are not published as real scholarly material.
