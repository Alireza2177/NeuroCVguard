"""S06 pairwise participant-denominator and stability boundaries."""

from dataclasses import replace

import pandas as pd
import pytest

from neurocvguard.checks.associations import _pair_views
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.errors import ConfigurationError
from neurocvguard.models import Cohort


def pair_cohort(table=((5, 5), (5, 5)), repeats=1):
    records = []
    person = 0
    for row, counts in enumerate(table):
        for column, count in enumerate(counts):
            for _ in range(count):
                person += 1
                for visit in range(repeats):
                    records.append(
                        dict(
                            observation_id=f"o-{person:04}-{visit:02}",
                            subject_id=f"p-{person:04}",
                            site=f"s-{row}",
                            diagnosis=f"t-{column}",
                            phase=f"phase-{row}",
                            scanner=f"scanner-{row}",
                        )
                    )
    data = pd.DataFrame(
        records, columns=["observation_id", "subject_id", "site", "diagnosis", "phase", "scanner"]
    )
    columns = ColumnMap(session=None, phase="phase", categorical_covariates=("scanner",))
    return Cohort(data, None, columns, tuple(data.observation_id))


def views(cohort):
    return _pair_views(cohort, AuditConfig(columns=cohort.columns))


def changed(cohort, data):
    return Cohort(data, None, cohort.columns, tuple(data.observation_id))


def test_at_s06_05_within_person_covariate_changes():
    cohort = pair_cohort(repeats=2)
    data = cohort.metadata
    data.loc[0, "site"] = "a-different-site"
    cohort = changed(cohort, data)
    site, phase, scanner = views(cohort)
    assert site.reason == "unstable_within_participant" and site.n_unstable_field == 1
    assert site.n_original == 20 and site.n_complete == 19
    assert phase.reason is None and scanner.reason is None
    pd.testing.assert_frame_equal(cohort.metadata, data)


def test_at_s06_06_missing_pairs():
    cohort = pair_cohort()
    data = cohort.metadata
    data.loc[0, "site"] = None
    data.loc[1, "diagnosis"] = None
    cohort = changed(cohort, data)
    site = views(cohort)[0]
    assert site.reason is None and site.n_original == 20 and site.n_complete == 18
    assert site.n_missing_field == site.n_missing_target == 1
    pd.testing.assert_frame_equal(cohort.metadata, data)


def test_missing_one_visit_is_not_a_license_to_choose_another():
    cohort = pair_cohort(repeats=2)
    data = cohort.metadata
    data.loc[0, "site"] = None
    site = views(changed(cohort, data))[0]
    assert site.n_complete == 19 and site.n_missing_field == 1 and site.reason is None
    assert "p-0001" not in {p for p, _, _ in site.records}


def test_instability_is_not_hidden_by_missingness():
    cohort = pair_cohort(repeats=2)
    data = cohort.metadata
    data.loc[0, "site"] = "other"
    data.loc[data.subject_id == "p-0001", "diagnosis"] = None
    site = views(changed(cohort, data))[0]
    assert site.reason == "unstable_within_participant"
    assert site.n_missing_target == site.n_unstable_field == 1


def test_changing_target_invalidates_each_pair():
    cohort = pair_cohort(repeats=2)
    data = cohort.metadata
    data.loc[0, "diagnosis"] = "other-target"
    assert all(
        p.reason == "unstable_within_participant" and p.n_unstable_target == 1
        for p in views(changed(cohort, data))
    )


def test_complete_pair_view_repeat_and_row_order_invariance():
    once, repeated = pair_cohort(), pair_cohort(repeats=10)
    assert views(once) == views(repeated)
    data = repeated.metadata.iloc[::-1]
    assert views(repeated) == views(changed(repeated, data))


@pytest.mark.parametrize("column", ["site", "diagnosis"])
def test_absent_mapped_column_is_explicit(column):
    cohort = pair_cohort()
    result = views(changed(cohort, cohort.metadata.drop(columns=column)))[0]
    assert result.reason == ("missing_field" if column == "site" else "missing_target")
    assert result.n_complete == 0 and result.n_original == 20


def test_only_explicit_acquisition_fields_are_requested():
    cohort = pair_cohort()
    columns = replace(cohort.columns, site=None, phase=None, categorical_covariates=())
    cohort = Cohort(cohort.metadata, None, columns, cohort.observation_order)
    assert views(cohort) == ()
    with pytest.raises(ConfigurationError, match="roles differ"):
        _pair_views(cohort, AuditConfig())


def test_invalid_category_values_block_only_the_affected_pair():
    cohort = pair_cohort()
    data = cohort.metadata
    data.loc[0, "site"] = " padded "
    result = views(changed(cohort, data))
    assert result[0].reason == "invalid_values" and result[0].n_invalid_field == 1
    assert result[1].reason is None and result[2].reason is None


def test_no_complete_pairs_or_empty_cohort():
    cohort = pair_cohort()
    data = cohort.metadata
    data["site"] = None
    assert views(changed(cohort, data))[0].reason == "no_complete_pairs"
    assert views(pair_cohort(((0, 0), (0, 0))))[0].reason == "no_complete_pairs"
