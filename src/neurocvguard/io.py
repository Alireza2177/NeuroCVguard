"""Strict split-plan import and binding for validated in-memory cohorts.

Cohort/feature file ingestion and keyed joins (S02) are not implemented here.
"""

import csv
import io
import os
import tempfile
from dataclasses import replace
from pathlib import Path

from neurocvguard.config import AuditConfig
from neurocvguard.errors import ConfigurationError, InputValidationError, SplitValidationError
from neurocvguard.identity import _missing, _valid_label, _validated_metadata
from neurocvguard.models import AuditReport, Cohort, PlanOrigin, ReportStatus, SplitFold, SplitPlan
from neurocvguard.serialization import (
    JSONObject,
    JSONValue,
    canonical_json,
    json_digest,
    strict_json_loads,
)


def cohort_digest(cohort: Cohort) -> str:
    """Hash role mapping and mapped metadata, excluding features and unrelated columns.

    Parameters
    ----------
    cohort : Cohort
        Validated in-memory metadata with explicit observation identities.

    Returns
    -------
    str
        SHA-256 of canonical UTF-8 JSON: columns plus records sorted by observation ID.

    Raises
    ------
    InputValidationError
        Identity corruption or an unvalidated mapped categorical value prevents binding.

    Examples
    --------
    ``digest = cohort_digest(cohort)`` is an integrity aid, never anonymization.

    Notes
    -----
    Missing mapped fields/cells become explicit nulls. The mapping itself preserves
    which roles were requested. Unicode and identity text are not normalized.
    This minimal binding dependency does not implement S02 table ingestion.
    """
    data = _validated_metadata(cohort)
    mapping = cohort.columns.to_dict()
    names = {value for value in mapping.values() if isinstance(value, str)}
    names.update(cohort.columns.independence)
    names.update(cohort.columns.categorical_covariates)
    records: list[JSONValue] = []
    ordered_names = sorted(names)
    selected = data.reindex(columns=ordered_names).sort_values(cohort.columns.observation_id)
    for values in selected.itertuples(index=False, name=None):
        record: JSONObject = {}
        for name, value in zip(ordered_names, values, strict=True):
            if _missing(value):
                record[name] = None
            elif isinstance(value, str):
                record[name] = value
            else:
                raise InputValidationError(
                    "Mapped metadata must contain validated strings or missing values "
                    "before binding."
                )
        records.append(record)
    return json_digest({"columns": mapping, "records": records})


def _plan_context(cohort: Cohort, plan: SplitPlan, config: AuditConfig) -> str:
    if cohort.columns != config.columns:
        raise ConfigurationError(
            "Cohort roles differ from config.columns; use the matching mapping."
        )
    if plan.objective != config.study.objective:
        raise SplitValidationError("Plan objective must equal the configured study objective.")
    for fold in plan.folds:
        labels = [fold.repeat_id, fold.fold_id, *fold.train_ids, *fold.test_ids]
        for inner in fold.inner_folds or ():
            labels.extend((inner.inner_fold_id, *inner.train_ids, *inner.validation_ids))
        if any(not _valid_label(label) for label in labels):
            raise SplitValidationError(
                "Plan identities must be non-missing strings without surrounding whitespace "
                "or control characters; repair the source without automatic normalization."
            )
    digest = cohort_digest(cohort)
    if plan.cohort_digest is not None and plan.cohort_digest != digest:
        raise SplitValidationError(
            "Cohort digest mismatch; supply the original mapped metadata or explicitly "
            "review a new plan."
        )
    return digest


def _all_members(plan: SplitPlan) -> set[str]:
    members: set[str] = set()
    for fold in plan.folds:
        members.update((*fold.train_ids, *fold.test_ids))
        for inner in fold.inner_folds or ():
            members.update((*inner.train_ids, *inner.validation_ids))
    return members


def _read_plan_file(path: Path, config: AuditConfig) -> str:
    limit = config.limits.max_input_mb * 1024 * 1024
    if (
        "://" in str(path)
        or str(path).startswith("\\\\")
        or path.suffix.lower() not in {".json", ".tsv"}
    ):
        raise InputValidationError("Use a local uncompressed .json or outer-only .tsv split plan.")
    try:
        if not path.is_file() or path.stat().st_size > limit:
            raise InputValidationError("Split plan file is missing or exceeds limits.max_input_mb.")
        with path.open("rb") as handle:
            content = handle.read(limit + 1)
        if len(content) > limit:
            raise InputValidationError("Split plan exceeds limits.max_input_mb.")
        return content.decode("utf-8-sig")
    except (OSError, UnicodeError):
        raise InputValidationError("Cannot read the split plan as a local UTF-8 file.") from None


