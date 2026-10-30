Current v0.4.3 evidence and abstract architecture: [original-word inspection and abstract fallback](VERBATIM_ABSTRACT_V043.md), with the continuing [native acquisition architecture](FULL_TEXT_ACCESS_V042.md). Historical v2/v3 architecture follows.

# Architecture

Current v3 reader/selection/output architecture: [READER_ROADMAP_V3.md](READER_ROADMAP_V3.md).

The v2 quality-gate/framework extension and migration are described in [QUALITY_ENGINE_V2.md](QUALITY_ENGINE_V2.md). The native retrieval/rendering flow below remains the foundation.

The agent does scientific reasoning; deterministic Python retrieves, validates, scores, formats and renders. No hidden LLM service, API key or invented semantic synthesis.

`cli/config` → prospective protocol → `search` (ERIC front door, Scholar plan/import, Crossref identity, OpenAlex/optional Semantic Scholar metrics) → `Source` validation → dedup/scope screening → relevance-first ranking/diversity selection → validated source extractions and synthesis graph → gap calibration → one flow-based PDF and traceable machine records → page inspection/audit.

Source JSON is the analysis boundary. The canonical skill directs an agent to critically read sources and prepare evidence-linked `summary`, `source_argument` and `target_argument`; Python checks referential integrity and exact quote spans. Without analysis inputs, live retrieval produces honest metadata/abstract candidates with unconstructed claims and speculative gaps. Supply `--synthesis` for independent claims, warrants, objections, contradictions, method alignment and closest-work comparisons. The CLI cannot establish whether an interpretation is academically sound.

HTTP uses bounded retries, Retry-After, 25-second timeouts, daily response cache, safe request logs and no keys in URLs. Pagination is staged in ERIC batches of 50; caches survive interruption. Offline mode refuses network calls. Source IDs survive the pipeline, and duplicates/exclusions are logged. Private outputs and caches are ignored by git.

JSON/CSV retain complete fields; the PDF rejects overlong analytical cells rather than truncating them. Subrows keep 9.5 pt matrix typography. Bibliography uses a real CSL APA processor. The package carries its style JSON, so installed wheels do not depend on repository-relative assets. The separately discoverable `.agents` skill requires installing the companion Python package.
