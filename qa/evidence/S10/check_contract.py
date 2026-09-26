"""Check only the approved schema migration, not the legacy foundation-state gate."""

import copy
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

root = Path(__file__).resolve().parents[3]
schema = json.loads((root / "contracts/evaluation-result.schema.json").read_text())
installed = json.loads(
    (root / "src/neurocvguard/schemas/evaluation-result.schema.json").read_text()
)
assert schema == installed
Draft202012Validator.check_schema(schema)
baseline = json.loads(Path(__file__).with_name("baseline.json").read_text())
old = json.loads(
    subprocess.check_output(
        ["git", "show", baseline["git_head"] + ":contracts/evaluation-result.schema.json"],
        cwd=root,
        text=True,
    )
)
legacy = json.loads((root / "fixtures/evaluation_schema_example.json").read_text())
assert Draft202012Validator(old).is_valid(legacy)
assert Draft202012Validator(schema).is_valid(legacy)
counterexample = copy.deepcopy(legacy)
counterexample["plan_digest"] = "0" * 64
errors = list(Draft202012Validator(old).iter_errors(counterexample))
assert any(error.validator == "additionalProperties" for error in errors)
assert set(schema["properties"]) - set(old["properties"]) == {"plan_digest", "actual_plan"}
reduced = copy.deepcopy(schema)
for key in ("plan_digest", "actual_plan"):
    reduced["properties"].pop(key)
reduced.pop("dependentRequired")
assert reduced == old
plan = json.loads((root / "contracts/split-plan.schema.json").read_text())
for key in ("$id", "$schema", "title"):
    plan.pop(key, None)
assert schema["properties"]["actual_plan"] == plan
print(
    "Approved schema delta only; legacy fixture preserved; "
    "original additionalProperties conflict reproduced; "
    "embedded plan exact; packaged schema equal."
)
