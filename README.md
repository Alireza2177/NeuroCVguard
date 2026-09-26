# NeuroCVguard

Research-only Python software under development. **S01 provides typed records,
strict configuration and serialization; S03 adds in-memory cohort checks;
S04 adds supplied split audits; S05 adds deterministic outer plan generation
and sensitive assignment exports; S06 adds participant-level categorical
association diagnostics with explicit support counts and descriptive warnings;
S07 adds preprocessing declarations and fit-boundary validation;
S08 adds privacy-projected JSON and offline HTML reports;
S09 exposes init, validate, audit, split and report commands;
S10 adds fixed-C participant classification through evaluate;
S11 adds nested participant-aware C selection.**
See [the CLI guide](docs/cli.md) for a complete local workflow. The local development version
is `0.1.0`, matching the foundation's target release; it is not a published or
completed release.

S02 now provides strict local CSV/TSV loading and keyed feature joins through
`load_cohort`; see [the input guide](docs/input_tables.md). It was completed as the
explicitly authorized prerequisite for S09 after initially being skipped.
Diagnostic overlap evaluation, comparison computation and the
synthetic demo remain unimplemented. The intended research scope is defined in [START_HERE.md](START_HERE.md)
and [spec/00_project_charter.md](spec/00_project_charter.md). This software does
not provide clinical advice or certify scientific validity.

## Local installation and use

From this source directory in PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev,docs]"
.venv/Scripts/python.exe -c "import neurocvguard; print(neurocvguard.__version__)"
.venv/Scripts/python.exe -m neurocvguard --version
.venv/Scripts/neurocvguard.exe --help
```

The version command prints `neurocvguard 0.1.0`. No activation is required.
Reuse an existing project environment only if it is appropriate; do not replace
an unrelated environment. Initial installation requires access to the declared
dependencies. Import and help/version work locally without a network connection.

For an ordinary source install, create a separate environment and run its Python
with `-m pip install .`. S00's verification uses `.venv-install` for this check.
On other systems the conventional environment interpreter path is `.venv/bin/python`;
those systems have not been verified in this run. No public package installation
or repository URL is advertised.

## Development checks

```powershell
.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe -m mypy src/neurocvguard
```

Tests require the editable developer install; no source-path injection is used.
The import test uses a fresh interpreter in an empty temporary directory with
audited file/network/process operations and blocked thread creation. Interpreter
bytecode caching is disabled for that test to distinguish package behavior from
Python's own cache writes. All data used for checks are synthetic or package metadata.

Python 3.11, 3.12, and 3.13 are the initial compatibility targets in the foundation.
Only combinations explicitly recorded in [the S00 handoff](state/handoffs/S00.md)
are tested. Exact resolved package versions, logs, and limitations are under
[qa/evidence/S00](qa/evidence/S00/). S01 verification is recorded in
[the S01 handoff](state/handoffs/S01.md) and [qa/evidence/S01](qa/evidence/S01/).
Dependency lower/upper bounds have not been
invented from a single environment; minimum-version testing is pending.
NumPy, pandas, SciPy, scikit-learn, Jinja2 and jsonschema are the prescribed
runtime dependencies. They are not eagerly imported by the package root.
The developer extra also includes pandas/jsonschema type stubs.

Ruff checks the package, tests, and stage evidence helpers. Its configuration
excludes the two unchanged foundation scripts to preserve the supplied utilities.
The standalone foundation validator checks original specification consistency
and asserts an unimplemented project state; it is not application verification.
Documentation builds and release distribution checks belong to later stages.

## License and review status

BSD-3-Clause is the **proposed** license; [LICENSE](LICENSE) records the proposal,
not a confirmed copyright grant. License adoption, copyright ownership, maintainer
identity, security contact, namespace ownership, and publication URLs require real
maintainer confirmation before release. Package license/author/URL fields are
omitted until confirmed; proposed values are under `tool.neurocvguard.release`.
No DOI, publication, CI result, or support commitment is claimed.

[AI_ASSISTANCE.md](AI_ASSISTANCE.md) records the assistance actually provided.
S11 verification and review status are recorded in [its handoff](state/handoffs/S11.md).
S12 remains unstarted; further work needs
a subsequent instruction.

## Configuration and record API

```python
from neurocvguard.config import load_config
from neurocvguard.models import MetricValue
from neurocvguard.serialization import canonical_json

