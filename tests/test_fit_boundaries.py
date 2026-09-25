"""S07.C plans never impersonate fit calls; synthetic records exercise validation only."""

from dataclasses import FrozenInstanceError, replace

import pytest
from test_split_audit import nested_plan

from neurocvguard.config import AuditConfig
from neurocvguard.errors import EvaluationError, InputValidationError
from neurocvguard.fit_boundaries import prepare_fit_boundary, validate_fit_event, validate_fit_ids
from neurocvguard.models import FitEvent, FoldStatus


def prepare(cohort, nested=False):
    plan = nested_plan(cohort)
    outer = plan.folds[0]
    boundary = prepare_fit_boundary(
        cohort,
        plan,
        config=AuditConfig(),
        event_id="planned-fit",
        repeat_id=outer.repeat_id,
        fold_id=outer.fold_id,
        C=1.0,
        inner_fold_id=outer.inner_folds[0].inner_fold_id if nested else None,
    )
    return boundary, outer


def test_at_s07_07_no_ghost_fit_events(clean_cohort, monkeypatch):
    def prohibited(*args, **kwargs):
        pytest.fail("Planning must not construct completed/failed FitEvent records")

    monkeypatch.setattr(FitEvent, "__post_init__", prohibited)
    boundary, outer = prepare(clean_cohort)
    assert not isinstance(boundary, FitEvent)
    assert not hasattr(boundary, "status") and not hasattr(boundary, "evidence_kind")
    assert not hasattr(boundary, "fit_events")
    assert validate_fit_ids(boundary, outer.train_ids) is None
    assert not hasattr(boundary, "status")


@pytest.mark.parametrize("nested", [False, True])
def test_actual_ids_restricted_to_current_training(clean_cohort, nested):
    boundary, outer = prepare(clean_cohort, nested)
    validate_fit_ids(boundary, boundary.allowed_ids)
    validate_fit_ids(boundary, boundary.allowed_ids[:1])
    with pytest.raises(EvaluationError, match="boundary violation"):
        validate_fit_ids(boundary, (outer.test_ids[0],))
    if nested:
        with pytest.raises(EvaluationError, match="boundary violation"):
            validate_fit_ids(boundary, (outer.inner_folds[0].validation_ids[0],))


@pytest.mark.parametrize("status", [FoldStatus.COMPLETED, FoldStatus.FAILED])
def test_handwritten_event_validation_does_not_authenticate_history(clean_cohort, status):
    boundary, _ = prepare(clean_cohort, True)
    # Synthetic record only, explicitly not a claim about an executed fit.
    event = FitEvent(
        boundary.event_id,
        boundary.repeat_id,
        boundary.fold_id,
        boundary.inner_fold_id,
        boundary.C,
        boundary.allowed_ids,
        status,
        boundary.scope,
    )
    assert validate_fit_event(event, boundary=boundary) is None
    for changes in (
        {"event_id": "different"},
        {"C": 2.0},
        {"repeat_id": "different"},
        {"fit_ids": ("outside-private",)},
    ):
        with pytest.raises(EvaluationError) as error:
            validate_fit_event(replace(event, **changes), boundary=boundary)
        assert "outside-private" not in str(error.value)


@pytest.mark.parametrize("C", [0.0, -1.0, float("inf"), float("nan"), True])
def test_invalid_candidate_parameter(clean_cohort, C):
    boundary, _ = prepare(clean_cohort)
    with pytest.raises(EvaluationError):
        replace(boundary, C=C)


def test_plans_are_immutable_and_ids_not_in_repr(clean_cohort):
    boundary, _ = prepare(clean_cohort)
    assert boundary.allowed_ids[0] not in repr(boundary)
    with pytest.raises(FrozenInstanceError):
        boundary.C = 3.0
    with pytest.raises(EvaluationError):
        validate_fit_ids(boundary, ())
    with pytest.raises(EvaluationError):
        validate_fit_ids(boundary, boundary.allowed_ids[:1] * 2)


def test_unknown_fold_is_not_prepared(clean_cohort):
    with pytest.raises(InputValidationError, match="Unknown repeat/fold"):
        prepare_fit_boundary(
            clean_cohort,
            nested_plan(clean_cohort),
            config=AuditConfig(),
            event_id="planned",
            repeat_id="absent",
            fold_id="absent",
            C=1.0,
        )
