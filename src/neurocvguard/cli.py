"""Local argparse commands; scientific work delegates to shared library APIs."""

import argparse
import json
import logging
import sys
import traceback
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from neurocvguard import __version__
from neurocvguard._paths import is_remote_path
from neurocvguard.errors import ConfigurationError, NeuroCVguardError, UnsupportedDesignError

if TYPE_CHECKING:
    from neurocvguard.models import AuditReport, ComparisonResult
    from neurocvguard.serialization import JSONObject


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        # argparse normally echoes arbitrary argv values, including private paths.
        self.print_usage(sys.stderr)
        self.exit(
            2,
            "neurocvguard: Invalid invocation; supply required options and supported values. "
            "See --help.\n",
        )


def _parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="neurocvguard",
        description="Local research audits and offline reports; no clinical certification.",
        allow_abbrev=False,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show sanitized stack locations on internal failures (place before command).",
    )
    commands = parser.add_subparsers(
        dest="command", metavar="{init,validate,audit,split,evaluate,compare,report,demo}"
    )
    descriptions = {
        "demo": (
            "Run a fully synthetic offline workflow; no patient data or downloads. "
            "Default clean is participant-disjoint; repeated opts into an invalid diagnostic."
        ),
        "init": "Write an editable strict JSON starter. No columns are inferred.",
        "validate": (
            "Validate local inputs and inspect scoped findings; "
            "validation is not scientific certification."
        ),
        "audit": (
            "Audit cohort, optional splits and declarations; write public JSON and offline HTML."
        ),
        "split": (
            "Generate and independently check outer splits. "
            "Output contains sensitive observation identities."
        ),
        "report": (
            "Render compatible exported report JSON without recomputing findings "
            "or recovering redacted details."
        ),
        "evaluate": (
            "Run participant classification with train-only fitting and optional nested C "
            "selection. Writes a sensitive private result and separate research reports."
        ),
        "compare": (
            "Compare two or more local evaluation.private.json records without fitting. "
            "Signed differences are descriptive, not causal; public reports omit private digests."
        ),
    }
    examples = {
        "demo": "demo --out local_outputs/demo --scenario clean",
        "init": "init --out config.json",
        "validate": "validate --cohort cohort.tsv --config config.json",
        "audit": "audit --cohort cohort.tsv --config config.json --out local_outputs/audit",
        "split": "split --cohort cohort.tsv --config config.json --out local_outputs/splits",
        "report": "report --input local_outputs/audit/report.json --out local_outputs/rerender",
        "evaluate": (
            "evaluate --cohort cohort.tsv --features features.tsv --splits plan.json "
            "--config config.json --out local_outputs/evaluation"
        ),
        "compare": (
            "compare --result A=run-a/evaluation.private.json "
            "--result B=run-b/evaluation.private.json --out local_outputs/comparison"
        ),
    }
    for name, description in descriptions.items():
        command = commands.add_parser(
            name,
            help=description,
            description=description,
            epilog="Example: neurocvguard " + examples[name],
            allow_abbrev=False,
        )
        if name in {"validate", "audit", "split", "evaluate"}:
            command.add_argument(
                "--cohort", required=True, help="Local CSV/TSV observation manifest."
            )
            command.add_argument("--config", required=True, help="Strict JSON with explicit roles.")
        if name in {"validate", "audit"}:
            command.add_argument(
                "--fail-on",
                choices=("none", "warning", "error"),
                default="error",
                help=(
                    "Exit 3 for fail/not-assessable findings at this severity (default: error); "
                    "none changes only exit policy."
                ),
            )
            command.add_argument(
                "--features", help="Optional keyed table of selected numeric features."
            )
            command.add_argument(
                "--splits", help="Optional JSON plan or outer-only assignment TSV."
            )
        if name == "audit":
            command.add_argument(
                "--ledger", help="Local JSON user declarations, not verified history."
            )
        if name == "evaluate":
            command.add_argument(
                "--features", required=True, help="Explicitly keyed numeric feature table."
            )
            command.add_argument(
                "--splits", required=True, help="Complete single-repeat CV plan or assignment TSV."
            )
        if name == "report":
            command.add_argument(
                "--input",
                required=True,
                help="Compatible report.json; standalone comparison needs its version manifest.",
            )
        if name == "compare":
            command.add_argument(
                "--result",
                action="append",
                required=True,
                metavar="NAME=PATH",
                help="Repeat for distinct design names and private operational JSON records.",
            )
        if name == "demo":
            command.add_argument(
                "--scenario",
                choices=("clean", "repeated", "site_shift"),
                default="clean",
                help="Documented fixed-seed scenario; no performance-based seed search.",
            )
        command.add_argument(
            "--out",
            required=name != "validate",
            help="Output JSON file for init; otherwise a local directory. Optional for validate.",
        )
        command.add_argument(
            "--overwrite", action="store_true", help="Explicitly replace named outputs only."
        )
        if name in {"validate", "audit", "report", "evaluate", "compare", "demo"}:
            command.add_argument(
                "--sensitive-details",
                action="store_true",
                help="Explicit sensitive local report with a visible warning.",
            )
    return parser


