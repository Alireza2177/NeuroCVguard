"""Offline synthetic workflows using the ordinary public audits and evaluator."""

import argparse
import hashlib
import json
import platform
import sys
import tempfile
from dataclasses import dataclass, replace
from importlib.metadata import version
from pathlib import Path

from sklearn.model_selection import StratifiedKFold

from neurocvguard import (
    __version__,
    compare_designs,
    evaluate_baseline,
    load_cohort,
    load_split_plan,
    make_splits,
)
from neurocvguard._report_writes import write_bundle
from neurocvguard.config import (
    AuditConfig,
    ColumnMap,
    Objective,
    SplitConfig,
    SplitScheme,
    StudyConfig,
)
from neurocvguard.errors import InputValidationError, NeuroCVguardError, UnsupportedDesignError
from neurocvguard.io import cohort_digest, feature_digest
from neurocvguard.models import AuditReport, Cohort, EvaluationResult, SplitPlan
from neurocvguard.reporting import _report_contents
from neurocvguard.serialization import JSONObject, canonical_json
from neurocvguard.synthetic import (
    SYNTHETIC_NOTICE,
    SyntheticParameters,
    generate_synthetic,
    scenario_parameters,
)
from neurocvguard.workflows import audit_workflow


@dataclass(frozen=True)
class DemoRun:
    """Written synthetic artifacts; completion is separate from scientific validity."""

    paths: dict[str, Path]
    execution_status: str


def _save_report(work: Path, report: AuditReport, sensitive: bool, prefix: str = "") -> None:
    labelled = replace(report, limitations=(*report.limitations, SYNTHETIC_NOTICE))
    data = labelled.to_dict(sensitive_details=sensitive)
    for name, content in _report_contents(
        data, comparison=False, sensitive_details=sensitive
    ).items():
        if name == "report.manifest.json" and prefix:
            manifest = json.loads(content)
            manifest["artifacts"] = [prefix + item for item in manifest["artifacts"]]
            content = canonical_json(manifest) + "\n"
        (work / (prefix + name)).write_text(content, encoding="utf-8", newline="\n")


def _evaluate(
    work: Path, name: str, cohort: Cohort, plan: SplitPlan, config: AuditConfig, sensitive: bool
) -> EvaluationResult:
    result = evaluate_baseline(cohort, plan, config=config)
    (work / f"{name}.evaluation.private.json").write_text(
        canonical_json(result.to_operational_dict()) + "\n", encoding="utf-8"
    )
    (work / f"{name}.plan.json").write_text(
        canonical_json(plan.to_operational_dict()) + "\n", encoding="utf-8"
    )
    (work / f"{name}.config.json").write_text(
        canonical_json(config.to_dict()) + "\n", encoding="utf-8"
    )
    _save_report(
        work,
        AuditReport.from_dict(result.to_dict(sensitive_details=sensitive)),
        sensitive,
        name + ".",
    )
    return result


def _row_random_plan(cohort: Cohort, config: AuditConfig) -> SplitPlan:
    """Explicit educational observation split, never a fallback/default generator."""
    metadata = cohort.metadata
    splitter = StratifiedKFold(n_splits=3, shuffle=True, random_state=config.split.seed)
    assert config.columns.target is not None
    ids = metadata[config.columns.observation_id].to_numpy()
    folds = [
        {
            "repeat_id": "0",
            "fold_id": str(i),
            "train_ids": ids[train].tolist(),
            "test_ids": ids[test].tolist(),
        }
        for i, (train, test) in enumerate(splitter.split(ids, metadata[config.columns.target]))
    ]
    return load_split_plan(
        {
            "schema_version": "1.0",
            "plan_id": "synthetic-observation-random",
            "origin": "imported",
            "objective": "unseen_participant",
            "scheme": "imported",
            "seed": config.split.seed,
            "cohort_digest": None,
            "folds": folds,
        },
        cohort=cohort,
        config=config,
    )


def _comparison_report(base: AuditReport, results: dict[str, EvaluationResult]) -> AuditReport:
    return replace(
        base,
        result_type="comparison",
        objective=Objective.AUDIT_ONLY,
        checks=(),
        comparison_summary=compare_designs(results),
    )


