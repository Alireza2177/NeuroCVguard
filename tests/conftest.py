"""Synthetic S03 inputs; this fixture adapter is not production S02 ingestion."""

from pathlib import Path

import pandas as pd
import pytest

from neurocvguard.config import ColumnMap
from neurocvguard.models import Cohort


@pytest.fixture
def make_cohort():
    def make(rows=None, *, columns=None, features=None, fixture=None):
        if fixture:
            # Known bundled synthetic data only; no generic application loader.
            data = pd.read_csv(
                Path(__file__).parent.parent / "fixtures" / fixture,
                sep="\t",
                dtype=str,
                keep_default_na=False,
            )
        else:
            data = pd.DataFrame(rows)
        roles = columns or ColumnMap()
        feature_frame = None if features is None else pd.DataFrame(features)
        return Cohort(data, feature_frame, roles, tuple(data[roles.observation_id]))

    return make


@pytest.fixture
def clean_cohort(make_cohort):
    return make_cohort(fixture="cohort_clean.tsv")
