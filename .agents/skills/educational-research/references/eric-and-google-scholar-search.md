# v2 auditable discovery and resume

ERIC uses the documented endpoint https://api.ies.ed.gov/eric/ from the official schema https://eric.ed.gov/api/eric-api.yaml. Subject descriptors and population/stage/geography/date/peer-review filters survive general/theory/recent expansions. There is no invented Thesaurus API; browse ERIC's actual descriptors. A live execution writes a preserved response, its digest and exact UTC time/count/IDs. Cache replays are ERIC_CACHED, not new searches.

Google Scholar has no bulk API in this package. Use permitted manual/UI access following https://scholar.google.com/intl/en/scholar/help.html or an actual user export. A discovery observation requires exact query, filters, timestamp, observed title/link records, observer, artifact path/SHA256 and observation kind. A query plan or a CSV containing only declared title/query/date cannot satisfy G1 without the underlying export/observation. The code tests consistency and integrity, not independent authenticity of the observer.

Package a genuine CSV/JSON export containing `title,url` (optional `cited_by`) with:

```bash
python scripts/import_scholar_observation.py private/actual_export.csv --query 'exact executed query' --executed-at '2026-10-29T10:00:00+00:00' --observer 'actual observer' --filters-json '{"since":2020}' --output private/scholar-observations.json
```

The timestamp above is illustrative; enter the actual observation time. For browser observations retain the actual snapshot/artifact and structured result records; never fabricate them. Imported observations are named as imports, not newly executed searches. Counts describe observed results, not all available literature. Citation counts are index/date-specific and never inferred.

Resume with the original prospective `--protocol` and `--discovery-records` archived receipts. The protocol must predate observed searches; do not retroactively create one and claim prospective design. Combine observations from original ERIC execution and actual Scholar work in the private input array. An unavailable/blocked Scholar session yields GOOGLE_SCHOLAR_NOT_CHECKED and manual handoff; cross-index metadata enrichment cannot substitute. Respect access restrictions, CAPTCHA and rate limits.
