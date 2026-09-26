"""Apply the user-approved ADR-S10-001 schema extension to both local copies."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
path = root / "contracts/evaluation-result.schema.json"
schema = json.loads(path.read_text())
assert "actual_plan" not in schema["properties"]
plan = json.loads((root / "contracts/split-plan.schema.json").read_text())
for field in ("$id", "$schema", "title"):
    plan.pop(field, None)
schema["properties"]["plan_digest"] = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
schema["properties"]["actual_plan"] = plan
schema["dependentRequired"] = {"plan_digest": ["actual_plan"], "actual_plan": ["plan_digest"]}
text = json.dumps(schema, indent=2) + "\n"
path.write_text(text, encoding="utf-8")
(root / "src/neurocvguard/schemas/evaluation-result.schema.json").write_text(text, encoding="utf-8")
print("Applied approved optional plan_digest/actual_plan extension to both schema copies.")
