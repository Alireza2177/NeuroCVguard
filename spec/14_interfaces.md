# 14 — Public Python API and command-line interface

## 14.1 Public API boundary

Expose a small intentional surface from neurocvguard: load_config, load_cohort, load_split_plan, audit_cohort, audit_splits, make_splits, evaluate_baseline, compare_designs, write_report, and the documented records/exceptions. Additional lower-level functions may remain private. Use keyword-only optional parameters.

The exact signatures to implement are:

```python
load_config(path: str | Path) -> AuditConfig
load_cohort(metadata: str | Path | pd.DataFrame, *, config: AuditConfig,
            features: str | Path | pd.DataFrame | None = None) -> Cohort
load_split_plan(source: str | Path | dict, *, cohort: Cohort,
                config: AuditConfig) -> SplitPlan
audit_cohort(cohort: Cohort, *, config: AuditConfig,
             ledger: dict | None = None) -> AuditReport
audit_splits(cohort: Cohort, plan: SplitPlan, *,
             config: AuditConfig) -> AuditReport
make_splits(cohort: Cohort, *, config: AuditConfig) -> SplitPlan
evaluate_baseline(cohort: Cohort, plan: SplitPlan, *,
                  config: AuditConfig) -> EvaluationResult
compare_designs(results: dict[str, EvaluationResult]) -> ComparisonResult
write_report(result: AuditReport | EvaluationResult | ComparisonResult, *,
             output_dir: str | Path, sensitive_details: bool = False,
             overwrite: bool = False) -> dict[str, Path]
```

Normalize format handling once in I/O. A record's `.to_dict(sensitive_details=False)` must apply the same projection as write_report. A `.summary()` convenience returns a concise string rather than printing unconditionally. SplitPlan's `.write(output_dir, overwrite=False)` creates sensitive plan.json and assignments.tsv and documents that fact.

Combine cohort/split/provenance checks in the CLI's audit orchestration without discarding duplicate scopes. An evaluation result includes its prerequisite audit summary. The core API must not read global project paths or mutate config.

## 14.2 CLI commands

Use argparse and expose both `neurocvguard` and `python -m neurocvguard` with identical behavior. Require subcommands; no command displays help with an actionable return. Support `--version` and `--help`. Global `--debug` is placed before the subcommand. Each subcommand has purpose, required inputs, examples, output semantics and caveats in help.

| Command | Purpose | Core options |
|---|---|---|
| `init` | Write an editable strict JSON configuration | `--out config.json`, optional `--overwrite` |
| `validate` | Structural/semantic local input validation | `--cohort`, `--config`, optional `--features`, `--splits` |
| `audit` | Inventory + optional partition/provenance audit | `--cohort`, `--config`, `--out`, optional `--features`, `--splits`, `--ledger` |
| `split` | Generate and independently check a plan | `--cohort`, `--config`, `--out` |
| `evaluate` | Run the controlled baseline | `--cohort`, `--features`, `--splits`, `--config`, `--out` |
| `compare` | Compare local evaluation JSON results | repeated `--result name=path`, `--out` |
| `report` | Render a compatible exported JSON report | `--input`, `--out` |
| `demo` | Run a packaged fully synthetic workflow | `--out`, optional `--scenario clean|repeated|site_shift` |

Commands that write reports accept `--overwrite` and `--sensitive-details`. The flag overrides report.sensitive_details upward only by explicit user choice. Default remains false. `init` writes a documented starter schema without claiming it knows the user's columns. `demo` never downloads data.

For validate/audit, `--fail-on none|warning|error` defaults to error and controls the exit status after a report is successfully written. It does not change the findings. Report privacy settings never change audit decisions.

## 14.3 Exit codes and streams

0 = command completed and the configured audit threshold was not crossed. 1 = unexpected internal failure. 2 = invocation/configuration/structural input error. 3 = requested operation completed but findings crossed fail-on, or a validly described design is infeasible for planning/evaluation. 4 = expected evaluation/runtime failure after fitting began. Do not call sys.exit inside library functions.

Warnings and progress use stderr; a compact final summary and artifact paths use stdout. Do not flood terminals with entire tables. JSON artifacts are written to files, not mixed with logs on stdout. Debug may add tracebacks but must not dump row contents. Common failures should propose a concrete repair.

## 14.4 End-to-end command contract

These commands are future implementation acceptance commands, not a claim they work before Codex builds the package:

```bash
python -m pip install -e ".[dev,docs]"
neurocvguard demo --out ./demo-output
neurocvguard validate --cohort ./cohort.tsv --config ./config.json
neurocvguard audit --cohort ./cohort.tsv --config ./config.json --out ./audit-output
neurocvguard split --cohort ./cohort.tsv --config ./config.json --out ./split-output
neurocvguard evaluate --cohort ./cohort.tsv --features ./features.tsv --splits ./split-output/plan.json --config ./config.json --out ./evaluation-output
```

Paths are examples, not hard-coded defaults. Every command must be exercised in a temporary directory in integration tests. Demo must also pass from a clean installed wheel outside the repository. Copyable examples should work on Windows and POSIX; use Path and avoid shell-specific assumptions in Python code.

## 14.5 User friendliness without a GUI

A simple terminal workflow plus a readable offline HTML report is the first-release user interface. It is normal for research tools to offer a library and CLI; the project does not need a web app to be usable. Prioritize clear mapping examples, common-error messages, complete examples, fast demo, and honest limitations. A later GUI is considered only after real user feedback shows a concrete need.
