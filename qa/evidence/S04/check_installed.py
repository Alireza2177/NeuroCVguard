"""Probe ordinary S04 installation in an isolated interpreter outside the source tree."""

import subprocess
import sys
import tempfile

probe = """
from pathlib import Path
import sys
import neurocvguard
assert Path(neurocvguard.__file__).is_relative_to(sys.prefix)
import pandas as pd

from neurocvguard import audit_splits, load_split_plan
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.models import Cohort

data = pd.DataFrame(
    {
        "observation_id": ["o1", "o2", "o3", "o4"],
        "subject_id": ["p1", "p2", "p3", "p4"],
        "diagnosis": ["A", "B", "A", "B"],
        "site": ["site-X", "site-X", "site-X", "site-X"],
    }
)
config = AuditConfig(columns=ColumnMap(session=None))
cohort = Cohort(data, None, config.columns, ("o1", "o2", "o3", "o4"))
assignments = {
    "schema_version": "1.0",
    "plan_id": "synthetic-explicit",
    "origin": "imported",
    "cohort_digest": None,
    "objective": "unseen_participant",
    "scheme": "imported",
    "seed": None,
    "folds": [
        {"repeat_id": "r0", "fold_id": "f0", "train_ids": ["o1", "o2"], "test_ids": ["o3", "o4"]},
        {"repeat_id": "r0", "fold_id": "f1", "train_ids": ["o3", "o4"], "test_ids": ["o1", "o2"]},
    ],
}
plan = load_split_plan(assignments, cohort=cohort, config=config)
assert assignments["cohort_digest"] is None  # input not mutated
assert plan.cohort_digest is not None and plan.origin == "imported"
report = audit_splits(cohort, plan, config=config)
summary = next(
    check.evidence
    for check in report.checks
    if check.rule_id == "NCG-SPLIT-011" and check.scope.get("field") == "split_summary"
)
assert summary["valid_for_objective"] and summary["complete_cv"]
public_report = report.to_dict()
assert any(
    check["evidence"].get("evaluation_permitted") is True for check in public_report["checks"]
)
assert any(
    check.rule_id == "NCG-PROV-001" and check.status == "not_assessable" for check in report.checks
)

from neurocvguard.rules import SPLIT_RULES
assert len(SPLIT_RULES) == 11
print('PASS: ordinary installed S04 import, binding, audit, public summary and upstream boundary')
"""
with tempfile.TemporaryDirectory(prefix="neurocvguard-s04-") as directory:
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    print(result.stdout.strip())
