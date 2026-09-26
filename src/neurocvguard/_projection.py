"""Shared conservative privacy projection for records and offline reports."""

import re
from collections.abc import Mapping
from typing import cast

from neurocvguard import __version__
from neurocvguard._report_tables import association_display
from neurocvguard.errors import InputValidationError
from neurocvguard.models import (
    AuditReport,
    CheckResult,
    CheckStatus,
    ComparisonResult,
    EvaluationResult,
    MetricSet,
)
from neurocvguard.rules import (
    ASSOCIATION_RULES,
    COHORT_RULES,
    PLAN_RULES,
    PROVENANCE_RULES,
    SPLIT_RULES,
    _public_message,
    get_rule,
)
from neurocvguard.schema import validate_document
from neurocvguard.serialization import JSONObject, JSONValue, _json_value

_ROLES = {
    "observation_id",
    "subject_id",
    "target",
    "session",
    "site",
    "phase",
    "independence",
    "categorical_covariates",
}
_LIMITATIONS = (
    "Upstream preprocessing is not verified; a valid record does not establish fold-local fitting.",
    "Public projection omits free-text and open evidence; "
    "review the sensitive local record for details.",
    "Aggregate counts and target class names can still be sensitive; "
    "this is not formal anonymization.",
)
_SENSITIVE = "Sensitive research output: do not publish without review."
_GROUPS = ("COHORT", "SPLIT", "PLAN", "ASSOC", "PROV", "EVAL", "REPORT")


def _options(sensitive: bool, threshold: int) -> None:
    if type(sensitive) is not bool or type(threshold) is not int or threshold < 2:
        raise InputValidationError(
            "sensitive_details must be boolean; small_cell_threshold must be an integer >= 2."
        )


def _version(value: str) -> str:
    return (
        value
        if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:(?:a|b|rc|\.post|\.dev)[0-9]+)?", value)
        else "withheld"
    )


def project_check(check: CheckResult) -> JSONObject:
    messages = {
        CheckStatus.PASS: "No violation detected by this check in the supplied information.",
        CheckStatus.FAIL: "This check identified a scoped violation in the supplied information.",
        CheckStatus.NOT_ASSESSABLE: "This check was not assessable from the supplied information.",
        CheckStatus.NOT_APPLICABLE: "This check does not apply to the stated assessment.",
    }
    message = messages[check.status]
    if check.rule_id == "NCG-PROV-001":
        message = "Upstream preprocessing remains unassessable."
    if check.rule_id == "NCG-SPLIT-002" and check.status == CheckStatus.PASS:
        message = "No participant overlap detected in this supplied split."
    cohort_rule = check.rule_id in {rule.id for rule in COHORT_RULES}
    if cohort_rule:
        message = _public_message(check.rule_id, check.status)
    split_rule = check.rule_id in {rule.id for rule in (*SPLIT_RULES, *PLAN_RULES)}
    if split_rule and check.status in (CheckStatus.PASS, CheckStatus.FAIL):
        definition = get_rule(check.rule_id)
        message = (
            definition.trigger_message
            if check.status == CheckStatus.FAIL
            else definition.clear_message
        )
    if check.rule_id == "NCG-SPLIT-004" and check.status == CheckStatus.NOT_APPLICABLE:
        message = (
            "Domain separation is not required by this scoped objective; shared "
            "sites are not leakage."
        )
    safe_evidence: JSONObject = {}
    provenance_rule = check.rule_id in {rule.id for rule in PROVENANCE_RULES}
    if provenance_rule:
        definition = get_rule(check.rule_id)
        message = (
            definition.clear_message
            if check.status in {CheckStatus.PASS, CheckStatus.NOT_APPLICABLE}
            else "The declared fitting boundary is unassessable from the supplied context."
            if check.rule_id == "NCG-PROV-003" and check.status == CheckStatus.NOT_ASSESSABLE
            else definition.trigger_message
        )
        # No imported notes, transform names, event IDs or memberships are public.
        safe_evidence = {"execution_verified": False}
    association_rule = check.rule_id in {rule.id for rule in ASSOCIATION_RULES}
    if association_rule:
        definition = get_rule(check.rule_id)
        message = (
            definition.clear_message
            if check.status == CheckStatus.PASS
            else definition.trigger_message
        )
        # Individual checks remain conservative; whole reports may add a validated
        # display table after applying their explicit small-cell threshold.
        safe_evidence = {"details_omitted": True}
        if check.rule_id == "NCG-ASSOC-003" and check.status == CheckStatus.NOT_ASSESSABLE:
            statistic = check.evidence.get("statistic")
            reason = statistic.get("reason") if isinstance(statistic, Mapping) else None
            if isinstance(reason, str) and reason in {
                "unstable_within_participant",
                "invalid_values",
                "missing_field",
                "missing_target",
                "no_complete_pairs",
                "too_many_categories",
                "constant_variable",
            }:
                safe_evidence["statistic"] = {"value": None, "reason": reason}
    if check.rule_id == "NCG-SPLIT-011":
        message = (
            "Complete-CV coverage and objective validity are separate; "
            "holdouts and multiple repeats are outside ordinary single-repeat evaluation."
        )
        for key in (
            "complete_cv",
            "valid_for_objective",
            "evaluation_permitted",
            "diagnostic_requested",
        ):
            value = check.evidence.get(key)
            if type(value) is bool:
                safe_evidence[key] = value
        for key in ("n_repeats", "n_outer_folds"):
            value = check.evidence.get(key)
            if type(value) is int and value >= 0:
                safe_evidence[key] = value
    return {
        "instance_id": "check-001",
        "rule_id": check.rule_id,
        "status": check.status.value,
        "severity": check.severity.value,
        "evidence_kind": check.evidence_kind.value,
        "scope": {},
        "message": message,
        "recommendation": get_rule(check.rule_id).recommendation
        if cohort_rule or split_rule or association_rule or provenance_rule
        else "Review this rule's required inputs and the sensitive local evidence "
        "before drawing conclusions.",
        "evidence": safe_evidence,
    }


