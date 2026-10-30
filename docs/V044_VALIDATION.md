# v0.4.4 observed validation — 30 October 2026

The release changes the native PDF product: ORIGINAL AUTHOR TEXT leads each source block; concise OUR CRITICAL USE follows. Long per-paper AI explanations remain private. The source and reader schemas accept v0.4.4, retain older inputs, and distinguish exact displayed excerpts and omission flags from private inspection/explanation/inference.

## Engineering checks

**145 passed, 1 skipped**, with five upstream PyMuPDF/SWIG deprecation warnings; Ruff and skill validation pass. The opt-in network test was skipped; genuine repository retrieval is reported separately below. The full pytest suite and twelve new visible-text cases exercise A–H, including 12/15 printed words despite extensive private reading or AI prose; >=100 matched words actually shown; invented, foreign, wrong-version, overlapping and translated wording; licensed 85/120-word abstracts; unresolved reproduction rights; repeated positions; and PDF tampering after receipt hashes are refreshed. Older tests now check printed source excerpts rather than requiring the superseded AI-explanation paragraphs. No academic gate was weakened to make abstracts count as full readings.

Native commands run:

```bash
python -m pytest -q
python -m ruff check .
python scripts/generate_quality_example.py --count 10 --output outputs/roadmap-v044-10
python scripts/generate_quality_example.py --count 20 --abstract-count 7 --output outputs/roadmap-v044-20
python scripts/validate_research_pack.py outputs/roadmap-v044-10
python scripts/validate_research_pack.py outputs/roadmap-v044-20
python scripts/validate_research_pack.py outputs/roadmap-v044-20 --strict
python -m build --no-isolation
```

The ten-source synthetic PDF has eight pages and 100 independently matched printed English author words for each source. The twenty-source PDF has thirteen pages, thirteen full-text fixtures at 100 words and seven authentic-to-the-fixture abstract records at 95 words. Each short abstract explicitly displays 95/100 and a reason. All twenty blocks and APA entries remain. Structural validation passes; mixed strict validation correctly exits 1 and strict CLI saves provisional output then exits 3. Synthetic content is prominently TEST ONLY and never establishes genuine scholarship.

Every page undergoes native A4/black-text/font/bounds checks. Representative first, middle/dense evidence, framework and reference pages are rendered and actually viewed. Private records store review attestations, source hashes, exact spans, PDF word counts and explicit failures. Public previews contain only generated fixtures. Build and installed-wheel checks run outside the checkout using the ordinary CLI, including mixed source scope and exact item counts.

## Genuine retained OA article

The previously read and retained publisher OA article, Ritchie et al. (2013), DOI `10.1371/journal.pone.0078976`, is revalidated against its original artifact. Its independently reviewed publisher CC BY permission supports compact attributed original passages for critical comparison. The native PDF visibly prints 100 verified original English words across four roles, distinct from the 435 privately inspected words and the earlier explanation. The source's display gate passes. The one-work run is still academically incomplete against the default ten-work requirement; strict CLI returns 3. This is retained-reading revalidation, not a new claim of a complete corpus.

## Genuine Phoenix EPLI closest-study regression

Topic: *From Career Aspirations to Participation: Exploring Institutional Barriers to International Students’ Engagement with Career Development Support in UK Higher Education.*

The actual [University of Glasgow record for Nygren (2025)](https://theses.gla.ac.uk/85171/) and its linked thesis were retrieved with HTTP 200 and kept private. The official 339-word abstract was read and retained separately from the record’s bibliographic table. The thesis cover permits personal non-commercial study but reserves copyright and restricts extensive quotation; extended reproduction permission was not established. The whole 304-page thesis was not close-read. The reader therefore uses an explicitly ABSTRACT ONLY record and displays **0/100**, identifying reproduction permission as the reason. No protected wording is copied into the public repository.

The actual native Phoenix PDF includes a closest-study challenge: Nygren already examines international student employability facilitators/inhibitors and university services in UK universities. The broad claim of an unstudied institutional-barriers gap is unsupported. The remaining service-participation mechanism needs full-thesis and additional closest-study comparison; no novelty verdict, connected framework or journal acceptance is invented. This genuine run includes one closest work, leaving nine requested items and all ten full-text reviews unfilled. Strict CLI returns 3; ordinary structural validation passes; strict validator returns 1. No ERIC/Google Scholar search execution or authentic ten/twenty-work corpus is claimed.

## Permission and acceptance limits

The finished-PDF validator counts distinct matched source-word positions per source block, excluding repeats, paraphrase, inference and metadata. Source identity/version, precise locators, original-artifact digest and scoped public reproduction allowance remain separate checks. Missing text or counterfeit counters are structural failures. A truthful rights/length shortfall remains a useful structurally valid product but fails G5 display acceptance and strict completion. Abstracts never satisfy G2 full-text inspection, even with 100 publicly displayed words.

The default microquote review does not establish permission for 100 words. A recorded extended allowance or reviewed open licence supports larger excerpts; provenance must explain purpose, necessity, proportion and acknowledgement. Mathematical/text extraction and lexical exactness do not independently prove semantic interpretation, external authenticity or legal conclusions; source-specific agent review remains required. No student documents, original protected works or private ledgers are published.