def _provenance_example(work: Path, cohort: Cohort, config: AuditConfig, sensitive: bool) -> None:
    ledger: JSONObject = {
        "schema_version": "1.0",
        "source": "user_declaration",
        "events": [
            {
                "event_id": "synthetic-declared-global-pca",
                "transform": "PCA",
                "data_dependent": True,
                "repeat_id": None,
                "fold_id": None,
                "inner_fold_id": None,
                "fit_scope": "all_cohort",
                "fit_ids": None,
                "uses_target": False,
                "note": "Fictitious declaration; no PCA actually fitted.",
            }
        ],
    }
    (work / "ledger.json").write_text(canonical_json(ledger) + "\n", encoding="utf-8")
    unknown = audit_workflow(cohort, config=config)
    declaration: dict[str, object] = dict(ledger)
    declared = audit_workflow(cohort, config=config, ledger=declaration)
    _save_report(work, unknown, sensitive, "unknown.")
    _save_report(work, declared, sensitive)


def _workflow(
    work: Path, scenario: str, p: SyntheticParameters, sensitive: bool, example: int | None
) -> tuple[Cohort, AuditConfig, bool]:
    data = generate_synthetic(p)
    metadata, features, config = data.metadata, data.features, data.config()
    if example == 5:
        # Simulate an extracted local feature table with explicit custom key/role mappings.
        metadata = metadata.rename(
            columns={"observation_id": "scan_key", "subject_id": "person_key"}
        )
        features = features.rename(columns={"observation_id": "scan_key"}).iloc[::-1].copy()
        config = replace(
            config,
            columns=ColumnMap(
                observation_id="scan_key",
                subject_id="person_key",
                target="target",
                session="session",
            ),
        )
    metadata.to_csv(work / "cohort.tsv", sep="\t", index=False, lineterminator="\n")
    features.to_csv(work / "features.tsv", sep="\t", index=False, lineterminator="\n")
    cohort = load_cohort(work / "cohort.tsv", config=config, features=work / "features.tsv")
    (work / "config.json").write_text(canonical_json(config.to_dict()) + "\n", encoding="utf-8")
    if example == 4:
        _provenance_example(work, cohort, config, sensitive)
        return cohort, config, True
    participant_plan = make_splits(cohort, config=config)
    base = audit_workflow(cohort, config=config, plan=participant_plan)
    _save_report(work, base, sensitive, "audit.")
    participant = _evaluate(work, "participant", cohort, participant_plan, config, sensitive)
    completed = participant.execution_status == "completed"
    if scenario == "clean":
        _save_report(
            work, AuditReport.from_dict(participant.to_dict(sensitive_details=sensitive)), sensitive
        )
    else:
        if scenario == "repeated":
            other_config = replace(
                config, evaluation=replace(config.evaluation, diagnostic_allow_subject_overlap=True)
            )
            other_plan = _row_random_plan(cohort, other_config)
            name = "observation-diagnostic"
        else:
            other_config = replace(
                config,
                study=StudyConfig(Objective.UNSEEN_SITE),
                split=SplitConfig(SplitScheme.LEAVE_ONE_SITE_OUT, None, p.seed),
            )
            other_plan = make_splits(cohort, config=other_config)
            name = "site-held-out"
        other = _evaluate(work, name, cohort, other_plan, other_config, sensitive)
        completed = completed and other.execution_status == "completed"
        _save_report(
            work,
            _comparison_report(base, {"participant-disjoint": participant, name: other}),
            sensitive,
        )
    return cohort, config, completed


