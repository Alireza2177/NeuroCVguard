"""Typed contract records; constructing a record does not execute a research analysis."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, cast

import pandas as pd

from neurocvguard._records import Record
from neurocvguard.config import AuditConfig as AuditConfig
from neurocvguard.config import ColumnMap as ColumnMap
from neurocvguard.config import Objective
from neurocvguard.errors import EvaluationError, InputValidationError, SplitValidationError
from neurocvguard.serialization import FrozenJSONValue, JSONObject, json_digest


class CheckStatus(StrEnum):
    """Outcome for one scoped check, never a global validity verdict."""

    PASS = "pass"
    FAIL = "fail"
    NOT_ASSESSABLE = "not_assessable"
    NOT_APPLICABLE = "not_applicable"


class Severity(StrEnum):
    """Finding severity, separate from technical execution status."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class EvidenceKind(StrEnum):
    """Observed, declared, heuristic, or unassessable evidence."""

    OBSERVED = "observed"
    DECLARED = "declared"
    HEURISTIC = "heuristic"
    UNASSESSABLE = "unassessable"


class ReportStatus(StrEnum):
    """Technical assessment coverage; completed does not mean scientifically valid."""

    COMPLETED = "completed"
    PARTIAL = "partial"
    BLOCKED = "blocked"


class EvaluationStatus(StrEnum):
    """Technical evaluation completion with failed folds retained."""

    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    BLOCKED = "blocked"


class FoldStatus(StrEnum):
    """A fold/fit either completed or failed; failure is not omitted."""

    COMPLETED = "completed"
    FAILED = "failed"


class PlanOrigin(StrEnum):
    """Imported assignments differ from internally generated plans."""

    IMPORTED = "imported"
    GENERATED = "generated"


@dataclass(frozen=True)
class PlainRecord(Record):
    """Component record with a detached schema-shaped dictionary view."""

    def to_dict(self) -> JSONObject:
        """Return a fresh JSON dictionary of this component's declared fields.

        Returns
        -------
        JSONObject
            Detached component data. Identity-bearing components remain sensitive.

        Examples
        --------
        >>> MetricValue(None, "positive_class_unspecified", 10).to_dict()["value"] is None
        True
        """
        return self._as_dict()


_METRICS = ("properties", "pooled_metrics", "anyOf", 0)


@dataclass(frozen=True)
class MetricValue(PlainRecord):
    """Metric value, null reason and denominator n; zero is a real score."""

    _schema_name: ClassVar[str] = "evaluation-result"
    _schema_path: ClassVar[tuple[str | int, ...]] = (*_METRICS, "properties", "accuracy")
    value: float | None
    reason: str | None
    n: int

    def _validate_semantics(self) -> None:
        if self.value is None and (self.reason is None or not self.reason.strip()):
            raise InputValidationError("Undefined metric requires a non-empty reason.")


@dataclass(frozen=True)
class ClassMetric(PlainRecord):
    """One class in the global class order, its support, and descriptive recall."""

    _schema_name: ClassVar[str] = "evaluation-result"
    _schema_path: ClassVar[tuple[str | int, ...]] = (*_METRICS, "properties", "per_class", "items")
    class_label: str
    support: int
    recall: float | None


@dataclass(frozen=True)
class MetricSet(PlainRecord):
    """Participant metrics and a square confusion table in per_class order."""

    _schema_name: ClassVar[str] = "evaluation-result"
    _schema_path: ClassVar[tuple[str | int, ...]] = _METRICS
    accuracy: MetricValue
    balanced_accuracy: MetricValue
    macro_f1: MetricValue
    roc_auc: MetricValue
    n_participants: int
    per_class: tuple[ClassMetric, ...]
    confusion_matrix: tuple[tuple[int, ...], ...]

    def _validate_semantics(self) -> None:
        n_classes = len(self.per_class)
        if len({item.class_label for item in self.per_class}) != n_classes:
            raise InputValidationError("Metric per_class labels must be unique.")
        if len(self.confusion_matrix) != n_classes or any(
            len(row) != n_classes for row in self.confusion_matrix
        ):
            raise InputValidationError("Confusion matrix size must match per_class order.")
        if any(
            sum(row) != item.support
            for row, item in zip(self.confusion_matrix, self.per_class, strict=True)
        ):
            raise InputValidationError("Confusion matrix row support does not match per_class.")
        if sum(item.support for item in self.per_class) != self.n_participants:
            raise InputValidationError("Metric support does not match n_participants.")
        for metric in (self.accuracy, self.balanced_accuracy, self.macro_f1, self.roc_auc):
            if metric.n > self.n_participants:
                raise InputValidationError("Metric denominator exceeds participant coverage.")