def _tsv_plan(text: str, config: AuditConfig) -> SplitPlan:
    header = ("repeat_id", "fold_id", "role", "observation_id")
    grouped: dict[tuple[str, str], dict[str, list[str]]] = {}
    seen = set()
    try:
        reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t", strict=True)
        if tuple(next(reader, ())) != header:
            raise InputValidationError(
                "Assignment TSV requires exact unique columns: repeat_id, fold_id, role, "
                "observation_id."
            )
        for count, row in enumerate(reader, 1):
            if count > config.limits.max_rows:
                raise InputValidationError(
                    "Assignment rows exceed limits.max_rows; review the limit explicitly."
                )
            if len(row) != len(header):
                raise InputValidationError(
                    "Malformed assignment TSV row; supply exactly four fields."
                )
            repeat, fold, role, observation = row
            if role not in {"train", "test"}:
                raise InputValidationError(
                    "Invalid assignment role; only train and test are supported in TSV."
                )
            if any(not _valid_label(value) for value in (repeat, fold, observation)):
                raise InputValidationError(
                    "Invalid TSV identity; use non-missing, unpadded string keys."
                )
            key = (repeat, fold, role, observation)
            if key in seen:
                raise SplitValidationError(
                    "Duplicate role/observation membership in assignment TSV."
                )
            seen.add(key)
            grouped.setdefault((repeat, fold), {"train": [], "test": []})[role].append(observation)
    except csv.Error:
        raise InputValidationError(
            "Malformed assignment TSV syntax; repair quoting or field sizes."
        ) from None
    folds = tuple(
        SplitFold(repeat, fold, tuple(roles["train"]), tuple(roles["test"]))
        for (repeat, fold), roles in grouped.items()
    )
    payload = [fold._as_dict() for fold in folds]
    return SplitPlan(
        "1.0",
        "imported-" + json_digest(payload),
        PlanOrigin.IMPORTED,
        None,
        config.study.objective,
        "imported",
        None,
        folds,
    )


def load_split_plan(
    source: str | Path | dict[str, object],
    *,
    cohort: Cohort,
    config: AuditConfig,
) -> SplitPlan:
    """Load JSON/dict or outer-only TSV, check identities and bind imported metadata.

    Parameters
    ----------
    source : str, Path or dict
        Local .json/.tsv path or a schema-shaped mapping. Strings are paths, not JSON code.
    cohort : Cohort
        Validated in-memory cohort; no cohort loading or joining occurs.
    config : AuditConfig
        Explicit roles/objective and file/assignment-row limits.

    Returns
    -------
    SplitPlan
        New identity-bound operational record. Design violations remain auditable;
        binding is not approval of separation, coverage or training feasibility.

    Raises
    ------
    InputValidationError, SplitValidationError, ConfigurationError
        Malformed input, duplicate/unknown identity, incompatible objective/mapping or digest.

    Examples
    --------
    ``plan = load_split_plan("assignments.tsv", cohort=cohort, config=config)``

    Notes
    -----
    Imported origin and unknown seed are retained. Memberships are not repaired.
    Use audit_splits next; observation overlap is never waived by diagnostics.
    """
    if isinstance(source, dict):
        plan = SplitPlan.from_dict(source)
    else:
        path = Path(source)
        text = _read_plan_file(path, config)
        plan = (
            _tsv_plan(text, config)
            if path.suffix.lower() == ".tsv"
            else SplitPlan.from_dict(strict_json_loads(text))
        )
    digest = _plan_context(cohort, plan, config)
    unknown = _all_members(plan) - set(cohort.observation_order)
    if unknown:
        raise SplitValidationError(
            f"Plan contains {len(unknown)} unknown observation IDs; supply matching keyed metadata."
        )
    return replace(plan, cohort_digest=digest) if plan.cohort_digest is None else plan


def _write_sensitive_files(
    output_dir: str | Path, contents: dict[str, str], *, overwrite: bool
) -> dict[str, Path]:
    if type(overwrite) is not bool:
        raise InputValidationError("overwrite must be an explicit boolean.")
    destination = Path(output_dir)
    if "://" in str(output_dir) or str(destination).startswith("\\\\"):
        raise InputValidationError("Choose a local directory for sensitive split artifacts.")
    paths = {name: destination / name for name in contents}
    try:
        # Check all names before writing any artifact, including dangling links.
        if any(
            path.is_symlink() or (path.exists() and (not overwrite or not path.is_file()))
            for path in paths.values()
        ):
            raise InputValidationError(
                "Split output already exists or is not a regular file. Choose a new directory "
                "or explicitly set overwrite=True for regular files."
            )
        destination.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".neurocvguard-", dir=destination) as staging:
            staged = {name: Path(staging) / name for name in contents}
            for name, text in contents.items():
                with staged[name].open("x", encoding="utf-8", newline="\n") as handle:
                    handle.write(text)
                staged[name].chmod(0o600)
            reserved: list[Path] = []
            if not overwrite:
                try:
                    for path in paths.values():
                        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                        os.close(descriptor)
                        reserved.append(path)
                except OSError:
                    # These are only empty files exclusively created by this invocation.
                    for path in reserved:
                        path.unlink()
                    raise
            # Each file replacement is atomic, but the bundle is not a filesystem transaction.
            for name, path in paths.items():
                os.replace(staged[name], path)
    except OSError:
        raise InputValidationError(
            "Could not write the sensitive split artifacts. Check permissions and destination "
            "conflicts; a storage failure during replacement may leave a partial bundle."
        ) from None
    return paths


