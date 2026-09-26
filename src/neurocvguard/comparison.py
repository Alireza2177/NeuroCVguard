"""Descriptive comparisons of local private evaluation records; never fits models."""

from itertools import combinations
from pathlib import Path

from neurocvguard.errors import InputValidationError
from neurocvguard.identity import _valid_label
from neurocvguard.models import (
    ComparisonContext,
    ComparisonDesign,
    ComparisonResult,
    EvaluationResult,
    EvaluationStatus,
    MetricDifference,
)
from neurocvguard.serialization import strict_json_loads

INTERPRETATION = (
    "Signed score_difference is design A minus design B in participant metric units (0–1 scale). "
    "Design differences are descriptive, not causal estimates of leakage. Different objectives "
    "can change held-out distributions, training sizes and class coverage even when cohort and "
    "feature identities match. No winning scientific design is selected. Upstream preprocessing "
    "remains unverified. Diagnostic designs have diagnostic_only=true and "
    "valid_for_objective=false. Do not report as evidence for unseen-participant "
    "generalization. For these diagnostic designs, "
    "participant aggregation does not repair training leakage. Context aliases denote recorded "
    "digest equivalence only. Full model settings require the original configuration. "
    "Small-cell metrics and their dependent differences are withheld in public reports."
)
MISMATCH_REASONS = frozenset(
    {
        "cohort_mismatch",
        "cohort_counts_mismatch",
        "feature_mismatch",
        "class_definitions_mismatch",
        "metric_unit_mismatch",
        "design_a_incomplete",
        "design_b_incomplete",
        "metric_undefined_a",
        "metric_undefined_b",
        "privacy_small_cells",
        "metric_unavailable",
    }
)


def load_evaluation(source: str | Path, *, max_input_mb: int = 128) -> EvaluationResult:
    """Read bounded strict local JSON; public projections cannot supply lost identity."""
    path = Path(source)
    if type(max_input_mb) is not int or max_input_mb <= 0:
        raise InputValidationError("max_input_mb must be a positive integer.")
    if (
        "://" in str(source)
        or str(source).startswith(("\\\\", "//"))
        or path.suffix.lower() != ".json"
    ):
        raise InputValidationError("Use a local evaluation.private.json operational record.")
    limit = max_input_mb * 1024 * 1024
    try:
        if not path.is_file() or path.stat().st_size > limit:
            raise InputValidationError("Private evaluation file is missing or exceeds input limit.")
        with path.open("rb") as handle:
            raw = handle.read(limit + 1)
        if len(raw) > limit:
            raise InputValidationError("Private evaluation exceeds input limit.")
        data = strict_json_loads(raw.decode("utf-8-sig"))
    except (OSError, UnicodeError):
        raise InputValidationError("Cannot read a local UTF-8 private evaluation record.") from None
    if not isinstance(data, dict) or data.get("format") != "neurocvguard.evaluation.private":
        raise InputValidationError(
            "Compare requires evaluation.private.json, the operational evaluation record; "
            "a public report omits digests and fit metadata and cannot be reconstructed."
        )
    return EvaluationResult.from_dict(data)


def _context(result: EvaluationResult, cohort: str, features: str) -> ComparisonContext:
    sizes = [fold.train_participants for fold in result.folds]
    return ComparisonContext(
        result.execution_status,
        result.metric_unit,
        cohort,
        features,
        len(result.folds),
        sum(f.status == "completed" for f in result.folds),
        result.n_participants,
        result.n_observations,
        len(result.feature_columns),
        min(sizes, default=0),
        max(sizes, default=0),
        result.class_order,
        result.positive_class,
        "prescribed_logistic_baseline",
        tuple(
            sorted(
                {e.C for e in result.fit_events}
                | {f.selected_C for f in result.folds if f.selected_C is not None}
            )
        ),
        any(f.candidate_scores for f in result.folds),
    )


def _mismatches(a: EvaluationResult, b: EvaluationResult) -> list[str]:
    comparisons = (
        (a.cohort_digest != b.cohort_digest, "cohort_mismatch"),
        (
            (a.n_participants, a.n_observations) != (b.n_participants, b.n_observations),
            "cohort_counts_mismatch",
        ),
        (
            a.feature_digest != b.feature_digest or a.feature_columns != b.feature_columns,
            "feature_mismatch",
        ),
        (
            (a.class_order, a.positive_class) != (b.class_order, b.positive_class),
            "class_definitions_mismatch",
        ),
        (a.metric_unit != b.metric_unit, "metric_unit_mismatch"),
        (a.execution_status != EvaluationStatus.COMPLETED, "design_a_incomplete"),
        (b.execution_status != EvaluationStatus.COMPLETED, "design_b_incomplete"),
    )
    return [reason for condition, reason in comparisons if condition]


def compare_designs(results: dict[str, EvaluationResult]) -> ComparisonResult:
    """Compare named private results without refitting or ranking scientific designs.

    Names sort lexically; each unordered pair reports A minus B for accuracy,
    balanced accuracy, macro-F1 and ROC-AUC. Incomplete or incompatible records
    remain displayed with null differences and explicit reasons. Digests match
    recorded inputs, not causal estimands or authenticated upstream history.
    """
    if not isinstance(results, dict) or len(results) < 2:
        raise InputValidationError("Supply at least two named private evaluation records.")
    if any(
        not _valid_label(name) or not isinstance(value, EvaluationResult)
        for name, value in results.items()
    ):
        raise InputValidationError("Use nonempty names and EvaluationResult operational records.")
    # Revalidate snapshots, including schema/unit and embedded-plan consistency.
    records = {
        name: EvaluationResult.from_dict(value.to_operational_dict())
        for name, value in sorted(results.items())
    }
    cohorts = {
        digest: f"cohort-{i + 1:02d}"
        for i, digest in enumerate(sorted({r.cohort_digest for r in records.values()}))
    }
    features = {
        digest: f"features-{i + 1:02d}"
        for i, digest in enumerate(sorted({r.feature_digest for r in records.values()}))
    }
    designs = tuple(
        ComparisonDesign(
            name,
            r.objective,
            r.diagnostic_only,
            r.pooled_metrics,
            _context(r, cohorts[r.cohort_digest], features[r.feature_digest]),
        )
        for name, r in records.items()
    )
    differences = []
    for (name_a, a), (name_b, b) in combinations(records.items(), 2):
        common = _mismatches(a, b)
        for metric in ("accuracy", "balanced_accuracy", "macro_f1", "roc_auc"):
            left = getattr(a.pooled_metrics, metric).value if a.pooled_metrics else None
            right = getattr(b.pooled_metrics, metric).value if b.pooled_metrics else None
            reasons = [*common]
            if left is None:
                reasons.append("metric_undefined_a")
            if right is None:
                reasons.append("metric_undefined_b")
            value = left - right if not reasons and left is not None and right is not None else None
            differences.append(MetricDifference(name_a, name_b, metric, value, tuple(reasons)))
    return ComparisonResult(designs, tuple(differences), INTERPRETATION)
