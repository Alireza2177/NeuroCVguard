"""Apply the exact optional context extension approved in ADR-S12-001."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
properties = {
    "execution_status": {"enum": ["completed", "incomplete", "blocked"]},
    "metric_unit": {"const": "participant"},
    "cohort_reference": {"type": "string", "pattern": "^cohort-[0-9]+$"},
    "feature_reference": {"type": "string", "pattern": "^features-[0-9]+$"},
    **{
        name: {"type": "integer", "minimum": 0}
        for name in (
            "n_folds",
            "n_completed_folds",
            "n_participants",
            "n_observations",
            "n_features",
            "training_participants_min",
            "training_participants_max",
        )
    },
    "class_order": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
        "minItems": 2,
        "uniqueItems": True,
    },
    "positive_class": {"type": ["string", "null"]},
    "model": {"const": "prescribed_logistic_baseline"},
    "recorded_C_values": {
        "type": "array",
        "items": {"type": "number", "exclusiveMinimum": 0},
        "uniqueItems": True,
    },
    "tuning_recorded": {"type": "boolean"},
}
context = {
    "type": "object",
    "properties": properties,
    "required": list(properties),
    "additionalProperties": False,
}
comparison = json.loads((root / "contracts/comparison-summary.schema.json").read_text())
assert "context" not in comparison["properties"]["designs"]["items"]["properties"]
comparison["properties"]["designs"]["items"]["properties"]["context"] = context
audit = json.loads((root / "contracts/audit-report.schema.json").read_text())


def extend_embedded(node):
    if isinstance(node, dict):
        if {"designs", "differences", "interpretation"} <= set(node.get("properties", {})):
            node["properties"]["designs"]["items"]["properties"]["context"] = context
        else:
            for value in node.values():
                extend_embedded(value)
    elif isinstance(node, list):
        for value in node:
            extend_embedded(value)


extend_embedded(audit)
for directory in ("contracts", "src/neurocvguard/schemas"):
    for name, document in (("comparison-summary", comparison), ("audit-report", audit)):
        (root / directory / f"{name}.schema.json").write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8"
        )
print("Added optional closed design context to standalone and embedded schema copies.")
