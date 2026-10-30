"""v2 native pack finalisation: structured artifacts, gates, renderer, receipts and QA."""

import json
from pathlib import Path
from .gates import evaluate_gates, QualityGates
from .editorial import editorial_audit
from .reading import evidence_registry, sha256_file
from .framework import mermaid
from .discovery import utc_now
from .deliverables import write_csv, validate_delivery, seal_receipt
from ..render.framework import diagram_spec, svg


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finalise(
    output,
    config,
    sources,
    synthesis,
    logs,
    observations,
    audit,
    graph_errors,
    draft_text,
    execution_context,
    protocol,
    selection,
):
    from ..render.essentials_pdf import render
    from ..render.inspect import inspect
    from ..render.roadmap import render as render_roadmap
    from .reader import build_reader, alignment_map
    from .layout import reader_pdf

    output = Path(output)
    matrices = json.loads((output / "Literature_Argument_Matrix.json").read_text())
    for row in matrices:
        claims = [c for c in synthesis.claims if row["id"] in c.source_ids]
        row["claim_ids"] = [c.id for c in claims]
        row["evidence_ids"] = list(dict.fromkeys(i for c in claims for i in c.evidence_ids))
        row["warrant_ids"] = [c.warrant_id for c in claims]
    dump(output / "Literature_Argument_Matrix.json", matrices)
    # Empty CSVs still carry the complete 15-group schema, never a reduced placeholder.
    from .deliverables import MATRIX_GROUPS

    columns = (
        list(matrices[0])
        if matrices
        else list(dict.fromkeys(f for fields in MATRIX_GROUPS.values() for f in fields))
    )
    for name in ["Evidence_Matrix", "Literature_Argument_Matrix"]:
        dump(output / (name + ".json"), matrices)
        write_csv(output / (name + ".csv"), matrices, columns)
    for legacy, native in [
        ("evidence_ledger.json", "Evidence_Ledger.json"),
        ("argument_graph.json", "Argument_Graph.json"),
    ]:
        dump(output / native, json.loads((output / legacy).read_text()))
    dump(output / "Discovery_Observations.json", [o.model_dump() for o in observations])
    qa = evaluate_gates(config, sources, synthesis, logs, observations, graph_errors=graph_errors)
    dump(output / "Full_Text_Reading_Audit.json", qa["reading_audit"])
    write_csv(output / "Full_Text_Reading_Audit.csv", qa["reading_audit"])
    dump(output / "Closest_Study_Novelty_Comparison.json", qa["novelty_audit"])
    write_csv(output / "Closest_Study_Novelty_Comparison.csv", qa["novelty_audit"]["comparisons"])
    dump(
        output / "Theoretical_Conceptual_Framework.json",
        synthesis.framework.model_dump()
        if synthesis.framework
        else {"status": "NOT_ESTABLISHED", "schema_version": "2.0"},
    )
    dump(output / "Framework_Diagram.json", diagram_spec(synthesis.framework))
    (output / "Framework.mmd").write_text(mermaid(synthesis.framework), encoding="utf-8")
    (output / "Framework.svg").write_text(svg(synthesis.framework), encoding="utf-8")
    write_csv(output / "Theory_RQ_Evidence_Method_Alignment.csv", qa["framework_audit"]["alignment"])
    dump(output / "Framework_Audit.json", qa["framework_audit"])
    dump(output / "Study_Design_Audit.json", qa["design_audit"])
    view = (
        build_reader(config, protocol, sources, synthesis, selection, qa)
        if config.presentation == "roadmap"
        else None
    )
    if view:
        dump(output / "Reader_View.json", view.model_dump())
        dump(output / "Argument_Alignment.json", alignment_map(config, protocol, synthesis))
    receipt = {
        "schema_version": "4.3",
        "presentation": config.presentation,
        "source_selection": selection.model_dump(),
        "include_audit_pdf": config.include_audit_pdf,
        "entrypoint": execution_context.get("entrypoint", "educational_research.pipeline.run"),
        "renderer": "educational_research.render.roadmap"
        if config.presentation == "roadmap"
        else "educational_research.render.essentials_pdf",
        "argv": execution_context.get("argv", []),
        "started_at": execution_context.get("started_at", utc_now()),
        "completed_at": utc_now(),
        "commands_executed": [
            {
                "command": execution_context.get("command", "Python API call: pipeline.run"),
                "executed_at": utc_now(),
                "result": "structured artifacts and native renderer executed",
            }
        ],
        "engine_source_sha256": sha256_file(Path(__file__).parents[1] / "pipeline.py"),
        "artifact_hashes": {},
    }
    dump(output / "Execution_Receipt.json", receipt)
    pdf = reader_pdf(output, config.presentation)
    # Resolve G5 with a conservative fixed point: label complete only after all artifacts and PDF pass.
    for iteration in range(3):
        audit["research_quality"] = qa
        dump(output / "Research_Quality_Gates.json", qa)
        editorial = editorial_audit(
            synthesis.editorial_review,
            qa["gates"],
            qa["framework_audit"],
            qa["design_audit"],
            evidence_registry(sources),
            draft_text,
            qa["synthetic"],
        )
        dump(output / "Editorial_Audit.json", editorial)
        audit["editorial"] = editorial
        dump(output / "audit.json", audit)
        (output / "QA_Report.md").write_text(
            "# Research quality and native QA\n\n"
            + qa["label"]
            + "\n\n"
            + "\n".join(
                f"- {key}: {gate['status']} — {gate['reason']}" for key, gate in qa["gates"].items()
            )
            + f"\n\nSource coverage: selected {len(sources)}/{selection.selection_target_N}; deeply reviewed {selection.qualified_deep_read_K}/{selection.deep_review_requirement_N}; micro-excerpts {selection.quotation_count}; shortfall {selection.shortfall}. Included {selection.included_N}; FULL_TEXT_VERIFIED {selection.full_text_verified_K}; ABSTRACT_ONLY {selection.abstract_only_A}; unfilled item shortfall {selection.selected_shortfall}."
            + (
                "\n\nSOURCE_ANCHORED_EXPLANATION word counts (not author words; no quota): "
                + json.dumps(
                    {
                        row["source_id"]: row["primary_evidence_depth"]
                        for row in qa["reading_audit"]
                        if row.get("primary_evidence_depth")
                    }
                )
                if config.presentation == "roadmap"
                else ""
            )
            + "\n\nVERBATIM_PRIMARY_TEXT inspection (only exact checked spans): "
            + json.dumps(
                {
                    row["source_id"]: row["verbatim_primary_text"]
                    for row in qa["reading_audit"]
                    if row.get("verbatim_primary_text")
                }
            )
            + "\n\nFramework: "
            + qa["framework_audit"]["status"]
            + "; methods: "
            + qa["design_audit"]["status"]
            + "\n\nEditorial: "
            + editorial["label"]
            + " (not acceptance or peer review).\n"
            + "\nCommands actually executed: "
            + json.dumps(receipt["commands_executed"])
            + "\n\nScientific interpretation and document authenticity remain reviewable judgements. Synthetic packs never earn production acceptance.\n",
            encoding="utf-8",
        )
        if config.presentation == "roadmap":
            render_roadmap(pdf, config, sources, synthesis, view, qa)
            if config.include_audit_pdf:
                render(
                    output / "Educational_Research_Essentials.pdf",
                    config,
                    sources,
                    synthesis,
                    json.loads((output / "gap_evidence.json").read_text()),
                    logs,
                    audit,
                )
        else:
            render(
                pdf,
                config,
                sources,
                synthesis,
                json.loads((output / "gap_evidence.json").read_text()),
                logs,
                audit,
            )
        audit["pdf"] = inspect(
            pdf,
            output / "previews",
            [s.id for s in sources],
            synthesis.framework
            if config.presentation != "roadmap" or (view and view.framework)
            else None,
            presentation=config.presentation,
        )
        receipt["commands_executed"].append(
            {
                "command": "Python call: educational_research.render.inspect",
                "executed_at": utc_now(),
                "result": {"pages": audit["pdf"]["pages"], "errors": audit["pdf"]["errors"]},
            }
        )
        delivery = validate_delivery(output, audit["pdf"], verify_receipt=True)
        receipt["commands_executed"].append(
            {
                "command": "Python call: educational_research.core.deliverables.validate_delivery",
                "executed_at": utc_now(),
                "result": delivery,
            }
        )
        next_qa = evaluate_gates(config, sources, synthesis, logs, observations, delivery, graph_errors)
        for gate in next_qa["gates"].values():
            gate["commands_executed"] = receipt["commands_executed"]
        if next_qa["gates"]["G5"]["status"] == qa["gates"]["G5"]["status"]:
            qa = next_qa
            break
        qa = next_qa
    qa = QualityGates.model_validate(qa).model_dump()
    audit["research_quality"] = qa
    audit["layout_passed"] = not audit["pdf"]["errors"]
    audit["passed"] = audit["layout_passed"]  # v1 API compatibility; never a research acceptance flag.
    audit["research_passed"] = qa["overall_status"] == "PASS"
    dump(output / "Research_Quality_Gates.json", qa)
    dump(output / "audit.json", audit)
    receipt["completed_at"] = utc_now()
    seal_receipt(output, receipt)
    # Verify the final file hashes and save diagnostics separately without invalidating the sealed pack.
    final = validate_delivery(output, audit["pdf"])
    dump(output / "Native_Delivery_Validation.json", final)
    receipt["commands_executed"].append(
        {
            "command": "Python call: final sealed-deliverable validation",
            "executed_at": utc_now(),
            "result": final,
        }
    )
    dump(output / "Execution_Receipt.json", receipt)
    return audit
