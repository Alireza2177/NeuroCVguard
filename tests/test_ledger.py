"""S07.A strict declarations, identities and fold context."""

import copy
import json
from dataclasses import replace

import pytest
from test_split_audit import nested_plan

from neurocvguard.config import AuditConfig
from neurocvguard.errors import InputValidationError
from neurocvguard.provenance import load_preprocessing_ledger


def declaration(**changes):
    event = dict(
        event_id="event-1",
        transform="PCA",
        data_dependent=True,
        repeat_id=None,
        fold_id=None,
        inner_fold_id=None,
        fit_scope="all_cohort",
        fit_ids=None,
        uses_target=False,
        note="Synthetic only",
    )
    event.update(changes)
    return dict(schema_version="1.0", source="user_declaration", events=[event])


def load(source, cohort, plan=None):
    return load_preprocessing_ledger(source, cohort=cohort, config=AuditConfig(), plan=plan)


def test_at_s07_04_forged_runtime_label(clean_cohort):
    for source in ("runtime_verified", "observed", "runtime"):
        data = declaration()
        data["source"] = source
        with pytest.raises(InputValidationError):
            load(data, clean_cohort)


def test_local_json_roundtrip_detached_and_bom(clean_cohort, tmp_path):
    original = declaration()
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(original), encoding="utf-8-sig")
    ledger = load(path, clean_cohort)
    assert ledger.to_operational_dict() == original
    original["events"][0]["note"] = "changed"
    assert ledger.events[0].note == "Synthetic only"


@pytest.mark.parametrize("text", ['{"source":1,"source":2}', '{"events":NaN}', "{}", "[]"])
def test_strict_json_rejected(clean_cohort, tmp_path, text):
    path = tmp_path / "ledger.json"
    path.write_text(text)
    with pytest.raises(InputValidationError):
        load(path, clean_cohort)


@pytest.mark.parametrize(
    "changes",
    [
        {"extra": 1},
        {"fit_ids": ["unknown-private-id"]},
        {"fit_ids": []},
        {"event_id": " padded "},
        {"repeat_id": "r"},
        {"inner_fold_id": "i"},
        {"fit_scope": "outer_train"},
        {"fit_scope": "inner_train"},
        {"fit_scope": "outer_train", "repeat_id": "r", "fold_id": "f", "inner_fold_id": "i"},
    ],
)
def test_invalid_declarations(clean_cohort, changes):
    with pytest.raises(InputValidationError) as error:
        load(declaration(**changes), clean_cohort)
    assert "unknown-private-id" not in str(error.value)


def test_duplicate_events_and_fit_ids_rejected(clean_cohort):
    data = declaration()
    data["events"].append(copy.deepcopy(data["events"][0]))
    with pytest.raises(InputValidationError, match="unique"):
        load(data, clean_cohort)
    key = clean_cohort.observation_order[0]
    with pytest.raises(InputValidationError):
        load(declaration(fit_ids=[key, key]), clean_cohort)


def test_named_nested_scope_and_outside_ids_are_not_parse_errors(clean_cohort):
    plan = nested_plan(clean_cohort)
    outer = plan.folds[0]
    data = declaration(
        fit_scope="inner_train",
        repeat_id=outer.repeat_id,
        fold_id=outer.fold_id,
        inner_fold_id=outer.inner_folds[0].inner_fold_id,
        fit_ids=[outer.test_ids[0]],
    )
    assert load(data, clean_cohort, plan).events[0].fit_ids == (outer.test_ids[0],)
    data["events"][0]["inner_fold_id"] = "absent"
    with pytest.raises(InputValidationError, match="Unknown inner"):
        load(data, clean_cohort, plan)
    data["events"][0]["inner_fold_id"] = None
    data["events"][0]["fit_scope"] = "outer_train"
    data["events"][0]["fold_id"] = "absent"
    with pytest.raises(InputValidationError, match="Unknown repeat/fold"):
        load(data, clean_cohort, plan)


def test_missing_plan_preserves_unresolved_declaration(clean_cohort):
    ledger = load(declaration(fit_scope="outer_train", repeat_id="r", fold_id="f"), clean_cohort)
    assert ledger.events[0].fit_ids is None


def test_corrupt_plan_cannot_supply_training_context(clean_cohort):
    plan = nested_plan(clean_cohort)
    first = plan.folds[0]
    bad = replace(
        plan, folds=(replace(first, train_ids=first.train_ids + first.test_ids), *plan.folds[1:])
    )
    with pytest.raises(InputValidationError, match="partition"):
        load(declaration(), clean_cohort, bad)


def test_local_file_limits_and_network_paths(clean_cohort, tmp_path):
    for path in (
        "https://invalid.example/ledger.json",
        "//server/share/ledger.json",
        tmp_path / "a.csv",
    ):
        with pytest.raises(InputValidationError, match="local"):
            load(path, clean_cohort)
    path = tmp_path / "large.json"
    path.write_bytes(b" " * (1024 * 1024 + 1))
    config = AuditConfig()
    config = replace(config, limits=replace(config.limits, max_input_mb=1))
    with pytest.raises(InputValidationError, match="max_input_mb"):
        load_preprocessing_ledger(path, cohort=clean_cohort, config=config)
