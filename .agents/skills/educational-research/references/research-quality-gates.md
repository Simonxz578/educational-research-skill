# Five gates, scientific judgement and delivery

Every native pack writes Research_Quality_Gates.json and a human-readable QA report. PASS/PARTIAL/FAIL/BLOCKED/NOT_APPLICABLE are evidence states, not aesthetic grades. Overall research PASS requires all applicable hard gates and a non-synthetic substantive run. Synthetic fixtures can satisfy structural tests but never certify actual discovery or research validity. `audit.passed` remains a deprecated v1 layout flag; use `research_passed` and `overall_status`.

G1: recorded ERIC API responses plus dated lawful Scholar observations, exact query/filters/IDs/counts and preserved artifact digests; original prospective protocol must predate searches. Cached data is labelled ERIC_CACHED rather than a new execution. Resume with original protocol and archived observations. A manually constructed query URL, Crossref record, legacy CSV without an export artifact or a fabricated retrospective log does not establish discovery. Missing providers block/partially satisfy G1. Digests test integrity, not independent human authenticity.

G2: >=10 distinct highly relevant works with verified identity, lawful versioned full-text files, reader/time/scope, central thesis, precise content locators and checked substantive sections. Whole work or a justified theoretical chapter, not a fragment. Empirical/review records need claim/method/result/limitation coverage; theoretical records use appropriate conceptual evidence. Lowering `--min-reviewed-fulltexts` never grants strict coverage. Authors/versions of one work are not independent studies. Metadata resolution never promotes text access.

G3: 3–7 major comparative claims, two independent qualified works each, attributed author positions and passage IDs, agreement/tension, warrant W#, objection O#, own inference, scope, relative strength and RQ/theory/paragraph links. Negative evidence declared in reading records must survive as evidence-linked graph relations or explicit opposing passages. Framework and conditional method-fit must pass. These checks cannot prove interpretation is correct.

G4: closest-study matrix, strongest novelty-destroying rival, content evidence, specific surviving contribution and search/confidence boundary. GAP_SUPPORTED / GAP_NARROW_BUT_DEFENSIBLE / GAP_NOT_SUPPORTED / INSUFFICIENT_EVIDENCE. A previous answer plus no substantive remainder yields NOVELTY_NOT_SUPPORTED. Country/population/terminology/mixed-methods substitutions alone fail. Author-claimed, researcher-inferred and empirically checked gaps remain distinct.

G5: actual native CLI and renderer receipt; complete 15-group matrix, bibliography/IDs, reading/argument/novelty/framework/alignment outputs, all page QA, links and artifact digests. `scripts/validate_research_pack.py` checks aliases, hashes and independently recomputes gates; `--strict` rejects provisional acceptance. Handwritten reduced-CSV/custom-PDF substitutes fail. Structural validation may accept an honest provisional pack without claiming research completion.

Editorial audit: 0 absent/fabricated; 1 superficial; 2 partial; 3 strong with qualifications; 4 rigorous and traceable with credible counterarguments. Critical source accuracy, novelty, theory-fit and method-fit <=2 block readiness. Scores need rationale/evidence/judgement calls; automatic scores cannot claim human assessment. Readiness means ready FOR expert review, never guaranteed acceptance.


# Reader-first gate extensions (v3)

G1 retains real auditable ERIC/Scholar requirements and honest plans/caches/imports. Candidate breadth expands after duplicates/shortfall within a stated budget; it is never a completeness guarantee.

G2 derives its required count from the effective user selection target: max(10,N,any higher explicitly required reading threshold). N=20 with ten full texts plus ten abstracts fails with a ten-work shortfall. Source count, qualified reading count and reproduced-excerpt count are different. Four distinct substantive anchor roles, private exact spans, context, author warrant, own inference, rights and precise locators govern roadmap promotion. Low assessed relevance cannot pad the corpus.

G3 requires independent reviewed-source comparisons, visible source-author vs own inference, warrants/counterpoints and paragraph-level links into the roadmap; G4 still challenges the proposed gap against closest work. Unsupported frameworks/claims remain in the private audit rather than becoming confident reader content.

G5 validates BOTH layers: complete 15-group evidence data and native Research_Roadmap.pdf, exactly one block and a full reference for every selected work, exact/at-least count semantics, consistent K/N/reading/quotation/shortfall values, source-linked wording/locators, per-work budgets, framework, source IDs, links, previews and receipts. The compatibility evidence-pack remains explicit. Automated structural eligibility and recorded visual inspection are not expert endorsement or journal acceptance.
