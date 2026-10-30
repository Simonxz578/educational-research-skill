# v0.4.2 full-text access, evidence depth and reader architecture

The product keeps the approved v3 A4 white/black Times/Liberation Serif visual language. The functional changes are lawful native acquisition, stronger original-text evidence and a smaller five-section reader. Retrieval and critical reading remain separate operations. A machine status or matching digest cannot establish comprehension, truthful external ownership, correct interpretation, a novel question or journal acceptance.

## Products and reader projection

The default output root contains `Research_Roadmap.pdf`, a short README/delivery note and `evidence/`. The native reader view exposes exactly these five sections, in order:

1. Research logic.
2. What the authors actually establish.
3. Argument integration and closest-study challenge.
4. Theoretical/conceptual framework and roadmap.
5. APA 7 references.

Each source block contains two connected evidence paragraphs and a short, distinctly marked use of the source. The first combines the author's original position and particular method/mechanism; the second combines findings/reasoning and the actual boundary/counterevidence. One or two authentic short fragments can be embedded with their native locators. All four underlying evidence paraphrases appear once in the PDF. Source identity, DOI/link and necessary locator detail remain visible; technical state fields do not.

The argument section presents three to five connected comparisons and counterarguments rather than printing the graph. The closest study can dissolve the proposed gap. A refuted contribution is removed from the reader's claim and a supplied revised question can be shown for investigation; the engine does not invent a replacement question. The framework section uses one connected vector diagram and selected parsimonious lens, construct distinctions, observables/analysis and a short writing/research sequence. Causal arrows require a stated identification argument; proposed/sensitising relations do not become tested causal effects. Required non-users who cannot be recruited trigger design revision/fallback.

The full source/argument/novelty/framework/alignment data remain private. The native renderer, delivery checks, original 15 matrix dimensions, complete bibliography, G1–G5 and sealed receipts are retained. Legacy `--presentation evidence-pack` and explicit `--include-audit-pdf` remain available.

## Acquisition modules and boundaries

| Native module | Responsibility |
|---|---|
| `core/access.py` | Typed locations, attempt observations and acquisition states, independent of reading |
| `fulltext/providers.py` | Crossref identity/links, OpenAlex locations, Unpaywall DOI lookup and optional CORE pointers; deterministic route/version preference and URL deduplication |
| `fulltext/documents.py` | Actual PDF/HTML/JATS extraction, native page or section/paragraph locators and conservative identity/body-structure checks |
| `fulltext/acquire.py` | Bounded permitted fetching/local validation, access denial handling, private retention, version/hash checks and operator handoff |
| `core/reading.py` | Actual reader/time/scope records, exact primary spans, permissions, version matching and substantive reading eligibility |
| `core/evidence_depth.py` | Per-work English evidence-word accounting, repetition/filler/boilerplate checks and cumulative declared-fragment usage |
| `core/reader.py`, `render/roadmap.py` | Source-linked five-section projection and the approved native PDF |

The progression is metadata identity → lawful OA pointer → actual retrieved resource → validated document/version/usage → actual close reading → supported short public excerpt. Completion at one step does not complete the next. The acquisition engine never creates claims, quotes or a reading record from a download.

### Route order and provider configuration

Publisher OA HTML/PDF/XML/JATS and genuine ERIC-hosted full text are preferred over independently lawful repositories, with explicit VoR/AAM/preprint distinctions. A supplied local route is considered only within its recorded authorised scope. Repeated URLs are deduplicated, and bounded attempts do not imply exhaustive access. Scholar `[PDF]`, `[HTML]`, All versions and institution links remain individual lawful manual/UI paths, not a bulk scraping interface.

| Provider | Native use | Configuration/boundary |
|---|---|---|
| Crossref | Compare title/author/year/DOI and retain updates; inspect available links/licences | Mainly metadata; a TDM link or DOI landing page can still be gated or incomplete |
| OpenAlex | Inspect OA locations, host/version/licence and direct document or landing-page pointers | Optional `OPENALEX_API_KEY` is sent through the environment-configured adapter; OA pointers still need actual retrieval |
| Unpaywall | `GET /v2/{doi}` OA locations | Requires explicitly configured `UNPAYWALL_EMAIL`; no fabricated contact identity and no retired search route |
| CORE | DOI-matched work pointers under current API terms | Optional `CORE_API_KEY` plus explicit `CORE_API_TERMS_ACCEPTED=1`; missing configuration is NOT_CHECKED |
| ERIC | Actual full-text URL or eligible hosted-file path, followed by real resource validation | ERIC indexing/abstract/full-text flags do not themselves establish a valid full document |
| User-supplied | Private PDF/HTML/JATS within documented permission and processing scope | Actual local path, version, legal basis, terms check and permission evidence required; no inherited institutional login |

