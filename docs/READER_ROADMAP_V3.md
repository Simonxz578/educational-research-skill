Historical v0.3 contract. The current five-section reader and 100-word/acquisition requirements are described in [v0.4.2](FULL_TEXT_ACCESS_V042.md).

# Reader roadmap v3: design, source quotas and migration

## Two products, one default reader PDF

The native pipeline separates `Research_Roadmap.pdf` and a concise README from `evidence/`, which contains all editable source/argument/reading/novelty/framework/alignment/CSL/discovery/gate/QA artifacts. `Reader_View.json` is a derived, validated projection of actual selected evidence; it does not generate unsupported source claims. `Source_Selection.json` records the single quantity contract. `Candidates.json` retains unqualified discoveries/access gaps. All original 15 source-matrix groups and aliases remain available privately.

Reader sequence: THE RESEARCH LOGIC → THE AUTHORS' ORIGINAL EVIDENCE → FROM EVIDENCE TO ARGUMENT → THEORETICAL / CONCEPTUAL FRAMEWORK → RESEARCH / WRITING ROADMAP → SELECTED APA 7 REFERENCES. Internal scores, five-gate tables, metric dumps and exhaustive methods diagnostics are not printed in the reader layer. The selected lens and strongest reason are visible; alternative theory comparisons stay in the audit. Source author position, actual reasoning/evidence/limitations and our inference remain distinct.

## Quantity semantics

Explicit N overrides word count. `--target-references N` means exact selection unless `--source-semantics at_least` is supplied. Without explicit N, `ceil(target_words/100)` has a floor of ten and default at-least semantics. Additional genuinely qualifying supplied sources can be included: ten is not a hidden maximum. An exact request below ten may select that many but cannot earn substantive acceptance below ten independent reviews.

The agent records natural-language intent with `--user-quantity-intent`; the CLI handles explicit flags, not unannounced chat parsing. Protocol and amendments, selection, G2, receipt, QA, reader and references retain requested_user_N, requested_semantics, selection_target_N, deep_review_requirement_N, verified_relevant_selected_K, qualified_deep_read_K, selected/deep shortfalls and quotation_count. N=20 and K=10 deep readings is a ten-work shortfall, not a satisfied generic ten-work gate. Selected works, deep readings and public excerpts are separate counts.

Candidate breadth is adaptive: general, theory and recent queries preserve scope filters; additional contrary/expanded queries respond to distinct candidate shortfalls within a declared budget. Logs preserve requested rows, retrieved/distinct counts, expansion reasons and stop bounds. Candidate retrieval is neither full-text access nor semantic reading. Actual ERIC receipts and permitted Scholar observations are still required for substantive acceptance.

## Primary-text reader eligibility

A selected roadmap work needs verified identity, high reviewed relevance, independent-work identity, actual lawful full-text/version/file/SHA256/read provenance and four meaningful checked roles: thesis/definition, method/mechanism, result/reasoning, limitation/boundary/counterpoint. Theoretical chapters use conceptual roles without invented empirical samples. ReadingEvidence adds exact_span, context, author_warrant and researcher_inference. Exact spans are private; unchanged raw source text cannot masquerade as paraphrase.

One or two minimal verified original excerpts appear where rights permit, with known locators. The default work-level reproduced budget remains 20 words across the reader PDF; explicit verified rights are needed for larger reproduction. An abstract, invented quote/page, mismatched digest, repeated anchor, unreviewed permissions or low relevance prevents promotion. No-reproduction rights can support traceable paraphrases with an honest zero excerpt count. The independent validator checks reader wording/locators against actual source extractions, blocks and references against selected IDs, source/reading/excerpt counters, budgets and sealed receipts. Code cannot certify external authenticity, interpretative correctness or journal acceptance.

## Inspected visual contract

The supplied local preview was inspected for layout only; none of its personal/topic content or PDF assets is published. The public MIT style authority is personalised-practice-generator v0.4.0. Current style-guide blob `1f780617041592f1373503298b877c720c44a501` and geometry blob `2b4e54faf886bfbf51b1b5fe1d9719320d295ea3` were re-read from GitHub. Geometry matches previously inspected commit `0f658aa0f7f6da8c072bcf596db06248aa59adbe`.

A4 portrait, white background, black serif text and subtle grey rules. Installed Times New Roman/Liberation Serif; no raw font files redistributed. Outer text/diagram bounds 56.7–538.6 pt (ReportLab's frame padding is explicitly compensated); content top 56.7 pt, bottom 48.2 pt; header 9 pt with rule at 42.5 pt from top; centred 8 pt folio at 27 pt from bottom. Title 18 pt; sections 12 pt; body 10.5/14 pt; locators >=9.5 pt. Source blocks are unboxed, kept together and followed by restrained rules. References are balanced over continuation pages to avoid a single stranded final citation. The framework is a vector diagram; directed mechanism/causal/feedback relations get arrows, while observational associations do not acquire causal arrows. Proposed links remain dashed.

The diagram and text use the native renderer, not a detached report shortcut. Exact page count adapts to the supplied evidence and title lengths; the three-page preview is a visual language, not a fixed page cap. Public ten/twenty-source examples are new, generated synthetic content and marked TEST ONLY. Protected originals, private reference PDFs and complete user texts never enter public commits.

## Compatibility and strict behavior

Default CLI and Python Config presentation is now `roadmap`; root output/paths have intentionally changed. Choose `--presentation evidence-pack` to retain v0.2 `Educational_Research_Essentials.pdf` and root aliases. `--include-audit-pdf` explicitly adds the detailed report under evidence/. Validators and visual-review recording accept the root output directory for either layout. The original v2 tests continue under the explicit compatibility presentation.

v1/v2 source inputs still load. They do not automatically acquire the richer v3 reading anchors/permissions; keep them as candidates or use compatibility output until actual rereading adds the missing fields. Source schema defaults to 3.0 and reader/selection schemas are separately supplied. `audit.passed` remains deprecated layout compatibility; CLI reports layout_passed and research_status explicitly. Strict mode saves honest diagnostics and exits 3 for incomplete quality (including synthetic fixtures), 2 for input errors, 1 for layout failures. All five gates remain machine-readable and human-reviewable. G2 derives its count dynamically from the user's target; G5 checks both evidence and reader products. Missing bibliometrics remain null/unverified internally and are not presented as publication scores.
