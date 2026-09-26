"""Offline reports from precomputed records, using the same projection as to_dict."""

import csv
import io
import json
from collections import Counter
from importlib.resources import files
from pathlib import Path
from typing import cast

from jinja2 import Environment, PackageLoader, StrictUndefined, TemplateError, select_autoescape

from neurocvguard import __version__
from neurocvguard._report_writes import write_bundle
from neurocvguard.config import AuditConfig
from neurocvguard.errors import InputValidationError
from neurocvguard.models import AuditReport, ComparisonResult, EvaluationResult
from neurocvguard.rules import get_rule
from neurocvguard.serialization import JSONObject, JSONValue, canonical_json

ReportRecord = AuditReport | EvaluationResult | ComparisonResult


def _project(result: ReportRecord, sensitive: bool) -> JSONObject:
    if not isinstance(result, (AuditReport, EvaluationResult, ComparisonResult)):
        raise InputValidationError(
            "Supply an AuditReport, EvaluationResult or ComparisonResult record."
        )
    if type(sensitive) is not bool:
        raise InputValidationError("sensitive_details must be an explicit boolean.")
    return result.to_dict(sensitive_details=sensitive)


def _render(data: JSONObject, sensitive: bool) -> str:
    # Both source strings are installed package data, never caller-selected paths.
    try:
        assets = files("neurocvguard").joinpath("templates")
        if not all(
            assets.joinpath(name).read_text(encoding="utf-8").strip()
            for name in ("report.html", "report.css")
        ):
            raise InputValidationError("Report assets are empty; reinstall the package.")
        environment = Environment(
            loader=PackageLoader("neurocvguard", "templates"),
            autoescape=select_autoescape(default=True, default_for_string=True),
            undefined=StrictUndefined,
        )
        environment.filters["pretty_json"] = lambda value: json.dumps(
            value, ensure_ascii=False, indent=2, allow_nan=False
        )
        checks = cast(list[JSONObject], data.get("checks", []))
        counts = Counter(str(check["status"]) for check in checks)
        references = []
        for rule_id in sorted({str(check["rule_id"]) for check in checks} | {"NCG-REPORT-001"}):
            try:
                rule = get_rule(rule_id)
                references.append({"id": rule.id, "name": rule.name, "meaning": rule.meaning})
            except KeyError:
                references.append(
                    {
                        "id": rule_id,
                        "name": "Supplied rule",
                        "meaning": "See the source record for this scoped check.",
                    }
                )
        return environment.get_template("report.html").render(
            report=data,
            checks=checks,
            counts=counts,
            sensitive=sensitive,
            references=references,
            version=__version__,
            comparison_only="designs" in data,
            incomplete=not checks
            or counts["not_assessable"] > 0
            or data.get("execution_status") != "completed",
        )
    except (OSError, TemplateError, ModuleNotFoundError):
        raise InputValidationError(
            "Cannot render packaged report assets; reinstall or repair the package."
        ) from None


def render_report(result: ReportRecord, *, sensitive_details: bool = False) -> str:
    """Render self-contained HTML from the record projection without writing files.

    Parameters
    ----------
    result : AuditReport, EvaluationResult or ComparisonResult
        Already computed schema-backed record; no audit or statistic is rerun.
    sensitive_details : bool, optional
        Explicit sensitive output, visibly labelled and autoescaped.

    Returns
    -------
    str
        Static HTML with packaged inline CSS and no JavaScript/network assets.
    """
    return _render(_project(result, sensitive_details), sensitive_details)