def _read_json(path: str | Path, *, max_input_mb: int = 128) -> "JSONObject":
    from neurocvguard.errors import InputValidationError
    from neurocvguard.serialization import strict_json_loads

    source = Path(path)
    if is_remote_path(path) or source.suffix.lower() != ".json":
        raise InputValidationError("Use a local UTF-8 JSON input.")
    limit = max_input_mb * 1024 * 1024
    try:
        if not source.is_file() or source.stat().st_size > limit:
            raise InputValidationError("JSON input is missing or exceeds the input-size limit.")
        with source.open("rb") as handle:
            raw = handle.read(limit + 1)
        if len(raw) > limit:
            raise InputValidationError("JSON input exceeds the input-size limit.")
        data = strict_json_loads(raw.decode("utf-8-sig"))
    except (OSError, UnicodeError):
        raise InputValidationError("Cannot read a local UTF-8 JSON input.") from None
    if not isinstance(data, dict):
        raise InputValidationError("JSON input requires a contract object.")
    return data


def _report_input(path: str) -> "AuditReport | ComparisonResult":
    from neurocvguard.errors import InputValidationError
    from neurocvguard.models import AuditReport, ComparisonResult

    data = _read_json(path)
    if "designs" in data:
        manifest = _read_json(Path(path).with_name("report.manifest.json"))
        if (
            manifest.get("schema_version") != "1.0"
            or manifest.get("result_schema") != "comparison-summary"
        ):
            raise InputValidationError(
                "Comparison report requires its compatible 1.0 version manifest."
            )
        return ComparisonResult.from_dict(data)
    return AuditReport.from_dict(data)


def _logger() -> logging.Logger:
    logger = logging.getLogger("neurocvguard.cli")
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _paths(paths: dict[str, Path]) -> None:
    print("Artifacts in requested output location:")
    for role, path in paths.items():
        safe_name = "".join(char for char in path.name if char.isprintable())[:160]
        print(f"  {role}: {safe_name}")


