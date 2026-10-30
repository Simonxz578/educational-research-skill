"""Command-line entry point; run python -m educational_research.cli --help."""

import argparse
import json
import logging
import sys
import shlex
from .core.discovery import utc_now
from .config import Config
from .pipeline import run


def parser():
    p = argparse.ArgumentParser(
        description="Build a compact evidence pack, not an essay. / 生成可追溯研究资料包"
    )
    p.add_argument("--topic", default="Manuscript evidence audit")
    p.add_argument("--target-words", type=int, default=1000)
    p.add_argument("--target-references", type=int)
    p.add_argument("--source-semantics", choices=["exact", "at_least"])
    p.add_argument(
        "--user-quantity-intent", help="Exact originating user count request, interpreted by the agent"
    )
    p.add_argument("--presentation", choices=["roadmap", "evidence-pack"], default="roadmap")
    p.add_argument("--include-audit-pdf", action="store_true")
    p.add_argument("--search-candidate-budget", type=int)
    p.add_argument(
        "--mode",
        choices=[
            "discover",
            "search",
            "synthesise",
            "gap",
            "outline",
            "audit",
            "revise",
            "full",
            "draft",
            "framework",
        ],
        default="full",
    )
    p.add_argument("--quality-level", choices=["exploratory", "substantive"])
    p.add_argument("--min-reviewed-fulltexts", type=int, default=10)
    p.add_argument("--require-verifiable-scholar", action="store_true")
    p.add_argument("--strict-quality-gates", action="store_true")
    p.add_argument("--empirical-proposal", action="store_true")
    p.add_argument("--protocol", help="Prospective scoped protocol JSON, prepared before searching")
    p.add_argument(
        "--discovery-records",
        help="Archived API receipts or lawful Scholar observations with artifact digests",
    )
    p.add_argument("--language", default="en-GB")
    p.add_argument("--offline", action="store_true")
    p.add_argument(
        "--sources", help="Validated private source JSON, including agent-reviewed extractions"
    )
    p.add_argument("--synthesis", help="Validated claims/gaps/relationships JSON")
    p.add_argument("--input", help="Existing draft Markdown/plain text for a line-addressed audit")
    p.add_argument("--scholar-csv", help="User-attested manual/export Scholar observations")
    p.add_argument("--providers", default="eric,google-scholar,crossref,openalex")
    p.add_argument(
        "--metrics",
        default="jif,quartile,article-citations",
        help="Requested display fields; unavailable values stay not verified",
    )
    p.add_argument("--include-draft", action="store_true")
    p.add_argument("--output-dir", default="outputs/research")
    for option in (
        "rq",
        "context",
        "methodology",
        "discipline",
        "framework",
        "author-thesis",
        "geography",
        "education-level",
        "inclusion",
        "exclusion",
        "search-date",
    ):
        p.add_argument("--" + option)
    p.add_argument("--year-from", type=int)
    p.add_argument("--year-to", type=int)
    p.add_argument("--descriptor", action="append", default=[])
    p.add_argument("--peer-reviewed", action="store_true")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    if args.mode in {"audit", "revise"} and not args.input:
        parser().error("--input is required for audit/revise mode")
    allowed = {"eric", "google-scholar", "crossref", "openalex", "semantic-scholar"}
    providers = set(args.providers.split(","))
    if providers - allowed:
        parser().error("Unsupported provider: " + ", ".join(providers - allowed))
    fields = Config.model_fields.keys()
    values = {k: v for k, v in vars(args).items() if k in fields and v is not None}
    values["descriptors"] = args.descriptor
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    try:
        result = run(
            Config(**values),
            args.output_dir,
            args.sources,
            args.synthesis,
            args.input,
            args.scholar_csv,
            providers,
            args.include_draft,
            protocol_path=args.protocol,
            discovery_records=args.discovery_records,
            execution_context={
                "entrypoint": "educational_research.cli",
                "argv": list(argv) if argv is not None else sys.argv[1:],
                "command": shlex.join(
                    ["python", "-m", "educational_research.cli"]
                    + (list(argv) if argv is not None else sys.argv[1:])
                ),
                "started_at": utc_now(),
            },
        )
    except (ValueError, OSError, RuntimeError) as exc:
        parser().exit(2, f"Research pack failed: {exc}\n")
    print(
        json.dumps(
            {
                "output_dir": args.output_dir,
                "layout_passed": result["layout_passed"],
                "research_status": result["research_quality"]["overall_status"],
                "label": result["research_quality"]["label"],
                "included": result["included"],
                "reference_shortfall": result["reference_shortfall"],
            }
        )
    )
    if args.strict_quality_gates and not result["research_passed"]:
        return 3
    return 0 if result["layout_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