def write_report(
    result: ReportRecord,
    *,
    output_dir: str | Path,
    sensitive_details: bool = False,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Write projected report.json, self-contained report.html and a version manifest.

    Parameters
    ----------
    result : AuditReport, EvaluationResult or ComparisonResult
        Precomputed typed record. Plain dictionaries must first be schema-validated.
    output_dir : str or Path
        Explicit local directory; existing artifacts are preserved by default.
    sensitive_details : bool, optional
        Enable sensitive details only by an explicit True, never by input provenance.
    overwrite : bool, optional
        Permit replacement of these named regular report files.

    Returns
    -------
    dict of str to Path
        json, html and manifest paths. No identity-bearing operational record is written.

    Raises
    ------
    InputValidationError
        Invalid options, missing assets, output conflict or failed write.

    Notes
    -----
    Every file is staged before replacement. Ordinary commit failures roll back
    changed files. This is not a multi-file power-loss transaction; recovery copies
    are retained if storage also prevents rollback. ComparisonResult retains its
    standalone comparison-summary schema; the manifest identifies its version.

    Examples
    --------
    ``paths = write_report(report, output_dir="local-report")``
    """
    data = _project(result, sensitive_details)
    return _write_projected_report(
        data,
        comparison=isinstance(result, ComparisonResult),
        output_dir=output_dir,
        sensitive_details=sensitive_details,
        overwrite=overwrite,
    )


def write_configured_report(
    result: ReportRecord,
    *,
    config: AuditConfig,
    output_dir: str | Path,
    sensitive_details: bool = False,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Write once using the configured small-cell threshold and explicit sensitivity.

    This orchestration helper retains the public writer's default projection while
    allowing config-driven workflows to honor their declared privacy settings.
    """
    if type(sensitive_details) is not bool or not isinstance(config, AuditConfig):
        raise InputValidationError("Supply a validated config and explicit sensitivity boolean.")
    sensitive = sensitive_details or config.report.sensitive_details
    data = result.to_dict(
        sensitive_details=sensitive,
        small_cell_threshold=config.report.small_cell_threshold,
    )
    return _write_projected_report(
        data,
        comparison=isinstance(result, ComparisonResult),
        output_dir=output_dir,
        sensitive_details=sensitive,
        overwrite=overwrite,
    )


def _write_projected_report(
    data: JSONObject,
    *,
    comparison: bool,
    output_dir: str | Path,
    sensitive_details: bool,
    overwrite: bool,
) -> dict[str, Path]:
    html = _render(data, sensitive_details)
    manifest = {
        "schema_version": "1.0",
        "result_schema": "comparison-summary" if comparison else "audit-report",
        "tool_version": __version__,
        "sensitive_details": sensitive_details,
        "artifacts": ["report.json", "report.html"],
        "operational_records_included": False,
    }
    contents = {
        "report.json": canonical_json(data) + "\n",
        "report.html": html,
        "report.manifest.json": canonical_json(manifest) + "\n",
    }
    paths = write_bundle(output_dir, contents, overwrite=overwrite)
    return {
        "json": paths["report.json"],
        "html": paths["report.html"],
        "manifest": paths["report.manifest.json"],
    }


def _spreadsheet_cell(value: str) -> str:
    candidate = value.lstrip("\ufeff \t\r\n")
    return (
        "'" + value
        if (value.startswith(("\t", "\r", "\n")) or candidate.startswith(("=", "+", "-", "@")))
        else value
    )


def write_findings_csv(
    result: AuditReport | EvaluationResult,
    *,
    path: str | Path,
    sensitive_details: bool = False,
    overwrite: bool = False,
) -> Path:
    """Explicit optional human-readable findings CSV with formula-neutralized cells.

    Uses the same privacy projection as reports. This is not canonical split TSV
    and never changes observation keys or operational records. Sensitive output
    has a sensitivity column. No CSV is silently added by write_report.
    """
    data = _project(result, sensitive_details)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        (
            "sensitivity",
            "rule_id",
            "status",
            "severity",
            "evidence_kind",
            "scope",
            "message",
            "recommendation",
        )
    )
    for check in cast(list[JSONObject], data.get("checks", [])):
        row: list[JSONValue] = [
            "SENSITIVE: do not publish without review"
            if sensitive_details
            else "Public projection",
            *[check[name] for name in ("rule_id", "status", "severity", "evidence_kind")],
            canonical_json(check["scope"]),
            check["message"],
            check["recommendation"],
        ]
        writer.writerow(_spreadsheet_cell(str(value)) for value in row)
    destination = Path(path)
    if destination.suffix.lower() != ".csv":
        raise InputValidationError("Use a local .csv path for the human findings export.")
    return write_bundle(
        destination.parent, {destination.name: stream.getvalue()}, overwrite=overwrite
    )[destination.name]