def write_split_plan(
    plan: SplitPlan, *, output_dir: str | Path, overwrite: bool = False
) -> dict[str, Path]:
    """Write sensitive plan.json, outer assignments.tsv and an explicit privacy notice.

    Parameters
    ----------
    plan : SplitPlan
        Structurally valid operational record; this writer is not a scientific audit.
    output_dir : str or Path
        Explicit local output directory.
    overwrite : bool, optional
        Replace these named regular artifacts only when explicitly True.

    Returns
    -------
    dict of str to Path
        Named artifact paths, including generation_report when captured by make_splits.

    Raises
    ------
    InputValidationError
        Invalid identity, existing output, unsupported path or write failure.

    Examples
    --------
    ``plan.write("local-splits")`` delegates to this writer. All outputs are sensitive.
    """
    if any(
        (Path(output_dir) / name).exists()
        for name in ("rejected-plan.private.json", "REJECTED.SENSITIVE.txt")
    ):
        raise InputValidationError("Choose a separate directory from rejected-plan diagnostics.")
    text = io.StringIO(newline="")
    writer = csv.writer(text, delimiter="\t", lineterminator="\n")
    writer.writerow(("repeat_id", "fold_id", "role", "observation_id"))
    for fold in plan.folds:
        labels = [fold.repeat_id, fold.fold_id, *fold.train_ids, *fold.test_ids]
        for inner in fold.inner_folds or ():
            labels.extend((inner.inner_fold_id, *inner.train_ids, *inner.validation_ids))
        if any(not _valid_label(label) for label in labels):
            raise InputValidationError(
                "Split export requires valid, unpadded identities without control characters."
            )
        for role, members in (("train", fold.train_ids), ("test", fold.test_ids)):
            writer.writerows((fold.repeat_id, fold.fold_id, role, member) for member in members)
    contents = {
        "plan.json": canonical_json(plan.to_operational_dict()) + "\n",
        "assignments.tsv": text.getvalue(),
        "README.SENSITIVE.txt": (
            "SENSITIVE LOCAL RESEARCH ARTIFACTS\n"
            "plan.json and assignments.tsv contain observation identities. Do "
            "not publish without review.\n"
            "JSON is canonical and retains inner folds; TSV is an outer-only convenience view.\n"
            "Writing or loading a plan does not verify its scientific design or prior execution.\n"
            "generation.private.json contains sensitive audit details and "
            "dependency versions when captured.\n"
            "No runtime generation history is inferred from a loaded plan or "
            "from current library versions.\n"
        ),
    }
    names = {
        "plan": "plan.json",
        "assignments": "assignments.tsv",
        "notice": "README.SENSITIVE.txt",
    }
    if plan.generation_report is not None:
        if plan.generation_report.execution_status == ReportStatus.BLOCKED:
            raise InputValidationError(
                "A rejected generation report cannot be exported as a usable plan."
            )
        contents["generation.private.json"] = (
            canonical_json(plan.generation_report.to_dict(sensitive_details=True)) + "\n"
        )
        names["generation_report"] = "generation.private.json"
    elif (Path(output_dir) / "generation.private.json").exists():
        raise InputValidationError(
            "Existing generation provenance cannot be attributed to this "
            "plan. Choose a new directory."
        )
    paths = _write_sensitive_files(output_dir, contents, overwrite=overwrite)
    return {role: paths[name] for role, name in names.items()}


def write_rejected_plan(
    report: AuditReport, *, output_dir: str | Path, overwrite: bool = False
) -> dict[str, Path]:
    """Save blocked planning diagnostics separately, without a usable plan or assignments.

    Parameters
    ----------
    report : AuditReport
        The blocked report exposed by PlanningError.report.
    output_dir : str or Path
        Local diagnostic directory, separate from usable-plan exports.
    overwrite : bool, optional
        Explicit permission to replace named diagnostic files.

    Returns
    -------
    dict of str to Path
        rejected-plan.private.json and a sensitive rejection notice.

    Raises
    ------
    InputValidationError
        Report is not blocked, outputs conflict, or writing fails.

    Examples
    --------
    ``write_rejected_plan(error.report, output_dir="rejected")`` is an explicit local export.
    """
    if report.execution_status != ReportStatus.BLOCKED:
        raise InputValidationError("Rejected-plan export requires a blocked planning report.")
    if any(
        (Path(output_dir) / name).exists()
        for name in ("plan.json", "assignments.tsv", "generation.private.json")
    ):
        raise InputValidationError("Choose a separate directory from usable-plan artifacts.")
    return _write_sensitive_files(
        output_dir,
        {
            "rejected-plan.private.json": canonical_json(report.to_dict(sensitive_details=True))
            + "\n",
            "REJECTED.SENSITIVE.txt": (
                "SENSITIVE REJECTED-PLAN DIAGNOSTICS\nNo usable plan was produced.\n"
            ),
        },
        overwrite=overwrite,
    )