@dataclass(frozen=True)
class CheckResult(Record):
    """Scoped evidence. Free text and open evidence are sensitive until projected."""

    _schema_name: ClassVar[str] = "audit-report"
    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "checks", "items")
    instance_id: str
    rule_id: str
    status: CheckStatus
    severity: Severity
    evidence_kind: EvidenceKind
    scope: Mapping[str, str | int | None]
    message: str
    recommendation: str
    evidence: Mapping[str, FrozenJSONValue]

    def _validate_semantics(self) -> None:
        if (
            self.status == CheckStatus.NOT_ASSESSABLE
            and self.evidence_kind != EvidenceKind.UNASSESSABLE
        ):
            raise InputValidationError("not_assessable status requires unassessable evidence.")
        if self.evidence_kind == EvidenceKind.UNASSESSABLE and self.status in (
            CheckStatus.PASS,
            CheckStatus.FAIL,
        ):
            raise InputValidationError("Unassessable evidence cannot establish a pass or fail.")
        if (
            self.rule_id in {"NCG-PROV-002", "NCG-PROV-003", "NCG-PROV-005"}
            and self.evidence_kind != EvidenceKind.DECLARED
        ):
            raise InputValidationError(
                "Imported preprocessing declarations must remain declared evidence."
            )
        if self.rule_id == "NCG-PROV-001" and self.evidence_kind != EvidenceKind.UNASSESSABLE:
            raise InputValidationError("Unknown upstream preprocessing remains unassessable.")

    def to_dict(self, sensitive_details: bool = False) -> JSONObject:
        """Project a check; free text/open evidence require explicit sensitive access.

        Parameters
        ----------
        sensitive_details : bool, optional
            Include the original message, scope and evidence only when True.

        Returns
        -------
        JSONObject
            Schema-shaped detached data; safe structural wording by default.

        Examples
        --------
        Use ``check.to_dict(sensitive_details=True)`` only for local review.
        """
        from neurocvguard._projection import project_check

        if type(sensitive_details) is not bool:
            raise InputValidationError("sensitive_details must be an explicit boolean.")
        return self._as_dict() if sensitive_details else project_check(self)


@dataclass(frozen=True)
class InnerFold(Record):
    """Sensitive observation memberships in one inner training/validation partition."""

    _schema_name: ClassVar[str] = "split-plan"
    _schema_path: ClassVar[tuple[str | int, ...]] = (
        "properties",
        "folds",
        "items",
        "properties",
        "inner_folds",
        "items",
    )
    inner_fold_id: str
    train_ids: tuple[str, ...]
    validation_ids: tuple[str, ...]

    def _validate_semantics(self) -> None:
        object.__setattr__(self, "train_ids", tuple(sorted(self.train_ids)))
        object.__setattr__(self, "validation_ids", tuple(sorted(self.validation_ids)))


@dataclass(frozen=True)
class SplitFold(Record):
    """Sensitive outer memberships. Cross-cohort membership auditing is separate."""

    _schema_name: ClassVar[str] = "split-plan"
    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "folds", "items")
    _omit_none: ClassVar[tuple[str, ...]] = ("inner_folds",)
    repeat_id: str
    fold_id: str
    train_ids: tuple[str, ...]
    test_ids: tuple[str, ...]
    inner_folds: tuple[InnerFold, ...] | None = None

    def _validate_semantics(self) -> None:
        object.__setattr__(self, "train_ids", tuple(sorted(self.train_ids)))
        object.__setattr__(self, "test_ids", tuple(sorted(self.test_ids)))
        ids = [item.inner_fold_id for item in self.inner_folds or ()]
        if len(ids) != len(set(ids)):
            raise SplitValidationError(
                "Inner fold identifiers must be unique within an outer fold."
            )