def _run_synthetic(
    output_dir: str | Path,
    scenario: str,
    parameters: SyntheticParameters,
    sensitive_details: bool,
    overwrite: bool,
    command: tuple[str, ...] | None,
    example: int | None,
) -> DemoRun:
    if type(sensitive_details) is not bool or type(overwrite) is not bool:
        raise InputValidationError("Demo sensitivity and overwrite must be explicit booleans.")
    destination = Path(output_dir)
    if (
        "://" in str(output_dir)
        or str(output_dir).startswith(("\\\\", "//"))
        or destination.is_symlink()
    ):
        raise InputValidationError("Choose a local regular demo output directory.")
    if not overwrite and (destination / "demo.private.json").exists():
        raise InputValidationError(
            "Demo already exists; choose a new output directory or overwrite."
        )
    with tempfile.TemporaryDirectory(prefix="neurocvguard-synthetic-") as directory:
        work = Path(directory)
        cohort, config, complete = _workflow(work, scenario, parameters, sensitive_details, example)
        contents = {path.name: path.read_text(encoding="utf-8") for path in work.iterdir()}
        contents["README.SYNTHETIC.txt"] = (
            SYNTHETIC_NOTICE + "\nScenario: " + scenario + "\n"
            "Generated locally; no download or account. Default reports are privacy-projected.\n"
            "*.plan.json, *.evaluation.private.json and demo.private.json "
            "are operational records.\n"
            "Even these fictitious operational records are marked private to teach the boundary.\n"
            "Repeated scenario is an opt-in invalid diagnostic; "
            "never use it as a recommended fix.\n"
            "Site-held-out and participant-disjoint estimates answer different questions.\n"
            "Unknown upstream preprocessing remains unassessable. Freeze real evaluation plans.\n"
            "The provenance example declares global PCA but never fits PCA or proves its history.\n"
        )
        manifest: JSONObject = {
            "format": "neurocvguard.synthetic-demo.private",
            "schema_version": "1.0",
            "sensitive": True,
            "synthetic": True,
            "notice": SYNTHETIC_NOTICE,
            "scenario": scenario,
            "example": example,
            "parameters": parameters.to_dict(),
            "config": config.to_dict(),
            "command": list(command) if command is not None else None,
            "invocation": "process" if command is not None else "Python API",
            "execution_status": "completed" if complete else "incomplete",
            "sensitive_details": sensitive_details,
            "cohort_digest": cohort_digest(cohort),
            "feature_digest": feature_digest(cohort),
            "versions": {
                "python": platform.python_version(),
                "neurocvguard": __version__,
                **{name: version(name) for name in ("numpy", "pandas", "scipy", "scikit-learn")},
            },
            "output_sha256": {
                name: hashlib.sha256(content.encode("utf-8")).hexdigest()
                for name, content in sorted(contents.items())
            },
        }
        contents["demo.private.json"] = canonical_json(manifest) + "\n"
        paths = write_bundle(destination, contents, overwrite=overwrite)
    return DemoRun(paths, "completed" if complete else "incomplete")


def run_demo(
    *,
    output_dir: str | Path,
    scenario: str = "clean",
    parameters: SyntheticParameters | None = None,
    sensitive_details: bool = False,
    overwrite: bool = False,
    command: tuple[str, ...] | None = None,
) -> DemoRun:
    """Generate, join, audit, split, evaluate and report without external input or network.

    Default clean uses participant-disjoint CV. repeated explicitly requests the
    narrow row-random diagnostic; site_shift compares different domain objectives.
    Output is staged as one flat atomic bundle; existing files require overwrite.
    Explicit parameters replace the entire preset and are recorded without tuning.
    """
    preset = scenario_parameters(scenario)
    return _run_synthetic(
        output_dir,
        scenario,
        preset if parameters is None else parameters,
        sensitive_details,
        overwrite,
        command,
        None,
    )


def run_example(
    number: int,
    *,
    output_dir: str | Path,
    sensitive_details: bool = False,
    overwrite: bool = False,
    command: tuple[str, ...] | None = None,
) -> DemoRun:
    """Run one of five self-contained tutorials; no repository fixtures are loaded."""
    if type(number) is not int or number not in range(1, 6):
        raise InputValidationError("Choose example 1 through 5.")
    scenario = {2: "repeated", 3: "site_shift"}.get(number, "clean")
    p = scenario_parameters(scenario)
    if number == 3:
        # Explicitly isolate class-associated domains; retain all rows and the fixed seed.
        p = replace(p, site_target_association=1.0)
    return _run_synthetic(output_dir, scenario, p, sensitive_details, overwrite, command, number)


def example_main(number: int) -> int:
    """Shared argument handling for the five shipped tutorial scripts."""
    parser = argparse.ArgumentParser(description=SYNTHETIC_NOTICE)
    parser.add_argument("--out", required=True, help="Fresh local output directory.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--sensitive-details", action="store_true")
    args = parser.parse_args()
    print(SYNTHETIC_NOTICE, file=sys.stderr)
    print("Operational demo records are separately marked private.", file=sys.stderr)
    if number == 2:
        print(
            "Diagnostic only; valid_for_objective=false. Do not report as evidence for "
            "unseen-participant generalization.",
            file=sys.stderr,
        )
    if args.sensitive_details:
        print(
            "Sensitive details explicitly requested for generated fictitious data.", file=sys.stderr
        )
    try:
        result = run_example(
            number,
            output_dir=args.out,
            overwrite=args.overwrite,
            sensitive_details=args.sensitive_details,
            command=tuple(sys.orig_argv),
        )
    except UnsupportedDesignError:
        print("Unsupported synthetic design; no fallback or seed search.", file=sys.stderr)
        return 3
    except (NeuroCVguardError, OSError):
        print(
            "Cannot complete example; check local output conflicts and permissions.",
            file=sys.stderr,
        )
        return 2
    print(f"Synthetic example {number:02d}: {result.execution_status}; open report.html in --out.")
    return 0 if result.execution_status == "completed" else 4
