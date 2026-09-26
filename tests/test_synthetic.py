"""S13.A deterministic mechanisms, local RNG and explicit fictitious identities."""

import random
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from neurocvguard.errors import InputValidationError
from neurocvguard.synthetic import (
    SCENARIOS,
    SyntheticParameters,
    generate_synthetic,
    scenario_parameters,
)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_at_s13_01_deterministic_shape_and_identity(scenario):
    p = scenario_parameters(scenario, n_participants=24, n_classes=3, n_features=4)
    a, b = generate_synthetic(p), generate_synthetic(p)
    pd.testing.assert_frame_equal(a.metadata, b.metadata, check_exact=True)
    pd.testing.assert_frame_equal(a.features, b.features, check_exact=True)
    assert a.features.shape == (48, 5)
    assert a.metadata.observation_id.is_unique
    assert a.metadata.subject_id.nunique() == 24
    assert (a.metadata.groupby("subject_id").target.nunique() == 1).all()
    assert a.metadata.session.nunique() == 2  # participant-local session labels
    assert a.metadata.target.value_counts().tolist() == [16, 16, 16]
    assert a.parameters.to_dict() == p.to_dict()


def test_at_s13_02_rng_isolation():
    before = np.random.get_state()
    python_before = random.getstate()
    for scenario in SCENARIOS:
        generate_synthetic(scenario_parameters(scenario))
    after = np.random.get_state()
    assert before[0] == after[0] and before[2:] == after[2:]
    np.testing.assert_array_equal(before[1], after[1])
    assert python_before == random.getstate()


@pytest.mark.parametrize("field", ["signal_strength", "participant_effect", "site_effect"])
def test_at_s13_03_strength_changes_only_additive_mechanism(field):
    p = SyntheticParameters(signal_strength=0, participant_effect=0, site_effect=0)
    base = generate_synthetic(p)
    one = generate_synthetic(replace(p, **{field: 1.0}))
    two = generate_synthetic(replace(p, **{field: 2.0}))
    pd.testing.assert_frame_equal(base.metadata, one.metadata)
    pd.testing.assert_frame_equal(base.metadata, two.metadata)
    x, y, z = [d.features.iloc[:, 1:].to_numpy() for d in (base, one, two)]
    assert not np.array_equal(x, y)
    np.testing.assert_allclose(z - x, 2 * (y - x), atol=1e-14)
    # Each added latent effect is constant across a person's visits.
    np.testing.assert_allclose((y - x)[::2], (y - x)[1::2], atol=1e-14)


def test_at_s13_03_association_changes_sites_without_relabeling_or_noise():
    p = SyntheticParameters(site_effect=0, site_target_association=0)
    a = generate_synthetic(p)
    b = generate_synthetic(replace(p, site_target_association=1))
    pd.testing.assert_frame_equal(a.metadata.drop(columns="site"), b.metadata.drop(columns="site"))
    pd.testing.assert_frame_equal(a.features, b.features, check_exact=True)
    assert not a.metadata.site.equals(b.metadata.site)
    for target, site in zip(b.metadata.target, b.metadata.site, strict=True):
        assert int(site.rsplit("-", 1)[1]) in {int(target[-1]), (int(target[-1]) + 1) % 3}
    assert scenario_parameters("repeated") == replace(p, participant_effect=3)
    assert scenario_parameters("site_shift") == replace(
        p, site_effect=2, site_target_association=0.8
    )


@pytest.mark.parametrize(
    "change",
    [
        {"seed": True},
        {"seed": -1},
        {"n_participants": 1},
        {"n_classes": 1},
        {"n_sites": 0},
        {"n_features": 0},
        {"observations_per_participant": 0},
        {"n_classes": 61},
        {"signal_strength": float("nan")},
        {"participant_effect": -1},
        {"site_effect": float("inf")},
        {"site_target_association": 1.1},
        {"n_participants": 100_000, "n_features": 1000},
    ],
)
def test_invalid_parameters_fail_before_allocation(change):
    with pytest.raises(InputValidationError):
        SyntheticParameters(**change)


def test_at_s13_06_synthetic_labeling_and_no_alias_inputs():
    data = generate_synthetic()
    assert set(data.metadata.data_kind) == {"fully_synthetic_no_patient_data"}
    assert data.metadata.observation_id.str.startswith("SYN-").all()
    assert data.metadata.subject_id.str.startswith("SYN-").all()
    assert data.config().evaluation.feature_columns == tuple(data.features.columns[1:])
    with pytest.raises(InputValidationError):
        scenario_parameters("real")
    with pytest.raises(InputValidationError):
        scenario_parameters("clean", hidden=1)
