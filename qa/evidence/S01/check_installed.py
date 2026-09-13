"""Verify ordinary installed S01 resources in an isolated process outside the source tree."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
expected = {
    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
    for path in (root / "contracts").glob("*.schema.json")
}
probe = """
import hashlib
import json
from pathlib import Path
import sys
from importlib.resources import files
import neurocvguard
from neurocvguard.config import AuditConfig
from neurocvguard.models import MetricValue
from neurocvguard.schema import SCHEMA_NAMES, load_schema, validate_document
from neurocvguard.serialization import canonical_json

assert Path(neurocvguard.__file__).is_relative_to(sys.prefix)
expected = json.loads(sys.argv[1])
for name in SCHEMA_NAMES:
    filename = name + '.schema.json'
    data = files('neurocvguard').joinpath('schemas', filename).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected[filename]
    assert load_schema(name)
config = AuditConfig()
validate_document('config', config.to_dict())
assert config.evaluation.positive_class is None
assert config.limits.max_input_mb == 128
expected_metric = '{"n":0,"reason":"undefined","value":null}'
assert canonical_json(MetricValue(None, 'undefined', 0).to_dict()) == expected_metric
print('PASS: installed S01 models/configuration and all six byte-identical packaged schemas')
"""
with tempfile.TemporaryDirectory(prefix="neurocvguard-s01-") as directory:
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe, json.dumps(expected)],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    print(result.stdout.strip())
