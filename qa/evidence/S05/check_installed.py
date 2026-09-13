"""Probe ordinary S05 installation in an isolated interpreter outside the source tree."""

import subprocess
import sys
import tempfile

probe = """
from pathlib import Path
import sys
import neurocvguard
assert Path(neurocvguard.__file__).is_relative_to(sys.prefix)
import pandas as pd

from neurocvguard import make_splits
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.models import Cohort

metadata = pd.DataFrame(
    {
        "observation_id": ["o1", "o2", "o3", "o4", "o5", "o6"],
        "subject_id": ["p1", "p2", "p3", "p4", "p5", "p6"],
        "diagnosis": ["A", "B", "A", "B", "A", "B"],
    }
)
config = AuditConfig(columns=ColumnMap(session=None, site=None))
cohort = Cohort(metadata, None, config.columns, tuple(metadata.observation_id))
plan = make_splits(cohort, config=config)
assert plan.origin == "generated" and len(plan.folds) == 3
assert plan.generation_report is not None
summary = next(
    check.evidence
    for check in plan.generation_report.checks
    if check.scope.get("field") == "split_summary"
)
assert summary["complete_cv"] and summary["valid_for_objective"]
paths = plan.write("local-splits")
assert paths["plan"].name == "plan.json"
assert paths["generation_report"].name == "generation.private.json"

from neurocvguard import load_split_plan
from neurocvguard.models import AuditReport
from neurocvguard.rules import PLAN_RULES
assert load_split_plan(paths['plan'], cohort=cohort, config=config) == plan
private = AuditReport.from_json(paths['generation_report'].read_text())
assert private.provenance['sensitive_details'] is True
assert private.provenance['versions']['scikit-learn']
assert len(PLAN_RULES) == 3
print('PASS: installed S05 generation, audit, sensitive writers and round trip')
"""
with tempfile.TemporaryDirectory(prefix="neurocvguard-s05-") as directory:
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    print(result.stdout.strip())