@dataclass(frozen=True)
class SplitPlan(Record):
    """Sensitive operational split contract; loading does not certify its design."""

    _schema_name: ClassVar[str] = "split-plan"
    _error_type = SplitValidationError
    schema_version: str
    plan_id: str
    origin: PlanOrigin
    cohort_digest: str | None
    objective: Objective
    scheme: str
    seed: int | None
    folds: tuple[SplitFold, ...]
    # Runtime audit/provenance is separate from the strict operational plan schema.
    # Reconstructing/replacing a plan does not authenticate or copy generation evidence.
    generation_report: "AuditReport | None" = field(
        default=None, init=False, repr=False, compare=False, metadata={"serialize": False}
    )

    def _validate_semantics(self) -> None:
        pairs = [(fold.repeat_id, fold.fold_id) for fold in self.folds]
        if len(pairs) != len(set(pairs)):
            raise SplitValidationError("repeat_id/fold_id pairs must be unique.")
        if self.origin == PlanOrigin.GENERATED:
            payload = self._as_dict()
            del payload["plan_id"]
            if self.plan_id != json_digest(payload):
                raise SplitValidationError(
                    "Generated plan_id must be SHA-256 of the canonical plan fields "
                    "excluding plan_id."
                )

    def to_operational_dict(self) -> JSONObject:
        """Return sensitive identity-bearing assignments, never a public report.

        Returns
        -------
        JSONObject
            Exact schema fields, with canonical sorted membership IDs.

        Examples
        --------
        ``SplitPlan.from_dict(plan.to_operational_dict())`` preserves the plan.
        """
        return self._as_dict()

    def write(self, output_dir: str | Path, *, overwrite: bool = False) -> dict[str, Path]:
        """Write sensitive canonical JSON and outer assignment TSV to a local directory.

        Parameters
        ----------
        output_dir : str or Path
            Explicit local destination; unrelated files are preserved.
        overwrite : bool, optional
            Explicitly allow replacement of this writer's existing artifacts.

        Returns
        -------
        dict of str to Path
            plan, assignments, notice and, when captured, generation_report paths.

        Raises
        ------
        InputValidationError
            Conflicting outputs, invalid identities, unsafe destination or I/O failure.

        Examples
        --------
        ``paths = plan.write("local-splits")`` writes identity-bearing private files.

        Notes
        -----
        Writing a supplied plan does not certify its design. Runtime generation_report
        is saved separately when available; loading plan.json cannot recreate that history.
        """
        from neurocvguard.io import write_split_plan

        return write_split_plan(self, output_dir=output_dir, overwrite=overwrite)


@dataclass(frozen=True)
class CandidateScore(PlainRecord):
    """A recorded candidate C and inner score; no selection is performed here."""

    _schema_name: ClassVar[str] = "evaluation-result"
    _schema_path: ClassVar[tuple[str | int, ...]] = (
        "properties",
        "folds",
        "items",
        "properties",
        "candidate_scores",
        "items",
    )
    C: float
    balanced_accuracy: float | None
    reason: str | None

    def _validate_semantics(self) -> None:
        if self.balanced_accuracy is None and (self.reason is None or not self.reason.strip()):
            raise EvaluationError("Undefined candidate score requires a reason.")
        if self.balanced_accuracy is not None and self.reason is not None:
            raise EvaluationError("Defined candidate score must have a null reason.")


@dataclass(frozen=True)
class EvaluationFold(Record):
    """One retained completed/failed fold, including candidate selection evidence."""

    _schema_name: ClassVar[str] = "evaluation-result"
    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "folds", "items")
    repeat_id: str
    fold_id: str
    status: FoldStatus
    reason: str | None
    train_participants: int
    test_participants: int
    selected_C: float | None
    metrics: MetricSet | None
    candidate_scores: tuple[CandidateScore, ...]

    def _validate_semantics(self) -> None:
        if self.status == FoldStatus.FAILED:
            if not self.reason or not self.reason.strip() or self.metrics is not None:
                raise EvaluationError("Failed fold requires a reason and null metrics.")
        elif self.reason is not None or self.metrics is None:
            raise EvaluationError("Completed fold requires metrics and a null failure reason.")
        if self.selected_C is not None and self.selected_C <= 0:
            raise EvaluationError("selected_C must be positive or null.")
        if self.metrics is not None and self.metrics.n_participants != self.test_participants:
            raise EvaluationError("Fold metric coverage must equal test_participants.")