def _checks(
    checks: tuple[CheckResult, ...], sensitive: bool, threshold: int = 5
) -> list[JSONValue]:
    def key(check: CheckResult) -> tuple[int, str, str, str, str]:
        group = check.rule_id.split("-")[1]
        return (
            _GROUPS.index(group) if group in _GROUPS else len(_GROUPS),
            check.rule_id,
            str(check.scope.get("fold_id", "")),
            str(check.scope.get("field", "")),
            check.instance_id,
        )

    ordered = sorted(checks, key=key)
    aliases = {
        role: {
            value: f"{label} {index + 1:02d}"
            for index, value in enumerate(
                sorted(
                    {
                        str(check.scope[role])
                        for check in ordered
                        if check.scope.get(role) is not None
                    }
                )
            )
        }
        for role, label in (
            ("repeat_id", "Repeat"),
            ("fold_id", "Fold"),
            ("inner_fold_id", "Inner fold"),
        )
    }
    domain_values: dict[str, set[str]] = {"Site": set(), "Phase": set(), "Category": set()}
    for check in ordered:
        if check.rule_id.startswith("NCG-ASSOC-"):
            raw = check.evidence.get("display_table", check.evidence)
            if isinstance(raw, Mapping):
                levels = raw.get("row_levels", ())
                label = (
                    "Site"
                    if check.scope.get("field") == "site"
                    else ("Phase" if check.scope.get("field") == "phase" else "Category")
                )
                if isinstance(levels, (tuple, list)):
                    domain_values[label].update(level for level in levels if isinstance(level, str))
    domain_aliases = {
        label: {
            value: f"{label} {i + 1:0{max(3, len(str(len(values))))}d}"
            for i, value in enumerate(sorted(values))
        }
        for label, values in domain_values.items()
    }
    output: list[JSONValue] = []
    for index, check in enumerate(ordered):
        item = check._as_dict() if sensitive else project_check(check)
        if not sensitive:
            item["instance_id"] = f"check-{index + 1:03d}"
            scope: JSONObject = {}
            for role, mapping in aliases.items():
                if check.scope.get(role) is not None:
                    scope[role] = mapping[str(check.scope[role])]
            for role in ("role", "field", "component"):
                if check.scope.get(role) in _ROLES:
                    scope[role] = check.scope[role]
            if str(check.scope.get("field", "")).startswith("categorical_covariates:"):
                scope["field"] = "categorical_covariates"
            item["scope"] = scope
            display = association_display(check, threshold, domain_aliases)
            if display is not None:
                cast(JSONObject, item["evidence"])["display_table"] = display
        output.append(item)
    if not sensitive:
        # Suppressed tables must not leave gaps or alter aliases on public rerender.
        tables = [
            cast(JSONObject, cast(JSONObject, item)["evidence"])["display_table"]
            for item in output
            if "display_table" in cast(JSONObject, cast(JSONObject, item)["evidence"])
        ]
        for label in domain_values:
            visible = sorted(
                {
                    str(value)
                    for table in tables
                    for value in cast(list[JSONValue], cast(JSONObject, table)["row_levels"])
                    if str(value).startswith(label + " ")
                }
            )
            compact = {
                value: f"{label} {i + 1:0{max(3, len(str(len(visible))))}d}"
                for i, value in enumerate(visible)
            }
            for table in tables:
                item_table = cast(JSONObject, table)
                item_table["row_levels"] = [
                    compact.get(str(value), value)
                    for value in cast(list[JSONValue], item_table["row_levels"])
                ]
    return output


