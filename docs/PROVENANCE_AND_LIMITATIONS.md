# Provenance and limits

Only generic methodology and clearly marked synthetic fixtures are public. No user manuscripts, feedback, uploads, private article identifiers, API keys, credentials or real research-run logs belong in this repository. Original code is MIT; external quotations, metadata, CSL styles and installed fonts retain their own rights.

Official references checked on 2026-10-29:
- [Codex skills](https://learn.chatgpt.com/docs/build-skills): SKILL.md frontmatter and progressive disclosure; repository `.agents/skills` discovery.
- [ERIC API navigation](https://eric.ed.gov/?api) and [actual Swagger schema](https://eric.ed.gov/api/eric-api.yaml): GET https://api.ies.ed.gov/eric/, search/format/start/rows/fields; no invented Thesaurus API.
- [Google Scholar help](https://scholar.google.com/intl/en/scholar/help.html): manual discovery and export, no bulk scraping.
- [Crossref REST](https://www.crossref.org/documentation/retrieve-metadata/rest-api/): metadata identity; [Crossmark](https://www.crossref.org/services/crossmark/): publication updates.
- [OpenAlex authentication](https://help.openalex.org/api/authentication/): keyless basic use and optional environment key, time-dependent limits.
- [APA examples](https://apastyle.apa.org/style-grammar-guidelines/references/examples) and [DORA](https://sfdora.org/read/): citation and responsible metrics.
- [PRISMA 2020](https://www.prisma-statement.org/prisma-2020-checklist): reporting framework, not a label earned by this tool alone.

Reference visual contract: [personalised-practice-generator](https://github.com/Simonxz578/personalised-practice-generator/tree/0f658aa0f7f6da8c072bcf596db06248aa59adbe), MIT, v0.4.0. Geometry and serif hierarchy adapted with attribution; academic renderer independently written. Fonts and reference sample PDFs are not redistributed.

Limits: bibliographic matching is conservative but publisher/VoR, date selection, corrections/retractions and licence authenticity still need review. Abstracts never verify full-text claims. Span verification checks supplied text, not source authenticity. JCR metrics need legitimate user-supplied provenance; the CLI does not access JCR. Evidence/method/argument scores need reviewed assessments; lexical relevance is provisional. Citation audits cover IDs and parenthetical author-years, not every narrative citation/disambiguation. CJK uses a viewer CID font reference; archival embedding requires a licensed font customisation. No automated OCR, full-text download, systematic-review guarantee, originality guarantee, empirical-data generation or autonomous manuscript writing. Explicit draft mode emits a source-linked scaffold; the agent writes any requested paper separately after critical verification. Natural-language intent routing lives in the skill; the CLI accepts explicit flags. All research modes share the essentials contract; the agent supplies mode-specific analysis. Revise mode creates a line-addressed audit map, with actual surgical editing performed by the agent.
