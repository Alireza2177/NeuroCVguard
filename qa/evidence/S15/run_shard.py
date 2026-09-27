"""Run one disjoint slice of the entire suite with a separate coverage data file."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
index = int(sys.argv[1])
manifest = json.loads(Path(__file__).with_name("shards.json").read_text())
files = manifest[str(index)]
data_dir = ROOT / ".coverage-s15" / str(index)
data_dir.mkdir(parents=True, exist_ok=True)
command = [
    sys.executable,
    "-m",
    "pytest",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--cov=neurocvguard",
    "--cov-branch",
    "--cov-report=",
    f"--junitxml=qa/evidence/S15/verified-{index}.xml",
    *files,
]
print(
    json.dumps(
        {"command": ["<ENV_PYTHON>", *command[1:]], "COVERAGE_FILE": f".coverage-s15/{index}/data"}
    ),
    flush=True,
)
result = subprocess.run(
    command, cwd=ROOT, env=dict(os.environ, COVERAGE_FILE=str(data_dir / "data"))
)
raise SystemExit(result.returncode)
