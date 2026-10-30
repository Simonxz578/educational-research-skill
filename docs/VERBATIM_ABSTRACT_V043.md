# v0.4.3: original-word inspection and honest abstract fallback

The approved reader geometry and five-section product stay unchanged. This release replaces the v0.4.2 explanation-writing floor with an actual original-text inspection gate and makes verified abstracts eligible reader sources.

## Three evidence layers

`core/evidence_types.py` defines VERBATIM_PRIMARY_TEXT, SOURCE_ANCHORED_EXPLANATION and OUR_INTERPRETATION. Their counts have different meanings. Only matched exact original spans can satisfy full-text inspection; explanation length has no minimum quota. Historical private `primary_evidence_words` fields in the reader now describe inspected original source words, not a promise of AI-authored “original evidence”. Explicit `verified_original_words`, explanation/interpretation counts, typed scope and layers remove ambiguity. An abstract's raw source-word count remains scoped ABSTRACT_ONLY and grants zero full-text credit.

`core/verification.py` matches four meaningful checked roles in the retained version. NFKC, ordinary punctuation and whitespace canonicalisation reconcile typography without accepting invented words. Source artifact/extraction digests, actual URL/version, exact locator, canonical character offsets, attributed claim and reader/date/scope are persisted in the private Full_Text_Reading_Audit. Counts use distinct non-overlapping English word positions, not unique vocabulary. Repeated/overlapping/ambiguous spans, source mixing, absent text and wrong version/digest fail. Title/metadata/references are excluded. Position/identity checks are not a semantic proof or independent authenticity certification.

Rights records separate access, processing, private retention and public quotation. Unresolved processing/retention prevents original-text inspection; forbidden-retention reading spans are not copied to the delivered private ledger. Original texts and real observations remain uncommitted. Private inspection gives no onward-publication right. Normally <=20 reproduced words per work apply across source, argument and framework prose, including repetitions. Verified licence or explicit permission can support a documented higher allowance while keeping the reader compact.

## Automatic abstract fallback

`fulltext/abstracts.py` prefers an actual publisher abstract, then genuine Crossref/ERIC indexed text tied to the exact paper. A raw unverified abstract string or DOI alone cannot promote a work. Retained abstract records include publication identity, URL/provider/version, artifact/extraction hashes, checked date/scope, separate rights and optional checked explanation/quotation. No genuine abstract means a metadata-only private candidate.

ABSTRACT ONLY works are visibly included when relevant. The native default explanation is deliberately conservative: literal topical mentions/link and an explicit full-text boundary, not inferred methods or findings. The agent reads available abstracts and supplies faithful checked explanations without a per-paper user negotiation. If the abstract reports a method but no result, no result is fabricated. Quotation requires separate permission; otherwise explanation and link suffice. The 100-word full-text rule is NOT APPLICABLE / NOT FULL-TEXT VERIFIED for abstracts of any length.

Source_Selection and the reader report included_N, full_text_verified_K, abstract_only_A, any provisional full-text tier and unfilled requested-item shortfall. The existing qualified_deep_read_K and deep-review shortfall remain strict full-text counters. Explicit essential/landmark/foundational roles preserve important paywalled works in an exact-N selection instead of maximising a gate score. Metadata/relevance screening and independent-work deduplication remain in force.

## Gates, reader and compatibility

G1 still needs actual discovery observations. G2 retains max(10,N,higher explicit minimum) independent qualified full-text reviews, now with the real original-word gate. Abstracts never satisfy it. Three-to-five connected arguments remain the target; an abstract-supported comparison must be explicitly PRELIMINARY_ABSTRACT and cannot earn full-text or novelty acceptance. G4 cannot prove a gap from unreviewed closest works. Unsupported frameworks remain provisional. G5 validates the actual included source blocks, complete references, wording/scope/counters, every-page geometry and native receipts.

A twenty-item request with thirteen full texts plus seven genuine abstracts produces twenty reader blocks/references and a seven-work strict full-text shortfall. The provisional PDF is still useful and saved. Strict CLI returns3; strict validator returns nonzero. Five reader sections, monochrome serif styling, readable type, private fifteen-group audits and explicit legacy layouts are preserved.

Old source schemas still load; previous explanation counts do not substitute for exact original spans. New source/reader/abstract/rights schemas describe v0.4.3. Source URLs, original-version locators and scope must be retained, especially for repository AAMs and publisher/indexed abstracts. A manual source can include `abstract_evidence` prepared by the native retention helper; its text/digests/scope must validate. `explanation_checked` is an explicit reviewer attestation, not an automatic semantic guarantee.

See the [validation report](V043_VALIDATION.md) for actual commands, live versus synthetic outcomes and limits. A genuine retained OA reading and a genuine indexed abstract illustrate the new distinction; neither establishes an authentic ten/twenty-paper corpus or journal-ready research.