@dataclass(frozen=True)
class FitEvent(Record):
    """Sensitive recorded fit IDs. Parsing cannot authenticate external fit history."""

    _schema_name: ClassVar[str] = "evaluation-result"
    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "fit_events", "items")
    event_id: str
    repeat_id: str
    fold_id: str
    inner_fold_id: str | None
    C: float
    fit_ids: tuple[str, ...]
    status: FoldStatus
    scope: str

    def _validate_semantics(self) -> None:
        if (self.scope == "inner_train") != (self.inner_fold_id is not None):
            raise EvaluationError("Fit scope must match presence of inner_fold_id.")


@dataclass(frozen=True)
class EvaluationResult(Record):
    """Sensitive operational evaluation record; no estimator fitting occurs here."""

    _schema_name: ClassVar[str] = "evaluation-result"
    _error_type = EvaluationError
    _omit_none: ClassVar[tuple[str, ...]] = ("plan_digest", "actual_plan")
    format: str
    schema_version: str
    tool_version: str
    sensitive: bool
    execution_status: EvaluationStatus
    objective: Objective
    diagnostic_only: bool
    cohort_digest: str
    feature_digest: str
    config_digest: str
    class_order: tuple[str, ...]
    positive_class: str | None
    feature_columns: tuple[str, ...]
    metric_unit: str
    n_observations: int
    n_participants: int
    folds: tuple[EvaluationFold, ...]
    fit_events: tuple[FitEvent, ...]
    pooled_metrics: MetricSet | None
    preflight_checks: tuple[CheckResult, ...]
    limitations: tuple[str, ...]
    provenance: Mapping[str, FrozenJSONValue]
    plan_digest: str | None = None
    actual_plan: SplitPlan | None = None

    def _validate_semantics(self) -> None:
        if (self.plan_digest is None) != (self.actual_plan is None):
            raise EvaluationError("plan_digest and actual_plan must be provided together.")
        if self.actual_plan is not None:
            plan = self.actual_plan
            if self.plan_digest != json_digest(plan.to_operational_dict()):
                raise EvaluationError("plan_digest does not match actual_plan.")
            if plan.cohort_digest != self.cohort_digest or plan.objective != self.objective:
                raise EvaluationError("Retained plan must match the cohort digest and objective.")
            memberships = {(fold.repeat_id, fold.fold_id): fold for fold in plan.folds}
            if set(memberships) != {(fold.repeat_id, fold.fold_id) for fold in self.folds}:
                raise EvaluationError("Evaluation folds must match the retained plan.")
            for event in self.fit_events:
                outer = memberships.get((event.repeat_id, event.fold_id))
                if outer is None:
                    raise EvaluationError("Fit event references an unknown retained fold.")
                allowed = outer.train_ids
                if event.inner_fold_id is not None:
                    inner = next(
                        (
                            fold
                            for fold in outer.inner_folds or ()
                            if fold.inner_fold_id == event.inner_fold_id
                        ),
                        None,
                    )
                    if inner is None:
                        raise EvaluationError(
                            "Fit event references an unknown retained inner fold."
                        )
                    allowed = inner.train_ids
                if not set(event.fit_ids) <= set(allowed):
                    raise EvaluationError("Fit event escapes its retained training boundary.")
        if self.positive_class is not None and self.positive_class not in self.class_order:
            raise EvaluationError("positive_class must belong to class_order.")
        pairs = [(fold.repeat_id, fold.fold_id) for fold in self.folds]
        if len(pairs) != len(set(pairs)):
            raise EvaluationError("Evaluation fold identifiers must be unique.")
        if self.execution_status != EvaluationStatus.COMPLETED and self.pooled_metrics is not None:
            raise EvaluationError("Incomplete or blocked evaluation cannot report pooled metrics.")
        if self.execution_status == EvaluationStatus.COMPLETED:
            if (
                len(self.folds) < 2
                or any(f.status != FoldStatus.COMPLETED for f in self.folds)
                or self.pooled_metrics is None
            ):
                raise EvaluationError(
                    "Completed evaluation requires completed folds and pooled metrics."
                )
            if len({fold.repeat_id for fold in self.folds}) != 1:
                raise EvaluationError("Completed v0.1 evaluation requires exactly one repeat.")
        for metrics in (*[fold.metrics for fold in self.folds], self.pooled_metrics):
            if (
                metrics is not None
                and tuple(item.class_label for item in metrics.per_class) != self.class_order
            ):
                raise EvaluationError("Metric class order must match global class_order.")
        if (
            self.pooled_metrics is not None
            and self.pooled_metrics.n_participants != self.n_participants
        ):
            raise EvaluationError("Pooled metric coverage must match n_participants.")

    def to_operational_dict(self) -> JSONObject:
        """Return the explicitly marked sensitive evaluation.private contract.

        Returns
        -------
        JSONObject
            Detached complete record, including fit IDs and integrity digests.

        Examples
        --------
        ``EvaluationResult.from_dict(result.to_operational_dict())`` round-trips locally.
        """
        return self._as_dict()

    def to_dict(
        self, sensitive_details: bool = False, *, small_cell_threshold: int = 5
    ) -> JSONObject:
        """Return an AuditReport envelope with a privacy-projected evaluation summary.

        Parameters
        ----------
        sensitive_details : bool, optional
            Explicitly retain sensitive report details. Operational IDs still use
            the separate operational serializer.
        small_cell_threshold : int, optional
            Hide a whole MetricSet when any positive confusion cell is below this value.

        Returns
        -------
        JSONObject
            Valid report envelope, not an operational record for comparison.

        Raises
        ------
        InputValidationError
            The privacy options are invalid.

        Examples
        --------
        ``result.to_dict()`` omits digests and fit_ids and retains failed-fold status.
        """
        from neurocvguard._projection import project_evaluation

        return project_evaluation(self, sensitive_details, small_cell_threshold)