def _run(args: argparse.Namespace, log: logging.Logger) -> int:
    from neurocvguard import load_cohort, load_split_plan, make_splits, write_report
    from neurocvguard._report_writes import write_bundle
    from neurocvguard.config import AuditConfig, load_config
    from neurocvguard.errors import InputValidationError
    from neurocvguard.reporting import write_configured_report
    from neurocvguard.workflows import audit_workflow

    if args.command == "init":
        destination = Path(args.out)
        if destination.suffix.lower() != ".json":
            raise InputValidationError("Choose a .json starter configuration output.")
        config = AuditConfig()
        paths = write_bundle(
            destination.parent,
            {destination.name: json.dumps(config.to_dict(), indent=2) + "\n"},
            overwrite=args.overwrite,
        )
        print(
            "Starter configuration written. Edit explicit column mappings; "
            "no columns were inferred."
        )
        _paths({"config": paths[destination.name]})
        return 0
    if args.command == "demo":
        from neurocvguard.demo import run_demo
        from neurocvguard.synthetic import SYNTHETIC_NOTICE

        log.warning(SYNTHETIC_NOTICE)
        log.warning("Operational plans, evaluations and demo.private.json are separately private.")
        if args.scenario == "repeated":
            log.warning(
                "Diagnostic only; valid_for_objective=false. Do not report as evidence "
                "for unseen-participant generalization."
            )
        if args.sensitive_details:
            log.warning("Sensitive details explicitly requested for generated fictitious data.")
        demo_result = run_demo(
            output_dir=args.out,
            scenario=args.scenario,
            overwrite=args.overwrite,
            sensitive_details=args.sensitive_details,
            command=args.invocation,
        )
        print(
            f"demo: synthetic=true; scenario={args.scenario}; "
            f"execution={demo_result.execution_status}"
        )
        print("Open report.html in the requested output directory; provenance: demo.private.json.")
        return 0 if demo_result.execution_status == "completed" else 4
    if args.command == "report":
        log.info("Reading compatible report JSON; no audit or statistics will run.")
        rendered_record = _report_input(args.input)
        if args.sensitive_details:
            log.warning("Sensitive report requested. Do not publish without review.")
        paths = write_report(
            rendered_record,
            output_dir=args.out,
            sensitive_details=args.sensitive_details,
            overwrite=args.overwrite,
        )
        print("Report rendered from precomputed values; redacted details cannot be recovered.")
        _paths(paths)
        return 0
    if args.command == "compare":
        from neurocvguard import compare_designs
        from neurocvguard.comparison import load_evaluation

        log.info("Reading private operational evaluations; no fitting or score selection.")
        results = {}
        for supplied in args.result:
            name, separator, path = supplied.partition("=")
            if not separator or not name or not path or name in results:
                raise InputValidationError("Supply distinct --result name=path arguments.")
            results[name] = load_evaluation(path)
        compared = compare_designs(results)
        if any(design.diagnostic_only for design in compared.designs):
            log.warning(
                "Diagnostic only: do not report as evidence for unseen-participant generalization."
            )
        if args.sensitive_details:
            log.warning("Sensitive report requested. Do not publish without review.")
        paths = write_report(
            compared,
            output_dir=args.out,
            sensitive_details=args.sensitive_details,
            overwrite=args.overwrite,
        )
        _paths(paths)
        print(
            f"compare: designs={len(compared.designs)}; "
            "signed score_difference=A-B; metric_unit=participant"
        )
        print(
            "Descriptive design differences, not causal estimates of leakage. "
            "No design winner selected."
        )
        return 0
    log.info("Validating configuration and explicitly keyed local inputs.")
    config = load_config(args.config)
    cohort = load_cohort(args.cohort, config=config, features=getattr(args, "features", None))
    if args.command == "split":
        log.warning(
            "Sensitive operational output: plan.json and assignments.tsv contain observation IDs. "
            "Do not publish without review."
        )
        generated_plan = make_splits(cohort, config=config)
        paths = generated_plan.write(args.out, overwrite=args.overwrite)
        print(
            f"Generated and independently checked {len(generated_plan.folds)} outer folds; "
            "upstream preprocessing is unverified."
        )
        _paths(paths)
        return 0
    plan = load_split_plan(args.splits, cohort=cohort, config=config) if args.splits else None
    if args.command == "evaluate":
        from neurocvguard import evaluate_baseline
        from neurocvguard.reporting import write_evaluation

        assert plan is not None
        log.warning(
            "Sensitive operational output: evaluation.private.json contains fit IDs, "
            "memberships and complete metrics. Do not publish without review."
        )
        log.info("Checking all evaluation prerequisites before fitting fresh outer pipelines.")
        evaluated = evaluate_baseline(cohort, plan, config=config)
        if evaluated.diagnostic_only:
            log.warning(
                "Diagnostic only; valid_for_objective=false. Do not report as evidence "
                "for unseen-participant generalization. "
                "Participant aggregation does not repair training leakage."
            )
        if args.sensitive_details or config.report.sensitive_details:
            log.warning("Sensitive report requested. Do not publish without review.")
        paths = write_evaluation(
            evaluated,
            config=config,
            output_dir=args.out,
            sensitive_details=args.sensitive_details,
            overwrite=args.overwrite,
        )
        _paths(paths)
        completed = sum(fold.status == "completed" for fold in evaluated.folds)
        print(
            f"evaluate: execution={evaluated.execution_status.value}; "
            f"folds_completed={completed}/{len(evaluated.folds)}; metric_unit=participant"
        )
        print("Research baseline only; upstream preprocessing remains unverified.")
        if any(check.rule_id == "NCG-PROV-004" for check in evaluated.preflight_checks):
            log.error("Internal fit-boundary defect; investigate before using any result.")
            return 1
        if evaluated.execution_status != "completed":
            log.error(
                "Evaluation is incomplete; failed folds are retained "
                "and no pooled score is available."
            )
            return 4
        return 0
    ledger_path = getattr(args, "ledger", None)
    ledger: dict[str, object] | None = (
        dict(_read_json(ledger_path, max_input_mb=config.limits.max_input_mb))
        if ledger_path
        else None
    )
    log.info("Computing scoped cohort, partition and declaration checks.")
    result = audit_workflow(cohort, config=config, plan=plan, ledger=ledger)
    if args.out:
        if args.sensitive_details or config.report.sensitive_details:
            log.warning("Sensitive report requested. Do not publish without review.")
        paths = write_configured_report(
            result,
            config=config,
            output_dir=args.out,
            sensitive_details=args.sensitive_details,
            overwrite=args.overwrite,
        )
        _paths(paths)
    counts = {
        status: sum(item.status == status for item in result.checks)
        for status in ("pass", "fail", "not_assessable", "not_applicable")
    }
    print(
        f"{args.command}: execution={result.execution_status.value}; "
        + "; ".join(f"{key}={value}" for key, value in counts.items())
    )
    print(
        "Technical completion is not scientific validity; "
        "upstream preprocessing remains unverified."
    )
    if args.fail_on != "none":
        severities = {"error", "warning"} if args.fail_on == "warning" else {"error"}
        if any(
            check.status in {"fail", "not_assessable"} and check.severity in severities
            for check in result.checks
        ):
            log.warning(
                "Requested findings threshold reached; requested reports have been written. "
                "Findings are unchanged by exit policy."
            )
            return 3
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run local commands with separate result and diagnostic streams.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Explicit arguments or process arguments. Global --debug precedes the command.

    Returns
    -------
    int
        CLI status. Explicit help/version use argparse's successful SystemExit.

    Examples
    --------
    ``main(["init", "--out", "config.json"])`` writes an editable starter.
    """
    parser = _parser()
    args = parser.parse_args(argv)
    args.invocation = tuple(sys.orig_argv) if argv is None else ("neurocvguard", *argv)
    if args.command is None:
        parser.print_help()
        print("Choose a subcommand; use --help for supported workflows.", file=sys.stderr)
        return 2
    log = _logger()
    try:
        return _run(args, log)
    except ConfigurationError:
        log.error(
            "Invalid configuration. Check strict JSON schema 1.0, "
            "unknown keys and explicit column mappings."
        )
        return 2
    except UnsupportedDesignError:
        log.error(
            "Design is infeasible or unsupported. Review target stability, protected "
            "relationships, domains and requested fold counts; no fitting occurred."
        )
        return 3
    except (NeuroCVguardError, OSError):
        if args.command == "compare":
            log.error(
                "Compare requires at least two distinct --result name=path arguments pointing "
                "to local evaluation.private.json operational records. Public report.json "
                "omits required digests and fit metadata; do not reconstruct them. Check "
                "schema 1.0, local JSON limits and output conflicts; choose a fresh output "
                "directory or explicit --overwrite."
            )
            return 2
        log.error(
            "Input or output validation failed. Check compatible schema 1.0, local formats, "
            "string keys, selected columns, resource limits and existing outputs; use a new "
            "destination or explicit --overwrite. Report accepts exported report JSON, "
            "not private evaluation records."
        )
        return 2
    except Exception as error:
        log.error(
            "Unexpected internal failure; no success is claimed. Retry with --debug "
            "before the command for sanitized stack locations."
        )
        if args.debug:
            print(
                "Sanitized traceback (no exception values, source text, locals or input paths):",
                file=sys.stderr,
            )
            for frame in traceback.extract_tb(error.__traceback__):
                print(
                    f"  {Path(frame.filename).name}:{frame.lineno} in {frame.name}", file=sys.stderr
                )
            print(type(error).__name__, file=sys.stderr)
        return 1