def _small(metrics: MetricSet | None, threshold: int) -> bool:
    return metrics is not None and any(
        0 < cell < threshold for row in metrics.confusion_matrix for cell in row
    )


def _public_class_label(label: str, index: int) -> str:
    # Keep ordinary semantic class names; paths, email-like text and controls
    # are unsuitable public labels even if supplied in a target-label field.
    if any(char in label for char in ("/", "\\", "@")) or any(ord(char) < 32 for char in label):
        return f"Target {index + 1:03d}"
    return label


def _metrics(metrics: MetricSet | None, sensitive: bool) -> JSONValue:
    if metrics is None:
        return None
    data = metrics.to_dict()
    if not sensitive:
        for index, row in enumerate(cast(list[JSONObject], data["per_class"])):
            row["class_label"] = _public_class_label(str(row["class_label"]), index)
        # Open reason strings can contain research-row text. Keep a stable generic
        # reason in the public view; operational metrics retain the exact reason.
        for name in ("accuracy", "balanced_accuracy", "macro_f1", "roc_auc"):
            item = cast(JSONObject, data[name])
            if item["reason"] is not None:
                item["reason"] = "undefined_metric"
    return data


def _evaluation_summary(
    summary: Mapping[str, object], sensitive: bool, threshold: int
) -> JSONObject:
    data = cast(JSONObject, _json_value(summary))
    pooled = None if data["pooled_metrics"] is None else MetricSet.from_dict(data["pooled_metrics"])
    folds = cast(list[JSONObject], data.get("fold_metrics", []))
    fold_sets = [
        None if fold["metrics"] is None else MetricSet.from_dict(fold["metrics"]) for fold in folds
    ]
    # Hide the linked family to prevent reconstructing a hidden fold by
    # subtracting visible folds from a visible pooled confusion matrix.
    hide = not sensitive and (
        _small(pooled, threshold)
        or any(_small(metrics, threshold) for metrics in fold_sets)
        or data.get("metrics_hidden_reason") == "privacy_small_cells"
        or any(fold.get("metrics_hidden_reason") == "privacy_small_cells" for fold in folds)
    )
    if not sensitive:
        data["class_order"] = [
            _public_class_label(str(label), index)
            for index, label in enumerate(cast(list[JSONValue], data["class_order"]))
        ]
    data["pooled_metrics"] = None if hide else _metrics(pooled, sensitive)
    data["metrics_hidden_reason"] = "privacy_small_cells" if hide else None
    aliases = {
        role: {
            value: f"{index:03d}"
            for index, value in enumerate(sorted({str(fold[role]) for fold in folds}))
        }
        for role in ("repeat_id", "fold_id")
    }
    for fold, metrics in zip(folds, fold_sets, strict=True):
        fold["metrics"] = None if hide else _metrics(metrics, sensitive)
        fold["metrics_hidden_reason"] = "privacy_small_cells" if hide else None
        if not sensitive:
            for role, mapping in aliases.items():
                fold[role] = mapping[str(fold[role])]
    if "fold_metrics" in data:
        data["fold_metrics"] = cast(list[JSONValue], folds)
    return data