config = load_config("fixtures/config.json")
assert config.limits.max_input_mb == 128
metric = MetricValue(None, "positive_class_unspecified", 12)
print(canonical_json(metric.to_dict()))
```

See [the record reference](docs/contracts.md) for fields, defaults, mutation
behavior, error types, and privacy boundaries. Constructing a validated record
does not run an audit, confirm cohort membership, or authenticate prior fitting.
`result.to_dict()` creates a public projection; `result.to_operational_dict()`
on an evaluation retains sensitive fit IDs and digests. Split plans and
preprocessing ledgers have explicitly operational serializers only.

## In-memory cohort checks

```python
from neurocvguard.checks.cohort import check_cohort

# cohort is an already validated, explicitly keyed S01 Cohort object.
result = check_cohort(cohort, ("feature_1", "feature_2"))
print(result.inventory.n_observations, result.inventory.n_participants)
public_checks = [check.to_dict() for check in result.checks]
```

The [S03 reference](docs/cohort_checks.md) includes a complete synthetic example,
field definitions, ordering and privacy boundaries. Repeats and cross-site visits
are descriptive. Feature equality never merges identities. Unknown protected
relationships and changing targets expose explicit prerequisite guards; this
does not implement or approve a split/evaluation design.

See the [S03 handoff](state/handoffs/S03.md) and [evidence](qa/evidence/S03/) for
the actual verification results. Human acceptance remains pending. S02 input
verification is recorded separately in [its handoff](state/handoffs/S02.md).

## Supplied split audit API

```python
from neurocvguard import audit_splits, load_split_plan

# cohort and config are explicitly constructed, validated in-memory inputs.
plan = load_split_plan("assignments.tsv", cohort=cohort, config=config)
report = audit_splits(cohort, plan, config=config)
public_report = report.to_dict()
```

See the [S04 reference](docs/split_audits.md) for a complete synthetic example,
strict import behavior and separate objective/complete-CV eligibility flags.
Unknown upstream preprocessing remains unassessable. A bound plan or clean split
check does not certify an experiment or compute a score. S04 includes the mapped
metadata digest necessary for binding; S02 now supplies cohort/feature ingestion.
Verification is recorded in the [S04 handoff](state/handoffs/S04.md) and
[S04 evidence](qa/evidence/S04/). S05 generation is described below.

## S05 outer plan generation

`neurocvguard.make_splits(cohort, config=config)` uses participant-level
StratifiedGroupKFold or strict site/phase LeaveOneGroupOut, then runs the independent
S04 audit. It refuses infeasible designs without changing rows, labels, seeds or
fold counts. `plan.generation_report` retains warnings, support and versions;
`plan.write(output_dir)` explicitly writes sensitive plan/assignment artifacts,
with no overwrite by default. Nested tuning is available through evaluation;
the standalone split command produces outer plans.

See the [executed API example](docs/split_generation.md),
[S05 handoff](state/handoffs/S05.md) and [verification evidence](qa/evidence/S05/).

## Acquisition/target association

See [the S06 guide](docs/association_diagnostics.md) for the executable synthetic
example, pairwise denominators, null reasons and public/sensitive evidence
boundary. These diagnostics are descriptive and do not establish causality,
model shortcut use or scientific validity.

## Preprocessing provenance

[The S07 guide](docs/preprocessing_provenance.md) provides a tested example of
`audit_cohort`, strict ledger loading, declared boundary checks and planned fit
validation. Imported history never authenticates execution. S10 now records
observed controlled fits while retaining the unknown upstream limitation.

## Offline reports

`neurocvguard.write_report(result, output_dir="local-report")` writes public
JSON, self-contained HTML and a version manifest from an existing typed audit,
evaluation or comparison record. Rendering runs no audit or statistic. Existing
files are preserved unless `overwrite=True`; sensitive detail requires an explicit
`sensitive_details=True` and a visible warning. No operational split or prediction
files are added to the report bundle.

See [the tested reporting guide](docs/reporting.md), [S08 handoff](state/handoffs/S08.md)
and [synthetic rendered example](qa/evidence/S08/rendered/public/report.html).
The [CLI guide](docs/cli.md) covers report rendering and configured privacy settings.

## Fixed-C evaluation

`neurocvguard.evaluate_baseline(cohort, plan, config=config)` uses fresh sklearn
imputer/scaler/logistic pipelines, training-only fits and participant probability
aggregation. Any failed fold prevents a complete pooled score. The `evaluate`
command writes a marked sensitive private record and separate projected reports.
See [the evaluation guide](docs/evaluation.md) for exact metric/null semantics,
copyable commands and the approved private-schema migration.
