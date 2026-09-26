"""S11.B independent checks of candidate membership, state, pooling and ties."""

import warnings
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from sklearn.exceptions import ConvergenceWarning
from sklearn.pipeline import Pipeline
from test_inner_plans import tuning_inputs

from neurocvguard._evaluation_fits import FitOutcome
from neurocvguard._evaluation_inputs import fixed_pipeline, preflight
from neurocvguard._tuning import select_C, tune_C
from neurocvguard.models import CandidateScore, InnerFold


@pytest.fixture(scope="module")
def prepared():
    cohort, plan, config = tuning_inputs()
    return preflight(cohort, plan, config), config


def capture(monkeypatch, prepared):
    inputs, config = prepared
    observed = []
    original = Pipeline.fit

    def spy(self, X, y, **kwargs):
        assert not hasattr(self.named_steps["scaler"], "mean_")
        observed.append((self, X.copy(), y.copy(), kwargs["classifier__sample_weight"].copy()))
        return original(self, X, y, **kwargs)

    monkeypatch.setattr(Pipeline, "fit", spy)
    selection = tune_C(inputs, inputs.plan.folds[0], config, fixed_pipeline(config))
    assert selection.reason is None
    return selection, observed


def test_at_s11_03_same_memberships_every_candidate(monkeypatch, prepared):
    selection, observed = capture(monkeypatch, prepared)
    inputs, config = prepared
    outer = inputs.plan.folds[0]
    assert len(selection.events) == len(config.evaluation.C_grid) * len(outer.inner_folds)
    assert len({event.event_id for event in selection.events}) == len(selection.events)
    for C in sorted(config.evaluation.C_grid):
        events = [e for e in selection.events if e.C == C]
        assert [(e.inner_fold_id, e.fit_ids) for e in events] == [
            (inner.inner_fold_id, inner.train_ids) for inner in outer.inner_folds
        ]
    for event, (_, frame, targets, weights) in zip(selection.events, observed, strict=True):
        assert event.fit_ids == tuple(frame.index) == tuple(targets.index)
        people = inputs.participants.loc[frame.index]
        for person in set(people):
            assert weights[people == person].sum() == pytest.approx(1)


def test_at_s11_04_fresh_pipeline_and_transformers(monkeypatch, prepared):
    selection, observed = capture(monkeypatch, prepared)
    assert len({id(row[0]) for row in observed}) == len(selection.events)
    for step in ("imputer", "scaler", "classifier"):
        assert len({id(row[0].named_steps[step]) for row in observed}) == len(observed)
    for pipe, frame, _, _ in observed:
        expected = frame.fillna(frame.median()).fillna(0).mean().to_numpy()
        np.testing.assert_allclose(pipe.named_steps["scaler"].mean_, expected)
        assert not np.allclose(expected, prepared[0].features.mean().to_numpy())


@pytest.mark.parametrize(
    "pairs,expected",
    [
        ([(10, 0.8), (0.1, 0.8), (1, 0.8)], 0.1),
        ([(1, 0.8), (0.1, 0.8 - 5e-13)], 0.1),
        ([(1, 0.8), (0.1, 0.8 - 2e-12)], 1),
        ([(0.1, 0.8 - 1.5e-12), (1, 0.8 - 0.75e-12), (10, 0.8)], 1),
    ],
)
def test_at_s11_05_smallest_C_ties_with_global_maximum(pairs, expected):
    assert select_C(tuple(CandidateScore(C, score, None) for C, score in pairs)) == expected


def test_at_s11_06_pooled_people_outvote_fold_means_and_repeated_rows(monkeypatch, prepared):
    inputs, config = prepared
    outer = inputs.plan.folds[0]
    truth = inputs.targets.loc[list(outer.train_ids)]
    people = inputs.participants.loc[list(outer.train_ids)]
    classes = inputs.classes
    by_class = {c: sorted(set(people[truth == c])) for c in classes}
    assert [len(by_class[c]) for c in classes] == [6, 6]
    small = {p for c in classes for p in by_class[c][:2]}
    large = set(people) - small
    first_correct = small | {by_class[c][2] for c in classes}
    second_correct = large - {by_class[classes[0]][2]}
    # Give a small-fold participant many visits. Row weighting favors C=.1.
    repeated = sorted(small)[0]
    original_id = people[people == repeated].index[0]
    extra = [f"extra-{i}" for i in range(30)]
    inputs = replace(
        inputs,
        participants=pd.concat([inputs.participants, pd.Series([repeated] * 30, index=extra)]),
        targets=pd.concat([inputs.targets, pd.Series([truth[original_id]] * 30, index=extra)]),
    )
    train_ids = (*outer.train_ids, *extra)
    small_ids = tuple(i for i in train_ids if inputs.participants[i] in small)
    large_ids = tuple(i for i in train_ids if inputs.participants[i] in large)
    outer = replace(
        outer,
        train_ids=train_ids,
        inner_folds=(
            InnerFold("small", large_ids, small_ids),
            InnerFold("large", small_ids, large_ids),
        ),
    )
    config = replace(config, evaluation=replace(config.evaluation, C_grid=(1, 0.1)))

    def predictions(inputs, fold, inner, candidate, template):
        correct = first_correct if candidate.evaluation.C == 0.1 else second_correct
        labels = [
            inputs.targets[i]
            if inputs.participants[i] in correct
            else classes[1 - classes.index(inputs.targets[i])]
            for i in inner.validation_ids
        ]
        probs = np.asarray([[float(c == label) for c in classes] for label in labels])
        return FitOutcome(fold, None, probs, None, ())

    monkeypatch.setattr("neurocvguard._tuning.fit_inner", predictions)
    result = tune_C(inputs, outer, config, fixed_pipeline(config))
    assert [s.C for s in result.scores] == [0.1, 1]
    assert [s.balanced_accuracy for s in result.scores] == pytest.approx([0.5, 7 / 12])
    assert result.selected_C == 1
    # Hand oracle: mean fold balanced accuracy would choose .1 (.625 > .4375).
    assert (1 + 0.25) / 2 > (0 + 0.875) / 2
    assert (12 + 30) / (24 + 30) > 14 / (24 + 30)


def test_at_s11_07_failed_candidate_prevents_selection(monkeypatch, prepared):
    inputs, config = prepared
    original = Pipeline.fit

    def fail_one(self, X, y, **kwargs):
        if self.named_steps["classifier"].C == min(config.evaluation.C_grid):
            warnings.warn("synthetic nonconvergence", ConvergenceWarning, stacklevel=2)
        return original(self, X, y, **kwargs)

    monkeypatch.setattr(Pipeline, "fit", fail_one)
    result = tune_C(inputs, inputs.plan.folds[0], config, fixed_pipeline(config))
    assert result.selected_C is None and result.reason == "inner_tuning_failed"
    assert len(result.scores) == len(config.evaluation.C_grid)
    assert result.scores[0].balanced_accuracy is None
    assert result.scores[0].reason == "fit_did_not_converge"
    assert all(s.balanced_accuracy is not None for s in result.scores[1:])
    assert any(e.status == "failed" for e in result.events)