Official references: [Crossref text/data mining](https://www.crossref.org/documentation/retrieve-metadata/rest-api/text-and-data-mining/), [OpenAlex locations](https://help.openalex.org/data/locations/) and [authentication](https://help.openalex.org/api/authentication/), [Unpaywall API](https://unpaywall.org/api), [CORE API](https://core.ac.uk/services/api) and [ERIC API contract](https://eric.ed.gov/api/eric-api.yaml). Unpaywall's search endpoint was retired on 18 September 2026; the implementation uses DOI lookup. Provider access, authentication requirements and terms remain external dependencies, not entitlements granted by this package.

### Content, version and usage checks

A 200 response, a `.pdf` suffix or a claimed Content-Type is insufficient. Native validation checks actual signature, readable extraction, title/first-author match, substantive body length/structure and absence of access-screen content. PDF extraction pages are labelled as such; printed pages are never inferred. HTML retains section/paragraph text, including ordinary inline markup. JATS is parsed as document content. A repository landing page or an abstract without substantive article structure remains unqualified. Broken/encrypted PDFs, scans with inadequate extraction and uncertain completeness stay unresolved until authorised inspection/OCR and verification.

Public use also needs an identified version and appropriate processing/licence evidence. The conservative automatic path recognises a narrow set of explicit open licences; an unrecognised licence is a review state, not a conclusion that all use is forbidden. A local supplied document must record the actual authorised automated/hosted processing scope. Individual reading, local analysis, hosted AI processing and onward redistribution are separate questions. User possession of a PDF does not settle them. No login credentials are requested, stored or borrowed.

For accepted manuscripts and preprints, preserve their actual wording and native locators and record differences from an unavailable VoR. Original bytes and extracted text are retained privately with separate hashes. A changed/missing artifact or extraction, a changed version or newly failed revalidation cannot silently inherit an earlier verified reading. Static hashes do not independently detect a later remote change; revalidate actual routes when relying on current access/version.

### Denied or uncertain routes

Unauthenticated public HTTPS routes are bounded and checked; credential-bearing/private-network/shadow-library routes are unsupported. The engine respects robots checks and document-route spacing. A 401/403/429, login screen, CAPTCHA, paywall or denied robots route is stopped. Rate-limited hosts are paused rather than repeatedly retried through alternative paths on that host; a Retry-After observation is retained. Independently lawful routes can still be tried. There is no proxy trick, borrowed credential, CAPTCHA bypass or unauthorised bulk download.

If rights, terms or version cannot be established, the document is not promoted merely because its bytes were reachable. Unsafe/uncertain content is not converted into a supposed close reading. An explicitly documented alternative may be supplied through the private handoff.

## Machine states and private outputs

| Status | Observed state |
|---|---|
| `OA_FULL_TEXT_VERIFIED` | Actual publisher/ERIC document passed machine body, identity, version and usage checks; reading remains separate |
| `REPOSITORY_FULL_TEXT_VERIFIED` | Actual identified repository version passed those checks; preserve version differences |
| `USER_SUPPLIED_LAWFUL_TEXT` | Supplied local copy passed content checks within recorded permitted scope; not automatically read |
| `ABSTRACT_ONLY` | Only abstract/fragment evidence was established |
| `PAYWALL_OR_LOGIN_BLOCKED` | Route denied/rate-limited or access-screen content returned |
| `FULL_TEXT_RETRIEVED_NOT_VALIDATED` | Resource obtained but actual article content, extraction or identity unresolved |
| `FULL_TEXT_UNAVAILABLE` | No usable lawful full document established |
| `RIGHTS_OR_VERSION_UNCLEAR` | Actual version or permitted processing scope unresolved |

`Full_Text_Access.json` preserves these observations, attempts and reading-record presence. The acquisition record separates retrieval completeness, content validation, legal usage and close-reading completion. Files live under private `evidence/full_text/`; source records point to the exact versioned artifacts rather than a public copy in Git.

`Full_Text_Access_Handoff.md` records the article/DOI, attempted lawful routes and their outcomes, needed version, unresolved scope and a practical next step: an authorised local copy, library assistance, an independently lawful OA version or a genuinely relevant alternative. Passwords, authenticated URLs, full-text copies and real observation logs must not enter public commits. The reader gets only factual coverage/provisional status, not retrieval errors.

## Evidence depth and quantity acceptance

At least four distinct checked anchors cover thesis/definition, method/mechanism, finding/reasoning and limitation/counterpoint. Each retains the actual exact source span, locator, context, author warrant, attributed claim/evidence kind, disconfirming qualification and separate researcher inference. Qualifications that materially limit a claim must be incorporated into the rendered paraphrase or boundary; their presence in a private field alone does not make a misleading public claim acceptable.

The four rendered source paraphrases must independently supply at least **100 English words** per work, normally around 100–140. Titles, references, citations, locators, declared quotation fragments and our own inference do not count. Duplicate sentences, repeated-word/phrase padding, generic filler and cross-work boilerplate cannot manufacture substantive depth. Lexical source-span matching is a conservative check, not a semantic proof; actual close reading and expert judgement remain required.

A genuine 99-word explanation can remain visible as provisional, without invented filler, but fails the depth requirement. Other works cannot compensate by being longer. Selection size, qualified deep-read count and reproduced-excerpt count are separate. Default substantive coverage is at least ten; explicit N controls selection and the reading requirement `max(10,N,any higher explicitly requested threshold)`. Exact and at-least semantics and word-count precedence are unchanged from v3. Thus ten fully read papers plus ten abstracts still yield a precise shortfall against a twenty-work request.

The conservative public-output policy aggregates up to 20 verbatim words per copyrighted work unless separately verified permission allows more. Declared fragments repeated in a source block, argument integration or relevant framework/novelty prose use the same work-level allowance. Private exact spans do not automatically enter the public PDF. The policy is not a generic legal copying allowance or an entitlement to reproduce 100 source words. Use brief authentic fragments and faithful close paraphrase rather than accumulating quotations.

G2 enforces reading eligibility, depth, relevant independence and the dynamic target; G3 retains independent comparisons, warrants, counterarguments and alignment; G4 permits the strongest close study to defeat novelty. G5 checks complete native evidence outputs and the actual reader PDF, including source wording, blocks, references, typography and receipts. Structural checks can fail dishonest/incomplete inputs but cannot certify publication-level validity.

## CLI workflow and migration

New options:

| Flag | Behaviour |
|---|---|
| `--full-text-mode auto` | Default online acquisition within the declared bounds; actual reading remains required |
| `--full-text-mode revalidate` | Explicit renewed route/document checks for existing work; changed artifacts invalidate the old reading |
| `--full-text-mode off` | Disable new acquisition; does not make unvalidated evidence acceptable |
| `--full-text-limit N` | Bound works attempted; otherwise use the configured candidate budget |
| `--full-text-max-routes N` | Bound routes per work; default 8, supported range 1–20 |
| `--offline` | No sockets; existing artifacts are checked and explicitly permitted local supplied routes can be validated |

```bash
python -m educational_research.cli --topic 'Retrieval practice in primary education' --target-references 20 --mode discover --full-text-mode auto --full-text-limit 30 --full-text-max-routes 8 --output-dir outputs/discovery

# Requires actual reviewed records prepared from the obtained lawful documents.
python -m educational_research.cli --topic 'Retrieval practice in primary education' --target-references 20 --source-semantics exact --user-quantity-intent 'Review exactly 20 papers' --offline --sources private/sources.json --synthesis private/synthesis.json --protocol outputs/discovery/evidence/search_protocol.json --discovery-records outputs/discovery/evidence/Discovery_Observations.json --strict-quality-gates --output-dir outputs/reviewed

python scripts/validate_research_pack.py outputs/reviewed --strict
```

Retain the original prospective protocol, actual discovery observations, acquired artifacts and permission/version evidence when resuming. The agent must prepare genuine close-reading records and synthesis; neither CLI command invents them. Missing authentic Scholar/ERIC observations still block the appropriate discovery gate even when an OA article was retrieved successfully.

Source schema defaults to `4.2`; older v1/v2/v3 inputs still load. Reader and access schemas are maintained separately. The native reader additionally requires validated acquisition for non-synthetic works, processing permission/evidence, four richer anchors and per-work evidence depth. Old flags or legacy access labels do not fill missing evidence; validate an authorised local document or acquire/reread the actual version and update the private record. Synthetic fixtures are explicitly labelled and never earn real-research PASS.

`--presentation evidence-pack` preserves detailed legacy output/aliases; `--include-audit-pdf` adds the detailed PDF only when requested. Strict quality checks still require the substantive evidence contract; changing presentation does not grant a source access or depth exemption. The default stays one reader PDF and a short note with private technical evidence. Incomplete strict runs save honest outputs and exit 3; the strict validator also returns nonzero when substantive acceptance is incomplete.

## Observed real exemplar and validation boundary

A separate actual [Ritchie, Della Sala and McIntosh (2013) PLOS article](https://doi.org/10.1371/journal.pone.0078976) was obtained through the native public HTML acquisition path and closely read across its article body. Its private exemplar contains seven checked anchors, 131 qualifying English evidence words and 11 reproduced quotation units. It remains **one qualified work against a minimum of ten**, with strict CLI exit 3 and saved diagnostics. No completed Scholar search, authentic ten/twenty-work corpus, novel research gap or scientific validity is inferred from this exemplar.

The public ten- and twenty-work examples are separate generated SYNTHETIC / TEST ONLY fixtures: currently 8 and 14 pages, with 128–136 qualifying evidence words for every source. They demonstrate rendering and contract behaviour, not authentic research. See [the release validation report](V042_VALIDATION.md) for executed commands, final outcomes, skipped/blocked services, wheel checks and actual preview inspection. Real user records, article copies and non-synthetic observations remain private.
