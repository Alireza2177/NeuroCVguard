"""S06 statistic oracles independent of implementation details."""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from test_association_pairs import changed, pair_cohort, views

from neurocvguard.checks.associations import _statistic
from neurocvguard.errors import InputValidationError


def statistic(cohort, minimum=5):
    return _statistic(views(cohort)[0], minimum)


def test_at_s06_01_zero_association():
    result = statistic(pair_cohort())
    assert result.value == pytest.approx(0.0, abs=1e-14)
    assert result.counts == ((5, 5), (5, 5)) and result.n == 20


def test_at_s06_02_perfect_association():
    result = statistic(pair_cohort(((10, 0), (0, 10))))
    assert result.value == pytest.approx(1.0, abs=1e-14)
    assert result.counts == ((10, 0), (0, 10))
    assert result.expected == ((5.0, 5.0), (5.0, 5.0))


@pytest.mark.parametrize("table", [((5, 5),), ((10,), (10,))])
def test_at_s06_03_constant_variable(table):
    result = statistic(pair_cohort(table))
    assert result.value is None and result.reason == "constant_variable"
    assert result.counts == table and result.n == sum(map(sum, table))


@given(st.integers(1, 10))
@settings(max_examples=6, deadline=None)
def test_at_s06_04_repeat_invariance(repeats):
    table = ((4, 7), (3, 11))
    assert statistic(pair_cohort(table, repeats)) == statistic(pair_cohort(table))


def test_at_s06_08_high_cardinality(monkeypatch):
    import neurocvguard.checks.associations as module

    cohort = pair_cohort(tuple((1, 1) for _ in range(101)))

    def fail(*args, **kwargs):
        pytest.fail("Do not allocate a high-cardinality table or compute its statistic")

    monkeypatch.setattr(module.np, "zeros", fail)
    result = statistic(cohort)
    assert result.value is None and result.reason == "too_many_categories"
    assert result.counts is None and result.n == 0


@given(st.permutations(("renamed-Z", "renamed-A", "renamed-M")))
@settings(max_examples=6, deadline=None)
def test_at_s06_10_category_name_invariance(names):
    cohort = pair_cohort(((1, 3, 4), (6, 2, 5), (3, 8, 1)))
    original = statistic(cohort)
    data = cohort.metadata
    data["site"] = data.site.map({f"s-{i}": value for i, value in enumerate(names)})
    data["diagnosis"] = data.diagnosis.map({f"t-{i}": value for i, value in enumerate(names[::-1])})
    transformed = statistic(changed(cohort, data.iloc[::-1]))
    assert transformed.value == pytest.approx(original.value, abs=1e-14)
    assert transformed.row_levels == tuple(sorted(names))


def test_literal_multiclass_formula_oracle():
    table = ((10, 20, 0), (0, 10, 30))
    total = sum(map(sum, table))
    rows = list(map(sum, table))
    columns = [sum(row[j] for row in table) for j in range(3)]
    chi_square = sum(
        (table[i][j] - rows[i] * columns[j] / total) ** 2 / (rows[i] * columns[j] / total)
        for i in range(2)
        for j in range(3)
    )
    reference = math.sqrt(chi_square / total)  # min(r-1,c-1)=1
    assert statistic(pair_cohort(table)).value == pytest.approx(reference, abs=1e-14)


def test_normative_fixture_oracles():
    values = json.loads((Path(__file__).parent.parent / "fixtures/known_answers.json").read_text())
    for oracle in values["association_oracles"]:
        assert statistic(pair_cohort(oracle["table"])).value == pytest.approx(
            oracle["cramers_v"], abs=1e-14
        )


def test_exact_scipy_method_and_correction(monkeypatch):
    import neurocvguard.checks.associations as module

    original = module.association
    calls = []

    def spy(table, **kwargs):
        calls.append(kwargs)
        return original(table, **kwargs)

    monkeypatch.setattr(module, "association", spy)
    statistic(pair_cohort(((8, 2), (2, 8))))
    assert calls == [dict(method="cramer", correction=False)]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_statistic_is_an_error(monkeypatch, bad):
    import neurocvguard.checks.associations as module

    monkeypatch.setattr(module, "association", lambda *args, **kwargs: bad)
    with pytest.raises(InputValidationError, match="Non-finite"):
        statistic(pair_cohort())


def test_unused_pandas_categories_removed_but_observed_zeros_retained():
    cohort = pair_cohort(((10, 0), (0, 10)))
    data = cohort.metadata
    data["site"] = pd.Categorical(data.site, categories=["s-0", "s-1", "unused"])
    data["diagnosis"] = pd.Categorical(data.diagnosis, categories=["unused-target", "t-0", "t-1"])
    assert statistic(changed(cohort, data)) == statistic(cohort)


def test_category_limit_is_inclusive_and_uses_all_observed_levels():
    assert statistic(pair_cohort(tuple((1, 1) for _ in range(100)))).reason is None
    cohort = pair_cohort(tuple((1, 1) for _ in range(101)))
    data = cohort.metadata
    data.loc[data.site == "s-100", "diagnosis"] = None
    assert statistic(changed(cohort, data)).reason == "too_many_categories"


def test_sparse_counts_include_observed_zeros_and_expected_counts():
    result = statistic(pair_cohort(((10, 0), (0, 10))))
    assert result.sparse_observed_cells == 2 and result.sparse_expected_cells == 0
    result = statistic(pair_cohort(((1, 10), (10, 79))), 2)
    assert result.sparse_observed_cells == 1 and result.sparse_expected_cells == 1


def test_global_rng_state_preserved():
    before = np.random.get_state()
    statistic(pair_cohort())
    after = np.random.get_state()
    assert before[0] == after[0] and np.array_equal(before[1], after[1]) and before[2:] == after[2:]
