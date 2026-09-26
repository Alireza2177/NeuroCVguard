"""S10.C fixed probabilities with independent arithmetic and pairwise-rank oracles."""

import numpy as np
import pytest

from neurocvguard.errors import EvaluationError
from neurocvguard.metrics import aggregate_participants, participant_metrics


def rank_auc(truth, scores):
    positive = [score for label, score in zip(truth, scores, strict=True) if label]
    negative = [score for label, score in zip(truth, scores, strict=True) if not label]
    return sum((a > b) + 0.5 * (a == b) for a in positive for b in negative) / (
        len(positive) * len(negative)
    )


def test_at_s10_05_mean_probabilities_not_votes():
    people, truth, means = aggregate_participants(
        ("p1", "p2", "p1", "p1"),
        ("B", "A", "B", "B"),
        np.array([[0.51, 0.49], [0.5, 0.5], [0.51, 0.49], [0.01, 0.99]]),
    )
    assert people == ("p1", "p2") and truth == ("B", "A")
    np.testing.assert_allclose(means, [[1.03 / 3, 1.97 / 3], [0.5, 0.5]])
    result = participant_metrics(truth, means, class_order=("A", "B"), positive_class="B")
    assert result.accuracy.value == 1  # Mean chooses B; tie chooses first declared A.


def test_at_s10_11_binary_metric_oracle():
    truth = ("A", "A", "A", "B", "B", "B")
    a = np.array([0.9, 0.6, 0.4, 0.8, 0.3, 0.1])
    result = participant_metrics(
        truth, np.column_stack([a, 1 - a]), class_order=("A", "B"), positive_class="A"
    )
    assert result.confusion_matrix == ((2, 1), (1, 2))
    assert result.accuracy.value == pytest.approx(4 / 6)
    assert result.balanced_accuracy.value == pytest.approx(2 / 3)
    assert result.macro_f1.value == pytest.approx(2 / 3)
    assert [item.recall for item in result.per_class] == pytest.approx([2 / 3, 2 / 3])
    assert result.roc_auc.value == pytest.approx(7 / 9)
    assert result.roc_auc.value == pytest.approx(rank_auc([label == "A" for label in truth], a))
    assert all(
        value.n == 6
        for value in (result.accuracy, result.balanced_accuracy, result.macro_f1, result.roc_auc)
    )


def test_at_s10_11_multiclass_oracle_declared_order():
    classes = ("z", "a", "m")
    truth = ("z", "z", "z", "a", "a", "a", "m", "m", "m")
    probs = np.array(
        [
            [0.8, 0.1, 0.1],
            [0.6, 0.3, 0.1],
            [0.2, 0.7, 0.1],
            [0.1, 0.7, 0.2],
            [0.1, 0.2, 0.7],
            [0.2, 0.6, 0.2],
            [0.1, 0.2, 0.7],
            [0.6, 0.1, 0.3],
            [0.1, 0.3, 0.6],
        ]
    )
    result = participant_metrics(truth, probs, class_order=classes, positive_class=None)
    assert result.confusion_matrix == ((2, 1, 0), (0, 2, 1), (1, 0, 2))
    assert result.accuracy.value == pytest.approx(2 / 3)
    assert result.macro_f1.value == pytest.approx(2 / 3)
    expected = np.mean(
        [
            rank_auc([label == name for label in truth], probs[:, i])
            for i, name in enumerate(classes)
        ]
    )
    assert result.roc_auc.value == pytest.approx(expected)


def test_at_s10_09_single_class_test():
    result = participant_metrics(
        ("A", "A"), np.array([[0.9, 0.1], [0.2, 0.8]]), class_order=("A", "B"), positive_class="B"
    )
    assert result.accuracy.value == 0.5
    assert result.per_class[0].recall == 0.5 and result.per_class[1].recall is None
    for value in (result.balanced_accuracy, result.macro_f1, result.roc_auc):
        assert value.value is None and value.reason == "missing_true_class" and value.n == 2


def test_at_s10_10_unspecified_positive_class():
    result = participant_metrics(
        ("A", "B"), np.array([[0.9, 0.1], [0.2, 0.8]]), class_order=("A", "B"), positive_class=None
    )
    assert result.roc_auc.value is None and result.roc_auc.reason == "positive_class_unspecified"
    assert result.accuracy.value == result.balanced_accuracy.value == result.macro_f1.value == 1


def test_supported_never_predicted_class_has_real_zero():
    result = participant_metrics(
        ("A", "B"), np.array([[0.9, 0.1], [0.9, 0.1]]), class_order=("A", "B"), positive_class="B"
    )
    assert result.per_class[1].recall == 0
    assert result.macro_f1.value == pytest.approx(1 / 3)
    assert result.balanced_accuracy.value == 0.5


def test_empty_scored_set_nulls():
    result = participant_metrics((), np.empty((0, 2)), class_order=("A", "B"), positive_class="B")
    assert result.accuracy.reason == "empty_scored_set" and result.n_participants == 0


@pytest.mark.parametrize(
    "probabilities", [np.array([[np.nan, 0.1]]), np.array([[0.5, 0.6]]), np.array([[-0.1, 1.1]])]
)
def test_invalid_probabilities_refused(probabilities):
    with pytest.raises(EvaluationError):
        participant_metrics(("A",), probabilities, class_order=("A", "B"), positive_class="B")


def test_aggregation_never_relabels():
    with pytest.raises(EvaluationError, match="relabel"):
        aggregate_participants(("p", "p"), ("A", "B"), np.array([[0.5, 0.5], [0.5, 0.5]]))
