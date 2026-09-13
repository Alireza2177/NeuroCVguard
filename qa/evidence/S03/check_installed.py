"""Probe the ordinary S03 install outside the source tree using an isolated interpreter."""

import subprocess
import sys
import tempfile

probe = """
from pathlib import Path
import sys
import pandas as pd
import neurocvguard
from neurocvguard.checks.cohort import check_cohort
from neurocvguard.config import ColumnMap
from neurocvguard.models import Cohort
from neurocvguard.rules import COHORT_RULES
assert Path(neurocvguard.__file__).is_relative_to(sys.prefix)
data = pd.DataFrame({'observation_id': ['o1', 'o2', 'o3'],
                     'subject_id': ['p1', 'p1', 'p2'],
                     'diagnosis': ['C1', 'C1', 'C2']})
features = pd.DataFrame({'observation_id': ['o1', 'o2', 'o3'], 'f': [1., 2., 1.]})
cohort = Cohort(data, features, ColumnMap(), ('o1', 'o2', 'o3'))
result = check_cohort(cohort, ('f',))
assert (result.inventory.n_observations, result.inventory.n_participants) == (3, 2)
assert len(result.components.components) == 2
assert result.feature_equality.groups[0].observation_ids == ('o1', 'o3')
assert len(COHORT_RULES) == 6
equality = next(check for check in result.checks if check.rule_id == 'NCG-COHORT-004')
assert 'heuristic' in equality.to_dict()['message']
result.inventory.require_constant_target()
result.components.require_complete()
print('PASS: ordinary installed S03 inventory, components, equality, guards and public wording')
"""
with tempfile.TemporaryDirectory(prefix="neurocvguard-s03-") as directory:
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    print(result.stdout.strip())
