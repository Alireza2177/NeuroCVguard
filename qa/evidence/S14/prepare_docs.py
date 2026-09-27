"""Generate checked reference tables from the shipped contracts and public types."""

import inspect
import json
from pathlib import Path

import neurocvguard
from neurocvguard import config, errors, models

ROOT = Path(__file__).resolve().parents[3]


def configuration_reference():
    schema = json.loads((ROOT / "contracts/config.schema.json").read_text())
    defaults = config.AuditConfig().to_dict()
    lines = [
        "# Configuration reference",
        "",
        "Source: `contracts/config.schema.json` and `neurocvguard.config.AuditConfig`.",
        "Verified by `tests/test_documentation.py` and the strict config/contract tests.",
        "",
        "JSON input requires every required field. Constructor/starter defaults below",
        "are not missing-key fallbacks. Only `evaluation.positive_class` and",
        "`limits.max_input_mb` may be omitted. Unknown/duplicate keys and booleans",
        "used as numbers fail. Resource quantities in MB use 1024² bytes.",
        "",
        "| Key | Default in starter | Structural type and constraints | Required in JSON |",
        "|---|---|---|---|",
    ]
    for section, definition in schema["properties"].items():
        entries = definition.get("properties", {"": definition})
        for key, rules in entries.items():
            name = f"{section}.{key}" if key else section
            default = defaults[section][key] if key else defaults[section]
            required = key in definition.get("required", []) if key else True
            lines.append(
                f"| `{name}` | `{json.dumps(default)}` | `{json.dumps(rules)}` | {required} |"
            )
    lines += [
        "",
        "## Meaning and semantic constraints",
        "",
        "`schema_version` is the string 1.0. `columns` maps actual input names:",
        "observation/participant IDs are mandatory; null optional roles mean absent.",
        "Scalar roles must differ. Independence columns connect participants by",
        "transitive equality within each field; categorical covariates feed descriptive",
        "association diagnostics. Feature names must be explicit and exclude every role,",
        "protected field and covariate. Empty features are allowed for inventory only.",
        "",
        "`study.objective` specifies the generalization claim. `split.scheme` must match",
        "that objective except under audit_only; imported plans are independently checked.",
        "`n_splits` must be an integer for subject_kfold and null otherwise. The seed is",
        "fixed explicitly, never searched. See [objectives](objectives.md).",
        "",
        "`association.review_threshold` flags descriptive Cramer's V for review; it is",
        "not a causal threshold. `min_cell_count` flags sparse observed/expected tables.",
        "",
        "`evaluation.C` is fixed inverse regularization strength when tune=false.",
        "With tune=true, C_grid candidates use participant-aware inner_splits and",
        "balanced accuracy; max_iter bounds logistic fitting. Positive_class explicitly",
        "defines binary AUC; null leaves binary AUC undefined. Diagnostic subject overlap",
        "is narrowly limited to imported unseen-participant plans without protected",
        "relationships or tuning; it never waives observation overlap or domain rules.",
        "See [evaluation](evaluation.md) and [comparison](comparison.md).",
        "",
        "`report.sensitive_details` explicitly enables sensitive local reporting.",
        "`small_cell_threshold` suppresses public cells/linked metric sets; it never",
        "changes scientific calculations. The root write_report API uses its own explicit",
        "sensitive_details argument and default threshold; see [reporting](reporting.md).",
        "",
        "`limits.max_rows` bounds observations; max_features bounds selected predictors;",
        "max_dense_mb bounds estimated float64 rows × features storage before allocation;",
        "max_input_mb bounds each file before parsing. These are guardrails, not an upper",
        "bound on total process memory. Limits never authorize silently truncating data.",
        "",
    ]
    return "\n".join(lines)


def api_reference():
    lines = [
        "Python API",
        "==========",
        "",
        "The root API below is intentional. Use keyword-only options. Calls do not",
        "read implicit project configuration. See contracts for serialization/privacy",
        "and the linked workflow guides for prerequisites and failure policies.",
        "",
    ]
    inventory = {}
    for module in (neurocvguard, config, models, errors):
        names = [
            name
            for name, value in vars(module).items()
            if not name.startswith("_")
            and (inspect.isclass(value) or inspect.isfunction(value))
            and value.__module__ == module.__name__
        ]
        inventory[module.__name__] = names
        lines += [module.__name__, "-" * len(module.__name__), ""]
        for name in names:
            value = getattr(module, name)
            directive = "autoclass" if inspect.isclass(value) else "autofunction"
            lines += [f".. {directive}:: {module.__name__}.{name}", ""]
    lines += [
        "Records inherit from_dict/from_json for strict schema parsing where applicable.",
        "to_dict returns a detached public projection for reports/results. SplitPlan and",
        "PreprocessingLedger require to_operational_dict; EvaluationResult offers both.",
        "SplitPlan.write writes sensitive plan.json/assignments.tsv with no overwrite",
        "unless requested. summary returns text. Cohort properties return copies.",
        "",
        "Implementation helpers outside this inventory are not a stability promise.",
        "The documented synthetic interface is in the synthetic guide; lower-level",
        "helpers mentioned by methodological guides retain their stated boundaries.",
        "",
    ]
    return "\n".join(lines), inventory


def main():
    (ROOT / "docs/configuration.md").write_text(configuration_reference(), encoding="utf-8")
    api, inventory = api_reference()
    (ROOT / "docs/api.rst").write_text(api, encoding="utf-8")
    (ROOT / "qa/evidence/S14/api_inventory.json").write_text(
        json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
    )
    rules = json.loads((ROOT / "qa/rule_catalog.json").read_text())
    lines = [
        "# Rule catalog",
        "",
        "Stable IDs from the rule register; checked against the register in documentation tests.",
        "Severity applies when triggered; status and evidence kind remain distinct.",
        "Read [warning actions](objectives.md) and [limitations](limitations.md).",
        "",
        "| Rule | Finding | Severity / evidence | Meaning |",
        "|---|---|---|---|",
    ]
    for rule in rules:
        lines.append(
            f"| `{rule['id']}` | {rule['name']} | {rule['trigger_severity']} / "
            f"{rule['evidence_kind']} | {rule['meaning']} |"
        )
    (ROOT / "docs/rules.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
