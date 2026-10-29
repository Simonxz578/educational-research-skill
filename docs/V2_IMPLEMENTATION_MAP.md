# v2 implementation map

Baseline: existing native CLI, models, source/argument schema, search adapters, ranking, renderer, tests and skill references inspected before edits. The v1 layout-only success flag does not certify substantive completion. Legacy source access flags and source records remain readable; they do not become deep-reading evidence automatically.

| Gap | Native implementation |
|---|---|
| Rendering mistaken for research completion | core/gates.py; Research_Quality_Gates.json; explicit provisional PDF and strict CLI exit |
| Abstracts or one passage counted as close reading | models.py; core/reading.py; per-section evidence, scoped full-text document provenance and reading audit |
| Citation lists mistaken for comparative argument | core/graph.py; independent works, passages, comparisons, rival evidence and paragraph plans |
| Gap overlaps closest work | core/novelty.py; multi-dimension closest-work comparison and rival challenge verdict |
| Decorative theory and construct drift | core/framework.py; candidate lens comparison, constructs, relationships, alignment, editable diagram and semantic audit |
| Mixed methods without independent questions/integration | core/design.py; conditional strand/feasibility validators and design audit |
| Editorial scores mistaken for acceptance probability | core/editorial.py; anchored reviewable assessment, conservative readiness rule |
| Custom/partial PDF bypass | pipeline.py + render + core/deliverables.py; native receipt, all matrix groups, gate recomputation and file hashes |
| Unobserved Scholar search and retrospective logs | typed discovery observations, artifact hashes, actual ERIC receipts, explicit import/resume with provenance |
| Regression and documentation | synthetic v2 fixtures; tests/test_v2_*; updated canonical skill/schema and release notes |
