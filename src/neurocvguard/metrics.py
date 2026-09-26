"""Explicit participant probability aggregation and complete-class metric semantics."""

from collections import defaultdict

import numpy as np
import numpy.typing as npt
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, recall_score, roc_auc_score

from neurocvguard.errors import EvaluationError
from neurocvguard.models import ClassMetric, MetricSet, MetricValue


def _validate_probabilities(probabilities: npt.NDArray[np.float64], n: int, k: int) -> None:
    if (
        probabilities.shape != (n, k)
        or not np.isfinite(probabilities).all()
        or (probabilities < 0).any()
        or (probabilities > 1).any()
        or not np.allclose(probabilities.sum(axis=1), 1, atol=1e-8, rtol=0)
    ):
        raise EvaluationError("Scoring requires finite aligned probability vectors summing to one.")


def aggregate_participants(
    participants: tuple[str, ...],
    truth: tuple[str, ...],
    probabilities: npt.NDArray[np.float64],
) -> tuple[tuple[str, ...], tuple[str, ...], npt.NDArray[np.float64]]:
    """Arithmetic means by explicit participant keys; no majority vote or relabeling."""
    if len(participants) != len(truth) or probabilities.ndim != 2:
        raise EvaluationError("Participant scoring inputs must have aligned lengths.")
    _validate_probabilities(probabilities, len(truth), probabilities.shape[1])
    positions: dict[str, list[int]] = defaultdict(list)
    for index, person in enumerate(participants):
        positions[person].append(index)
    order = tuple(sorted(positions))
    targets = []
    means = []
    for person in order:
        rows = positions[person]
        labels = {truth[index] for index in rows}
        if len(labels) != 1:
            raise EvaluationError("Participant scoring cannot relabel changing targets.")
        targets.append(truth[rows[0]])
        means.append(probabilities[rows].mean(axis=0))
    return (
        order,
        tuple(targets),
        np.asarray(means, dtype=np.float64).reshape(len(order), probabilities.shape[1]),
    )


def participant_metrics(
    truth: tuple[str, ...],
    probabilities: npt.NDArray[np.float64],
    *,
    class_order: tuple[str, ...],
    positive_class: str | None,
) -> MetricSet:
    """Score one vector per participant, with explicit labels and null reasons.

    Ties use class_order. Class-complete balanced accuracy and macro-F1 require
    every declared class to have true support. Binary AUC never guesses a positive
    label. No confidence interval or fold-average estimate is computed.
    """
    n = len(truth)
    if len(class_order) < 2 or len(set(class_order)) != len(class_order):
        raise EvaluationError("Metrics require at least two unique declared classes.")
    if not set(truth) <= set(class_order) or (
        positive_class is not None and positive_class not in class_order
    ):
        raise EvaluationError("Scored labels and the positive class must belong to class_order.")
    _validate_probabilities(probabilities, n, len(class_order))
    if not n:
        undefined = MetricValue(None, "empty_scored_set", 0)
        return MetricSet(
            undefined,
            undefined,
            undefined,
            undefined,
            0,
            tuple(ClassMetric(label, 0, None) for label in class_order),
            tuple(tuple(0 for _ in class_order) for _ in class_order),
        )
    indices = probabilities.argmax(axis=1)
    predicted = [class_order[int(index)] for index in indices]
    matrix = np.asarray(confusion_matrix(truth, predicted, labels=list(class_order)), dtype=int)
    support = matrix.sum(axis=1)
    recalls = recall_score(
        truth, predicted, labels=list(class_order), average=None, zero_division=0
    )
    per_class = tuple(
        ClassMetric(label, int(count), float(recall) if count else None)
        for label, count, recall in zip(class_order, support, recalls, strict=True)
    )
    accuracy = MetricValue(float(accuracy_score(truth, predicted)), None, n)
    complete = bool((support > 0).all())
    if complete:
        balanced = MetricValue(float(np.mean(recalls)), None, n)
        macro = MetricValue(
            float(
                f1_score(
                    truth, predicted, labels=list(class_order), average="macro", zero_division=0
                )
            ),
            None,
            n,
        )
    else:
        balanced = macro = MetricValue(None, "missing_true_class", n)
    if len(class_order) == 2 and positive_class is None:
        auc = MetricValue(None, "positive_class_unspecified", n)
    elif not complete:
        auc = MetricValue(None, "missing_true_class", n)
    elif len(class_order) == 2:
        assert positive_class is not None
        binary = np.asarray([label == positive_class for label in truth], dtype=int)
        auc = MetricValue(
            float(roc_auc_score(binary, probabilities[:, class_order.index(positive_class)])),
            None,
            n,
        )
    else:
        # Integer encoding follows declared order even when labels are not lexical.
        encoded = np.asarray([class_order.index(label) for label in truth], dtype=int)
        auc = MetricValue(
            float(
                roc_auc_score(
                    encoded,
                    probabilities,
                    labels=list(range(len(class_order))),
                    multi_class="ovr",
                    average="macro",
                )
            ),
            None,
            n,
        )
    return MetricSet(
        accuracy,
        balanced,
        macro,
        auc,
        n,
        per_class,
        tuple(tuple(int(value) for value in row) for row in matrix),
    )
