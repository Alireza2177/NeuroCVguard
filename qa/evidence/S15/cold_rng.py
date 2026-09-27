"""Reproduce cold dependency initialization separately from scientific computation."""

import json
import random
import traceback
from importlib.metadata import version
from pathlib import Path

import numpy as np

from neurocvguard import load_cohort, make_splits
from neurocvguard.config import AuditConfig

config = AuditConfig()
cohort = load_cohort("fixtures/cohort_clean.tsv", config=config)
original_getrandbits = random.getrandbits
calls = []


def traced(*args, **kwargs):
    calls.append(
        [
            str(frame.filename).replace(str(Path.home()), "<USER_HOME>") + ":" + str(frame.lineno)
            for frame in traceback.extract_stack()
        ]
    )
    return original_getrandbits(*args, **kwargs)


random.getrandbits = traced
before, before_numpy = random.getstate(), np.random.get_state()
first = make_splits(cohort, config=config)
after, after_numpy = random.getstate(), np.random.get_state()
second = make_splits(cohort, config=config)
random.getrandbits = original_getrandbits
print(
    json.dumps(
        {
            "python_random_changed_on_first_call": before != after,
            "python_random_unchanged_on_second_call": after == random.getstate(),
            "numpy_unchanged": before_numpy[0] == after_numpy[0]
            and np.array_equal(before_numpy[1], after_numpy[1])
            and before_numpy[2:] == after_numpy[2:],
            "identical_plans": first == second,
            "versions": {name: version(name) for name in ("scikit-learn", "rich")},
            "getrandbits_import_stacks": calls,
        },
        indent=2,
    )
)