@dataclass(frozen=True)
class ComparisonContext(PlainRecord):
    """Optional recorded design context; digest equivalence uses local aliases."""

    _schema_name: ClassVar[str] = "comparison-summary"
    _schema_path: ClassVar[tuple[str | int, ...]] = (
        "properties",
        "designs",
        "items",
        "properties",
        "context",
    )
    execution_status: EvaluationStatus
    metric_unit: str
    cohort_reference: str
    feature_reference: str
    n_folds: int
    n_completed_folds: int
    n_participants: int
    n_observations: int
    n_features: int
    training_participants_min: int
    training_participants_max: int
    class_order: tuple[str, ...]
    positive_class: str | None
    model: str
    recorded_C_values: tuple[float, ...]
    tuning_recorded: bool

    def _validate_semantics(self) -> None:
        if self.n_completed_folds > self.n_folds or not (
            self.training_participants_min <= self.training_participants_max <= self.n_participants
        ):
            raise InputValidationError("Comparison context counts are inconsistent.")
        if self.positive_class is not None and self.positive_class not in self.class_order:
            raise InputValidationError("Comparison positive class must belong to class_order.")


@dataclass(frozen=True)
class ComparisonDesign(PlainRecord):
    """Named design, objective and supplied metrics; no comparison is computed."""

    _schema_name: ClassVar[str] = "comparison-summary"
    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "designs", "items")
    _omit_none: ClassVar[tuple[str, ...]] = ("context",)
    name: str
    objective: Objective
    diagnostic_only: bool
    metrics: MetricSet | None
    context: ComparisonContext | None = None

    def _validate_semantics(self) -> None:
        if self.context is not None and self.metrics is not None:
            if (
                self.metrics.n_participants != self.context.n_participants
                or tuple(c.class_label for c in self.metrics.per_class) != self.context.class_order
            ):
                raise InputValidationError("Comparison metrics must match their design context.")


