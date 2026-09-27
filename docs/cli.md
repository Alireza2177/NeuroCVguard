# Local audit commands

The CLI provides `init`, `validate`, `audit`, `split`, `report`, `evaluate`,
`compare` and `demo`. These commands use the same APIs as Python
callers. All input is local and commands download nothing. `evaluate` and the
synthetic `demo` perform controlled model fitting.

After installing the package, use `neurocvguard` or `python -m neurocvguard`
interchangeably. Each command has `--help`. With no command, help is printed and
exit code 2 requests a subcommand. `--version` returns the local package version.

## Configure your own columns

```text
neurocvguard init --out config.json
```

Edit this strict JSON starter before use. `columns.observation_id` names a unique
string key; `columns.subject_id` names a stable participant identity. For example,
map `columns.target` to `diagnosis` if that is your target column. Optional role
columns may remain absent, with incomplete coverage reported. Set
`evaluation.feature_columns` explicitly before supplying a feature table.
The starter does not detect columns or infer a study objective. Consult
[input tables](input_tables.md) and [configuration](contracts.md).

## Fixture walkthrough

From the repository root, after installation, these commands use only the supplied
fictitious fixture. Choose a fresh output directory; existing files are protected.

```text
neurocvguard validate --cohort fixtures/cohort_clean.tsv --config fixtures/config.json
neurocvguard audit --cohort fixtures/cohort_clean.tsv --features fixtures/features_shuffled.tsv --config fixtures/config.json --out local_outputs/cohort-audit
neurocvguard split --cohort fixtures/cohort_clean.tsv --config fixtures/config.json --out local_outputs/splits
neurocvguard audit --cohort fixtures/cohort_clean.tsv --config fixtures/config.json --splits local_outputs/splits/plan.json --out local_outputs/split-audit
neurocvguard report --input local_outputs/split-audit/report.json --out local_outputs/rendered
```

`validate` checks local inputs and summarizes scoped findings without writing by
default. Add `--out directory` to retain its report. `audit` requires an output
directory and writes `report.json`, self-contained `report.html` and
`report.manifest.json`. Optional `--ledger ledger.json` adds strict preprocessing
declarations. Declarations remain unverified; every scope and persistent unknown
upstream finding is retained. A successful command is not scientific certification.

`split` writes **sensitive** `plan.json`, `assignments.tsv`, a sensitivity README
and separate generation diagnostics. These contain operational observation IDs;
the CLI warns before export. Protect them locally. Changing targets or infeasible
protected components cause refusal, with no seed hunting or row dropping.

`report` only renders already exported JSON. It accepts schema 1.0 audit reports
(including exported evaluation reports) or a comparison summary accompanied by
its sibling `report.manifest.json` identifying `comparison-summary` version 1.0.
Private evaluation records are not report inputs. Redacted information cannot be
recovered. Rendering does not fit, audit or recalculate statistics.

## Exit status and output

| Code | Meaning |
|---|---|
| 0 | Completed; the configured findings threshold was not crossed |
| 1 | Unexpected internal failure |
| 2 | Invocation, configuration, structural input or output error |
| 3 | Findings crossed the threshold, or the requested design was infeasible |
| 4 | Expected evaluation/runtime failure after fitting begins; incomplete results retained |

For `validate` and `audit`, `--fail-on error` is the default. It returns 3 for an
error-severity `fail` or `not_assessable` check. `--fail-on warning` also includes
warning-severity outcomes, including unknown upstream preprocessing. `--fail-on
none` changes only the exit policy after successful execution; malformed inputs
still return 2. Findings and privacy decisions are identical under every policy.
Requested reports are written before threshold exit 3. Without `validate --out`,
the findings are summarized on stdout before deciding the status.

Progress and warnings go to stderr. Stdout contains a concise summary and artifact
basenames within the requested output location, avoiding absolute private paths.
No row tables or JSON payloads are printed. Error messages suggest contract checks
without echoing input values. Place `--debug` before the command for sanitized
stack locations on unexpected failures; exception values, locals and source text
are omitted. Review any diagnostics before sharing them.

Reports use `report.small_cell_threshold` from the audit configuration. The default
is 5. `--sensitive-details` explicitly enables sensitive local report output;
`report.sensitive_details: true` also enables it for config-driven commands. The
CLI warns and the HTML visibly marks sensitive output. A report input's provenance
alone never enables sensitive rerendering. Existing outputs require a new location
or explicit `--overwrite`, which affects only the named artifacts.

The lower-level `neurocvguard.workflows.audit_workflow` combines the existing audit
APIs without discarding duplicate scopes. For matching configured Python output,
use `neurocvguard.reporting.write_configured_report`; the small root `write_report`
API retains its default threshold. No API reads implicit project configuration.

## Fixed-C or nested evaluation

Use `evaluate --cohort cohort.tsv --features features.tsv --splits plan.json
--config config.json --out local_outputs/evaluation`. The feature table and
complete single-repeat CV plan are required. The command checks all prerequisites
before any fit and writes sensitive `evaluation.private.json` plus projected
reports. It accepts `--overwrite` and `--sensitive-details`. It does not accept
`--fail-on`; incomplete fitting returns 4 regardless of findings severity.
See [evaluation](evaluation.md) for training boundaries, weights, exact metrics,
failure policy and schema migration. Nested tuning supports `evaluation.tune=true` with the
explicit C grid and inner fold count. Supplied inner assignments are used or
derived from outer training only; infeasible tuning has no fixed-C fallback.

## Compare existing private evaluations

```text
neurocvguard compare --result A=local_outputs/a/evaluation.private.json --result B=local_outputs/b/evaluation.private.json --out local_outputs/comparison
```

Repeat `--result NAME=PATH` for at least two unique names. This command loads strict
private JSON, computes signed A-minus-B differences and writes projected JSON,
HTML and a version manifest without fitting. Public reports cannot replace the
private records. Incomplete or incomparable designs remain visible with null
differences and reasons. Exit 0 means the comparison was produced, even when
differences are null; malformed records or output conflicts return 2.

`compare` uses the default public small-cell threshold of 5 and has no implicit
configuration. It accepts `--overwrite` and explicit `--sensitive-details`.
Names become public aliases. See [comparison](comparison.md) for context fields,
privacy, interpretation and the diagnostic-only evaluation flag.

## Offline synthetic demo

```text
neurocvguard demo --out local_outputs/demo
neurocvguard demo --scenario repeated --out local_outputs/repeated
neurocvguard demo --scenario site_shift --out local_outputs/site-shift
```

The default is `clean`, a participant-disjoint workflow with two observations per
person. Every scenario generates its own explicitly fictitious local input;
there is no dataset path option, network access or account. The repeated scenario
explicitly requests the invalid row-random diagnostic and retains its warning.
Site-held-out evaluation changes the target distribution and objective.

The output directory contains `report.html`, its JSON/manifest, generated TSVs,
explicit configs and separate marked private plans/evaluations/provenance.
`--sensitive-details` explicitly shows complete fictitious metrics and labels with
a visible warning. Synthetic labeling never enables that option by itself.
`--overwrite` permits replacement of named artifacts only; unrelated files remain.
Exit 4 retains an incomplete result after expected fit failures; no fallback occurs.
See [the synthetic guide](synthetic_examples.md) for all parameters and scripts.
