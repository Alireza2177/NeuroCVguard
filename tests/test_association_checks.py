"""S06 scoped warnings, support records and conservative public projection."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from test_association_pairs import changed, pair_cohort

from neurocvguard.checks.associations import check_associations
from neurocvguard.config import AssociationConfig, AuditConfig
from neurocvguard.errors import InputValidationError
from neurocvguard.models import CheckStatus, Severity
from neurocvguard.rules import ASSOCIATION_RULES


def checks(cohort, **options):
    return check_associations(
        cohort, config=AuditConfig(columns=cohort.columns, association=AssociationConfig(**options))
    )


def site_check(results, number):
    return next(
        item
        for item in results
        if item.rule_id == f"NCG-ASSOC-{number:03}" and item.scope["field"] == "site"
    )


def test_at_s06_07_sparse_warning_without_inference():
    results = checks(pair_cohort(((10, 0), (0, 10))))
    sparse = site_check(results, 2)
    assert sparse.status == CheckStatus.FAIL and sparse.severity == Severity.WARNING
    assert sparse.evidence["sparse_observed_cells"] == 2
    assert sparse.evidence["sparse_expected_cells"] == 0
    text = json.dumps(sparse.to_dict(sensitive_details=True))
    assert "p_value" not in text and "p-value" not in text and "*" not in text
    assert "unstable" in sparse.message and "descriptive" in sparse.message
    assert site_check(checks(pair_cohort()), 2).status == CheckStatus.PASS


def test_at_s06_09_inclusive_noncausal_review_warning():
    results = checks(pair_cohort(((10, 0), (0, 10))), review_threshold=1.0)
    review = site_check(results, 1)
    assert review.status == CheckStatus.FAIL and review.severity == Severity.WARNING
    assert review.message == (
        "Acquisition/target association warrants review under the stated generalization objective."
    )
    assert "For a claim about new sites or phases" in review.recommendation
    assert "do not infer causal bias or model shortcut use" in review.recommendation
    assert review.to_dict()["message"] == review.message
    assert "violation" not in review.to_dict()["message"]
    zero = site_check(checks(pair_cohort(), review_threshold=0.0), 1)
    assert zero.status == CheckStatus.FAIL


def test_missing_pair_support_records_and_cohort_unchanged():
    cohort = pair_cohort()
    data = cohort.metadata
    data.loc[0, "site"] = None
    data.loc[1, "diagnosis"] = None
    cohort = changed(cohort, data)
    evidence = site_check(checks(cohort), 1).evidence
    assert (evidence["n_original"], evidence["n_complete"], evidence["n_excluded"]) == (20, 18, 2)
    assert evidence["n_in_table"] == evidence["statistic"]["n"] == 18
    assert evidence["missing_field_participants"] == evidence["missing_target_participants"] == 1
    assert sum(map(sum, evidence["table"])) == 18
    assert "not independent-sample inference" in evidence["interpretation"]
    pd.testing.assert_frame_equal(cohort.metadata, data)


def test_unstable_pair_never_computes_remaining_people(monkeypatch):
    import neurocvguard.checks.associations as module

    cohort = pair_cohort(repeats=2)
    data = cohort.metadata
    data.loc[0, "diagnosis"] = "changed-target"

    def fail(*args, **kwargs):
        pytest.fail("Unsupported pairs must not compute a table")

    monkeypatch.setattr(module, "expected_freq", fail)
    results = checks(changed(cohort, data))
    assert len(results) == 3
    for item in results:
        assert item.status == CheckStatus.NOT_ASSESSABLE
        assert item.evidence["statistic"] == dict(
            value=None, reason="unstable_within_participant", n=0
        )
        assert item.evidence["n_original"] == 20 and item.evidence["n_complete"] == 19
        assert item.evidence["table"] is None
        assert item.to_dict()["evidence"]["statistic"]["reason"] == "unstable_within_participant"


def test_constant_pair_has_null_and_independent_sparse_check(monkeypatch):
    import neurocvguard.checks.associations as module

    def fail(*args, **kwargs):
        pytest.fail("Constant pairs must not call association")

    monkeypatch.setattr(module, "association", fail)
    results = checks(pair_cohort(((1, 9),)))
    result = site_check(results, 3)
    assert result.status == CheckStatus.NOT_ASSESSABLE
    assert result.evidence["statistic"] == dict(value=None, reason="constant_variable", n=10)
    assert site_check(results, 2).status == CheckStatus.FAIL
    assert not any(item.rule_id == "NCG-ASSOC-001" for item in results)


@pytest.mark.parametrize("table", [((10, 0), (0, 10)), ((5, 5), (5, 5))])
def test_public_omits_all_linked_numbers_and_sensitive_labels(table):
    cohort = pair_cohort(table)
    data = cohort.metadata
    data["site"] = data.site.map({"s-0": "<script>private-A</script>", "s-1": "private-B"})
    results = checks(changed(cohort, data))
    for item in results:
        public = item.to_dict()
        assert public["evidence"] == {"details_omitted": True}
        assert "private-" not in json.dumps(public)
        private = item.to_dict(sensitive_details=True)
        assert private["evidence"]["n_original"] == 20
        assert "p-0001" not in json.dumps(private)
    assert "<script>private-A</script>" in json.dumps(
        site_check(results, 1).to_dict(sensitive_details=True)
    )


def test_public_reason_is_whitelisted_not_free_text():
    item = site_check(checks(pair_cohort(((2, 2),))), 3)
    forged = replace(item, evidence={"statistic": {"value": None, "reason": "private-subject"}})
    assert forged.to_dict()["evidence"] == {"details_omitted": True}


def test_scope_ids_unique_and_output_deterministic():
    cohort = pair_cohort()
    first = checks(cohort)
    second = checks(changed(cohort, cohort.metadata.iloc[::-1]))
    assert first == second and len({item.instance_id for item in first}) == len(first) == 6
    assert {item.scope["field"] for item in first} == {"site", "phase", "categorical_covariates:0"}


def test_config_thresholds_change_flags_not_statistic():
    cohort = pair_cohort(((8, 2), (2, 8)))
    first = checks(cohort, review_threshold=0.1, min_cell_count=1)
    second = checks(cohort, review_threshold=0.9, min_cell_count=10)
    assert site_check(first, 1).evidence["statistic"] == site_check(second, 1).evidence["statistic"]
    assert site_check(first, 1).status == CheckStatus.FAIL
    assert site_check(second, 1).status == CheckStatus.PASS
    assert site_check(first, 2).status == CheckStatus.PASS
    assert site_check(second, 2).status == CheckStatus.FAIL


def test_nonfinite_expected_counts_are_errors(monkeypatch):
    import neurocvguard.checks.associations as module

    monkeypatch.setattr(module, "expected_freq", lambda table: np.full(table.shape, np.nan))
    with pytest.raises(InputValidationError, match="Non-finite expected counts"):
        checks(pair_cohort())


def test_rules_match_normative_catalog():
    catalog = json.loads((Path(__file__).parent.parent / "qa/rule_catalog.json").read_text())
    for rule in ASSOCIATION_RULES:
        expected = next(row for row in catalog if row["id"] == rule.id)
        assert rule.name == expected["name"] and rule.meaning == expected["meaning"]
        assert rule.stage == expected["stage"] == "S06"


def test_expected_cells_alone_can_trigger_sparse_warning():
    result = site_check(checks(pair_cohort(((5, 5), (5, 100)))), 2)
    assert result.status == CheckStatus.FAIL
    assert result.evidence["sparse_observed_cells"] == 0
    assert result.evidence["sparse_expected_cells"] == 1


def test_report_round_trip_preserves_sensitivity_boundary():
    from neurocvguard.models import AuditReport
    from neurocvguard.serialization import canonical_json

    root = Path(__file__).parent.parent
    report = AuditReport.from_dict(
        json.loads((root / "fixtures/report_schema_example.json").read_text())
    )
    report = replace(report, checks=report.checks + checks(pair_cohort(((10, 0), (0, 10)))))
    public = report.to_dict()
    private = report.to_dict(sensitive_details=True)
    assert private["provenance"]["sensitive_details"] is True
    assert public["provenance"]["sensitive_details"] is False
    assert AuditReport.from_json(canonical_json(public)).to_dict() == public
    for item in public["checks"]:
        if item["rule_id"].startswith("NCG-ASSOC"):
            assert item["evidence"] == {"details_omitted": True}
    assert "expected_counts" not in canonical_json(public)
    assert "expected_counts" in canonical_json(private)


def test_documented_association_example():
    document = (Path(__file__).parent.parent / "docs/association_diagnostics.md").read_text(
        encoding="utf-8"
    )
    example = document.split("```python\n", 1)[1].split("```", 1)[0]
    # Execute only this repository's fixed synthetic example as documentation QA.
    exec(compile(example, "docs/association_diagnostics.md", "exec"), {})
