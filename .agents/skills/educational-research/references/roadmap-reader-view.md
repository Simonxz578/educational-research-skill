# Native reader-view and quantity model

Source v3 retains v1/v2 input migration and adds exact private anchor/context/warrant/inference fields. Reader_View.json contains only qualifying selected works, with separate source_author_position, source_reasoning_and_results, source_limitations, our_inference, original_microquotes, locators, debate_id and argument_ids. It is derived from checked anchors, never fabricated from titles/abstracts. Micro-excerpts occur once per selected source block; all selected works receive complete references.

Source_Selection.json and assets/source-selection.schema.json define the count contract. Assets/reader-view.schema.json defines the reader projection. Exact/at_least and explicit/default origin are persisted, not inferred retroactively. The originating user's natural-language text is supplied by the agent, not guessed by a Python parser. Incomplete counts are rendered as K/N with source/deep shortfalls. All private native evidence remains available for editing and expert verification.

Use `--presentation evidence-pack` for the old detailed layout. The native validator automatically resolves root/evidence directories and inspects both the complete evidence contract and the chosen PDF. Never copy an attractive private reference PDF, conceal missing sources or bypass G5 with a reduced handcrafted report.