@dataclass(frozen=True)
class MetricDifference(PlainRecord):
    """Descriptive design A minus B; undefined differences carry reasons."""

    _schema_name: ClassVar[str] = "comparison-summary"
    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "differences", "items")
    design_a: str
    design_b: str
    metric: str
    difference: float | None
    reasons: tuple[str, ...]

    def _validate_semantics(self) -> None:
        if self.difference is None and (
            not self.reasons or any(not reason.strip() for reason in self.reasons)
        ):
            raise InputValidationError("Undefined design difference requires non-empty reasons.")


@dataclass(frozen=True)
class ComparisonResult(Record):
    """Schema-shaped comparison summary; differences are descriptive, not causal."""

    _schema_name: ClassVar[str] = "comparison-summary"
    designs: tuple[ComparisonDesign, ...]
    differences: tuple[MetricDifference, ...]
    interpretation: str

    def _validate_semantics(self) -> None:
        names = [design.name for design in self.designs]
        if len(names) != len(set(names)):
            raise InputValidationError("Comparison design names must be unique.")
        if any(d.design_a not in names or d.design_b not in names for d in self.differences):
            raise InputValidationError("Difference references an unknown design.")

    def to_dict(
        self, sensitive_details: bool = False, *, small_cell_threshold: int = 5
    ) -> JSONObject:
        """Project names, metrics and differences; suppress reconstruction of small cells.

        Parameters
        ----------
        sensitive_details : bool, optional
            Preserve supplied labels/free text only for explicitly sensitive local use.
        small_cell_threshold : int, optional
            Positive confusion-cell suppression threshold, at least two.

        Returns
        -------
        JSONObject
            comparison-summary schema data. Sensitive output is not anonymous.

        Examples
        --------
        ``ComparisonResult.from_dict(result.to_dict(sensitive_details=True))`` round-trips.
        """
        from neurocvguard._projection import project_comparison

        return project_comparison(self, sensitive_details, small_cell_threshold)


@dataclass(frozen=True)
class AuditReport(Record):
    """Report envelope and structured coverage. Technical completion is not validity."""

    _schema_name: ClassVar[str] = "audit-report"
    _omit_none: ClassVar[tuple[str, ...]] = ("evaluation_summary", "comparison_summary")
    schema_version: str
    tool_version: str
    result_type: str
    objective: Objective
    execution_status: ReportStatus
    input_summary: Mapping[str, FrozenJSONValue]
    checks: tuple[CheckResult, ...]
    limitations: tuple[str, ...]
    provenance: Mapping[str, FrozenJSONValue]
    evaluation_summary: Mapping[str, FrozenJSONValue] | None = None
    comparison_summary: ComparisonResult | None = None

    def _validate_semantics(self) -> None:
        if self.result_type != "evaluation" and self.evaluation_summary is not None:
            raise InputValidationError("evaluation_summary requires result_type evaluation.")
        if self.result_type != "comparison" and self.comparison_summary is not None:
            raise InputValidationError("comparison_summary requires result_type comparison.")
        if len({check.instance_id for check in self.checks}) != len(self.checks):
            raise InputValidationError("Check instance identifiers must be unique within a report.")
        if self.execution_status == ReportStatus.COMPLETED and any(
            check.status == CheckStatus.NOT_ASSESSABLE for check in self.checks
        ):
            raise InputValidationError(
                "A report with unassessable requested checks cannot claim completed coverage."
            )
        if self.evaluation_summary is not None:
            summary = self.evaluation_summary
            metrics = [summary["pooled_metrics"]]
            folds = summary.get("fold_metrics", ())
            if isinstance(folds, (list, tuple)):
                metrics.extend(fold["metrics"] for fold in folds if isinstance(fold, Mapping))
            for value in metrics:
                if value is not None:
                    record = MetricSet.from_dict(value)
                    if tuple(item.class_label for item in record.per_class) != cast(
                        tuple[str, ...], summary["class_order"]
                    ):
                        raise InputValidationError(
                            "Public metric class order must match class_order."
                        )

    def to_dict(
        self, sensitive_details: bool = False, *, small_cell_threshold: int = 5
    ) -> JSONObject:
        """Return a detached public or explicitly sensitive report projection.

        Parameters
        ----------
        sensitive_details : bool, optional
            Include raw free text/evidence only when explicitly True.
        small_cell_threshold : int, optional
            Hide small-cell metrics in any supplied evaluation/comparison summary.

        Returns
        -------
        JSONObject
            A schema-validated report with an explicit sensitivity provenance flag.

        Examples
        --------
        ``AuditReport.from_dict(report.to_dict())`` loads the public projection.
        """
        from neurocvguard._projection import project_report

        return project_report(self, sensitive_details, small_cell_threshold)


