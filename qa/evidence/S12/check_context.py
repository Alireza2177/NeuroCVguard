"""Verify the exact approved schema delta, compatibility and packaged parity."""

import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

root = Path(__file__).resolve().parents[3]
baseline = json.loads(Path(__file__).with_name("baseline.json").read_text())
removed = 0


def without_context(node):
    global removed
    if isinstance(node, dict):
        if {"designs", "differences", "interpretation"} <= set(node.get("properties", {})):
            removed += 1
            properties = node["properties"]["designs"]["items"]["properties"]
            assert properties.pop("context")["additionalProperties"] is False
        for value in node.values():
            without_context(value)
    elif isinstance(node, list):
        for value in node:
            without_context(value)


for name in ("comparison-summary", "audit-report"):
    relative = f"contracts/{name}.schema.json"
    old = json.loads(
        subprocess.check_output(
            ["git", "show", f"{baseline['git_head']}:{relative}"],
            cwd=root,
            text=True,
            encoding="utf-8",
        )
    )
    new = json.loads((root / relative).read_text())
    assert new == json.loads((root / f"src/neurocvguard/schemas/{name}.schema.json").read_text())
    Draft202012Validator.check_schema(new)
    without_context(new)
    assert new == old
old_comparison = json.loads(
    subprocess.check_output(
        ["git", "show", f"{baseline['git_head']}:contracts/comparison-summary.schema.json"],
        cwd=root,
        text=True,
    )
)
example = json.loads((root / "fixtures/comparison_schema_example.json").read_text())
Draft202012Validator(old_comparison).validate(example)
example["designs"][0]["n_folds"] = 3
assert list(Draft202012Validator(old_comparison).iter_errors(example))
assert removed == 2
print(
    "Exact optional-context delta verified in both normative and packaged schemas; "
    "legacy fixture remains valid; original counterexample confirmed."
)
