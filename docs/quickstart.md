# Getting started

Run from an installed environment in a directory you control. Use a fresh output
directory. All inputs in this walkthrough are explicitly fictitious.

```text
python -m neurocvguard demo --out local_outputs/demo
```

Open `local_outputs/demo/report.html` locally. Read the objective, incomplete
coverage and limitations before interpreting metrics. Repeated visits alone are
not leakage. Unknown upstream preprocessing remains unassessable even when every
controlled Pipeline fit is correct. This is a research baseline, not clinical use.

The following uses the generated tables and explicit configuration:

```text
python -m neurocvguard init --out local_outputs/starter.json
python -m neurocvguard validate --cohort local_outputs/demo/cohort.tsv --features local_outputs/demo/features.tsv --config local_outputs/demo/config.json
python -m neurocvguard audit --cohort local_outputs/demo/cohort.tsv --features local_outputs/demo/features.tsv --config local_outputs/demo/config.json --out local_outputs/audit
python -m neurocvguard split --cohort local_outputs/demo/cohort.tsv --config local_outputs/demo/config.json --out local_outputs/splits
python -m neurocvguard evaluate --cohort local_outputs/demo/cohort.tsv --features local_outputs/demo/features.tsv --config local_outputs/demo/config.json --splits local_outputs/splits/plan.json --out local_outputs/evaluation
python -m neurocvguard compare --result demo=local_outputs/demo/participant.evaluation.private.json --result rerun=local_outputs/evaluation/evaluation.private.json --out local_outputs/comparison
python -m neurocvguard report --input local_outputs/evaluation/report.json --out local_outputs/rendered
```

The starter is an editable example, not a detected mapping. For your own data,
edit its roles and explicit feature list before use. Comparing the same design
here demonstrates file handling only; it is not independent validation.
`plan.json`, `assignments.tsv`, configs and `evaluation.private.json` are sensitive
operational files. Keep them separate from projected `report.json`/`report.html`.
Projection suppresses some information but does not guarantee anonymity.

See [inputs](input_tables.md), [configuration](configuration.md), [CLI exits](cli.md),
and [warning actions](objectives.md). Freeze the evaluation plan before inspecting
final-test performance and document any amendments.
