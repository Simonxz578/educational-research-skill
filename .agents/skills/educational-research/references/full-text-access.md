# Lawful full-text access and operator handoff

The native `educational_research.fulltext` layer separates pointer discovery, HTTP retrieval, document/identity/completeness validation, permitted processing, version and critical reading. Success at one stage does not imply success at the next. `Full_Text_Access.json`, retained local artifacts and `Full_Text_Access_Handoff.md` live privately under evidence/; no downloaded paper or real observation log belongs in public examples or Git.

## Bounded routes and provider requirements

Default online `--full-text-mode auto` attempts sources within `--full-text-limit` (otherwise the candidate budget) and `--full-text-max-routes` per work. `--full-text-mode off` disables new acquisition; offline mode never opens a socket. `--full-text-mode revalidate` supports checking existing routes again. Preserve actual response/time/hash/version evidence; a stale or changed resource cannot silently inherit a previous verified-reading claim.

Prioritise actual publisher OA HTML/PDF/XML/JATS, ERIC-hosted files, and identified lawful repository AAM/preprint versions. Crossref verifies bibliographic identity and may expose links/licences, but metadata or a DOI landing page is never full text. OpenAlex locations and DOI-based Unpaywall results are OA pointers; the actual resource still needs validation. CORE adds optional permitted machine-readable OA routes. Scholar `[PDF]`, `[HTML]`, All versions and institutional links are individual lawful UI/manual discovery paths; no Scholar bulk scraper or CAPTCHA workaround is provided.

- [Unpaywall API](https://unpaywall.org/api): use `GET /v2/{doi}` with explicitly configured `UNPAYWALL_EMAIL`. The `/v2/search` endpoint was retired on 18 September 2026; never build discovery against it.
- [OpenAlex locations](https://help.openalex.org/data/locations/) and [authentication](https://help.openalex.org/api/authentication/): inspect best_oa_location/locations, OA status, source, licence and publishedVersion/acceptedVersion/submittedVersion. `OPENALEX_API_KEY`, when configured, stays in the environment; a pointer still does not validate the underlying document.
- [CORE API](https://core.ac.uk/services/api): `CORE_API_KEY` and explicit `CORE_API_TERMS_ACCEPTED=1` enable optional queries under the operator's actual current terms and limits. Missing credentials/consent are NOT_CHECKED, not a successful CORE search. Unknown source licence/version requires review, not an assumption.

Never hard-code keys, emails or authenticated URLs. Respect provider throttling/Retry-After, robots restrictions and actual platform terms. Stop 401/403/429, login, paywall, CAPTCHA, embargo or uncertain-rights paths; try an independently lawful alternative rather than proxy tricks, credential borrowing or shadow libraries. Bounded attempts are not a guarantee of exhaustive access.

## Validate actual content and rights

Inspect response status, actual signature and readable text, document front matter, title/author identity, substantive section structure and completeness. A PDF suffix, Content-Type header, HTTP 200 or a long abstract is insufficient. Preserve native HTML/JATS section/paragraph locators; PDF extraction pages are not automatically printed pages. Scans/failed OCR remain unresolved. A repository acceptedVersion keeps AAM wording/locators and records possible differences from unavailable VoR; do not borrow its pages or findings.

Keep both original artifact and extracted text hashed. A replacement artifact, changed version, extraction change, known link rot or newly blocked route invalidates stale verification and may require rereading. Machine structure/lexical checks supplement the actual reader; they cannot prove interpretive accuracy, external truthfulness or scientific validity.

`FullTextLocation` records URL/route, version, legal basis, licence evidence, processing_permission and permission evidence. A user-supplied document needs actual authorised scope, terms review and permitted processing before ingestion. Individual reading access, local non-commercial analysis, third-party hosted AI processing and onward distribution are different permissions. Never infer hosted-AI permission from a student's login or request passwords. If scope is unclear, stop that processing and ask for a documented lawful alternative through the private handoff.

## Machine states and completion boundary

| Status | Meaning |
|---|---|
| OA_FULL_TEXT_VERIFIED | Actual public publisher/ERIC document passed machine content/version/rights checks; reading still separate |
| REPOSITORY_FULL_TEXT_VERIFIED | Actual identified repository version passed those checks; preserve version differences |
| USER_SUPPLIED_LAWFUL_TEXT | Local supplied copy has recorded permitted scope and validated content; not automatically read |
| ABSTRACT_ONLY | Only abstract/fragment evidence is available |
| PAYWALL_OR_LOGIN_BLOCKED | This route is denied, rate-limited or an access screen |
| FULL_TEXT_RETRIEVED_NOT_VALIDATED | Bytes were obtained, but actual full content/identity/extraction is unresolved |
| FULL_TEXT_UNAVAILABLE | No usable lawful document was established |
| RIGHTS_OR_VERSION_UNCLEAR | Processing rights or actual version cannot yet be established |

`close_reading_completed` must never be inferred from retrieval. A separate actual reading record needs version/hash, reader/date, complete scope and checked source-specific anchors. G2 additionally requires the source's own 100-word explanation and the user's dynamic quota.

Blocked handoff: article + DOI; exact attempted legal routes and observations; needed version; unresolved processing/licence issue; and whether authorised user supply, library help, a lawful OA alternative or another genuinely relevant work could resolve it. Keep the handoff concise and private. The reader receives factual coverage/PROVISIONAL status, never URL error logs or candidate lists.