@dataclass(frozen=True)
class LedgerEvent(Record):
    """Sensitive user-declared preprocessing event; never proof of observed execution."""

    _schema_name: ClassVar[str] = "preprocessing-ledger"
    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "events", "items")
    event_id: str
    transform: str
    data_dependent: bool
    repeat_id: str | None
    fold_id: str | None
    inner_fold_id: str | None
    fit_scope: str
    fit_ids: tuple[str, ...] | None
    uses_target: bool
    note: str


@dataclass(frozen=True)
class PreprocessingLedger(Record):
    """Offline declaration ledger with source fixed to user_declaration."""

    _schema_name: ClassVar[str] = "preprocessing-ledger"
    schema_version: str
    source: str
    events: tuple[LedgerEvent, ...]

    def to_operational_dict(self) -> JSONObject:
        """Return sensitive declarations, retaining the user_declaration source.

        Returns
        -------
        JSONObject
            A detached schema-shaped ledger, not verified fit history.

        Examples
        --------
        ``PreprocessingLedger.from_dict(ledger.to_operational_dict())`` round-trips.
        """
        return self._as_dict()


@dataclass(frozen=True, init=False)
class Cohort:
    """Own copies of validated in-memory tables and explicit canonical row order.

    Parameters
    ----------
    metadata : pandas.DataFrame
        Already validated metadata in observation_order. No ingestion or joining occurs.
    features : pandas.DataFrame or None
        Optional aligned features including the explicit observation-key column.
    columns : ColumnMap
        Explicit roles; not inferred from the tables.
    observation_order : tuple of str
        Unique observation IDs in table order. It may not be based on dataframe index.

    Notes
    -----
    Stored frames and returned copies may contain sensitive data. Pandas deep
    copies do not recursively clone arbitrary objects; validated cells must be
    scalars. No public JSON serializer is supplied for raw cohort tables.
    """

    _metadata: pd.DataFrame = field(repr=False)
    _features: pd.DataFrame | None = field(repr=False)
    columns: ColumnMap
    observation_order: tuple[str, ...] = field(repr=False)

    def __init__(
        self,
        metadata: pd.DataFrame,
        features: pd.DataFrame | None,
        columns: ColumnMap,
        observation_order: tuple[str, ...],
    ) -> None:
        if not isinstance(metadata, pd.DataFrame) or (
            features is not None and not isinstance(features, pd.DataFrame)
        ):
            raise InputValidationError(
                "Cohort requires in-memory DataFrames, not inferred table formats."
            )
        order = tuple(observation_order)
        if any(type(key) is not str or not key for key in order) or len(order) != len(set(order)):
            raise InputValidationError(
                "Cohort observation_order requires unique non-empty string keys."
            )
        for frame in (metadata, features):
            if frame is not None:
                if not frame.columns.is_unique or columns.observation_id not in frame:
                    raise InputValidationError(
                        "Cohort tables require unique columns and the observation key."
                    )
                if tuple(frame[columns.observation_id]) != order:
                    raise InputValidationError(
                        "Cohort tables must already be aligned by explicit observation keys."
                    )
        object.__setattr__(self, "_metadata", metadata.copy(deep=True))
        object.__setattr__(
            self, "_features", None if features is None else features.copy(deep=True)
        )
        object.__setattr__(self, "columns", columns)
        object.__setattr__(self, "observation_order", order)

    @property
    def metadata(self) -> pd.DataFrame:
        """Return a caller-owned metadata copy; it is still sensitive."""
        return self._metadata.copy(deep=True)

    @property
    def features(self) -> pd.DataFrame | None:
        """Return a caller-owned aligned feature copy, or None."""
        return None if self._features is None else self._features.copy(deep=True)