def project_evaluation(result: EvaluationResult, sensitive: bool, threshold: int) -> JSONObject:
    _options(sensitive, threshold)
    summary: JSONObject = {
        "diagnostic_only": result.diagnostic_only,
        "metric_unit": result.metric_unit,
        "class_order": list(result.class_order),
        "n_participants": result.n_participants,
        "execution_status": result.execution_status.value,
        "pooled_metrics": _metrics(result.pooled_metrics, True),
        "fold_metrics": [
            {
                "repeat_id": fold.repeat_id,
                "fold_id": fold.fold_id,
                "status": fold.status.value,
                "metrics": _metrics(fold.metrics, True),
                "metrics_hidden_reason": None,
            }
            for fold in result.folds
        ],
    }
    data: JSONObject = {
        "schema_version": result.schema_version,
        "tool_version": result.tool_version if sensitive else _version(result.tool_version),
        "result_type": "evaluation",
        "objective": result.objective.value,
        "execution_status": {
            "completed": "completed",
            "incomplete": "partial",
            "blocked": "blocked",
        }[result.execution_status.value],
        "input_summary": {
            "n_observations": result.n_observations,
            "n_participants": result.n_participants,
            "supplied_roles": [],
            "missing_roles": [],
        },
        "checks": _checks(result.preflight_checks, sensitive, threshold),
        "limitations": _json_value(
            list(result.limitations) + [_SENSITIVE] if sensitive else list(_LIMITATIONS)
        ),
        "provenance": {
            "foundation_version": "1.0.0",
            "versions": {"neurocvguard": __version__},
            "sensitive_details": sensitive,
            "upstream_preprocessing_verified": False,
        },
        "evaluation_summary": _evaluation_summary(summary, sensitive, threshold),
    }
    return validate_document("audit-report", data)


def project_comparison(result: ComparisonResult, sensitive: bool, threshold: int) -> JSONObject:
    _options(sensitive, threshold)
    if sensitive:
        return result._as_dict()
    aliases = {
        name: f"Design {index + 1:02d}"
        for index, name in enumerate(sorted(design.name for design in result.designs))
    }
    hidden = {design.name for design in result.designs if _small(design.metrics, threshold)}
    designs: list[JSONValue] = [
        {
            "name": aliases[design.name],
            "objective": design.objective.value,
            "diagnostic_only": design.diagnostic_only,
            "metrics": None if design.name in hidden else _metrics(design.metrics, False),
        }
        for design in result.designs
    ]
    differences: list[JSONValue] = []
    for difference in result.differences:
        hide = difference.design_a in hidden or difference.design_b in hidden
        differences.append(
            {
                "design_a": aliases[difference.design_a],
                "design_b": aliases[difference.design_b],
                "metric": difference.metric,
                "difference": None if hide else difference.difference,
                "reasons": ["privacy_small_cells"]
                if hide
                else (["metric_unavailable"] if difference.difference is None else []),
            }
        )
    return validate_document(
        "comparison-summary",
        {
            "designs": designs,
            "differences": differences,
            "interpretation": "Design differences are descriptive, not causal estimates "
            "of leakage. Small-cell metrics are withheld when applicable.",
        },
    )


def project_report(report: AuditReport, sensitive: bool, threshold: int) -> JSONObject:
    _options(sensitive, threshold)
    data = report._as_dict()
    data["checks"] = _checks(report.checks, sensitive, threshold)
    provenance = cast(JSONObject, data["provenance"])
    provenance["sensitive_details"] = sensitive
    if sensitive:
        data["limitations"] = _json_value(
            list(report.limitations) + ([] if _SENSITIVE in report.limitations else [_SENSITIVE])
        )
    else:
        data["tool_version"] = _version(report.tool_version)
        data["limitations"] = _json_value(list(_LIMITATIONS))
        data["provenance"] = {
            "foundation_version": _version(str(provenance["foundation_version"])),
            "versions": {"neurocvguard": __version__},
            "sensitive_details": False,
            "upstream_preprocessing_verified": False,
        }
        summary = cast(JSONObject, data["input_summary"])
        for role in ("supplied_roles", "missing_roles"):
            summary[role] = [value for value in cast(list[str], summary[role]) if value in _ROLES]
    if report.evaluation_summary is not None:
        data["evaluation_summary"] = _evaluation_summary(
            report.evaluation_summary, sensitive, threshold
        )
    if report.comparison_summary is not None:
        data["comparison_summary"] = project_comparison(
            report.comparison_summary, sensitive, threshold
        )
    return validate_document("audit-report", data)
