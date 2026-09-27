"""Run the nine new archive-oracle tests after the complete baseline matrix."""

import os
import shutil

from linux_matrix import BASE, EVIDENCE, ROOT, SOURCE, run

for name in ("tools/audit_distributions.py", "tests/test_distribution_audit.py"):
    shutil.copyfile(ROOT / name, SOURCE / name)
for version in ("311", "312", "313"):
    name = "linux-" + version + "-packaging"
    run(
        name,
        [
            BASE / ("linux-" + version) / "bin/python",
            "-m",
            "pytest",
            "-q",
            "--strict-markers",
            "--strict-config",
            "tests/test_distribution_audit.py",
            f"--junitxml={EVIDENCE / (name + '.xml')}",
        ],
        SOURCE,
        dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"),
    )
