# Research baseline and nested regularization selection

`evaluate_baseline` runs one explicitly planned complete cross-validation repeat.
It supports constant participant targets with two or more string classes. It
protects participant/component boundaries and objective-specific domain boundaries.
It refuses holdout-only plans, multiple repeats, unknown protected relationships,
missing training classes and overlapping protected units before fitting anything.
Targets that change across visits remain meaningful audit inputs; explicitly
curate a supported cohort before using this constant-target baseline.

## Python and CLI

This source-workspace example uses only fictitious fixtures:

```python
from neurocvguard import evaluate_baseline, load_cohort, load_config, load_split_plan

config = load_config("fixtures/config.json")
cohort = load_cohort(
    "fixtures/cohort_clean.tsv", config=config, features="fixtures/features_shuffled.tsv"
)
plan = load_split_plan("fixtures/splits_clean.json", cohort=cohort, config=config)
result = evaluate_baseline(cohort, plan, config=config)
assert result.execution_status == "completed"
assert result.pooled_metrics is not None
assert result.metric_unit == "participant"
```

The API does not write files. Export explicitly with
`neurocvguard.reporting.write_evaluation(result, config=config, output_dir="local-evaluation")`.
Root `write_report` still writes only report artifacts, never the private result.

```text
neurocvguard evaluate --cohort fixtures/cohort_clean.tsv --features fixtures/features_shuffled.tsv --splits fixtures/splits_clean.json --config fixtures/config.json --out local_outputs/evaluation
```

The equivalent module invocation starts with `python -m neurocvguard`. Inputs are
strict local JSON/CSV/TSV. Estimator pickle/joblib files, config-selected Python
modules and executable transformations are unsupported.

## Fitting boundaries

Every outer fold receives a fresh sklearn Pipeline clone containing:

1. `SimpleImputer(strategy="median", keep_empty_features=True)`.
2. `StandardScaler()`.
3. `LogisticRegression(C=config.evaluation.C, solver="lbfgs", max_iter=config.evaluation.max_iter, random_state=config.split.seed)`.

Fits use current training observations selected by explicit keys. Classifier
weights equal one divided by that participant's observation count in the current
training subset. Each participant contributes total classifier loss weight one.
**Imputation and scaling use training-observation statistics**, not participant
weights. No global imputation, feature selection, class weighting, calibration or
threshold optimization occurs.

An entirely missing training feature is retained and filled with zero by the
prescribed imputer. NCG-EVAL-004 records that it provided no training information.
Held-out values never determine imputation, scaling or weights. Fit events record
actual calls, IDs, C and outcomes. A rejected boundary creates no fictional fit
event. Prediction can fail after a completed fit; fold and fit statuses remain
distinct. No fitted estimator is saved.

With `tune=false`, the runner fits only the outer models at the configured fixed C.
The evaluator permits only the explicitly enabled outer participant-overlap diagnostic
described in [comparison](comparison.md). All original audit failures remain;
these runs are invalid evidence for unseen-participant generalization.

## Nested regularization selection

Set `evaluation.tune=true`, an explicit positive `C_grid`, and `inner_splits`
in your local configuration. For the Python example above, enable tuning before
calling `evaluate_baseline`:

```python
from dataclasses import replace

config = replace(
    config,
    evaluation=replace(config.evaluation, tune=True, C_grid=(0.1, 1.0, 10.0), inner_splits=3),
)
result = evaluate_baseline(cohort, plan, config=config)
assert all(fold.selected_C is not None for fold in result.folds)
```

Valid supplied inner folds are retained. For each outer fold without them, the
runner generates participant/component-disjoint inner folds from **outer training
only**, using the same participant-level StratifiedGroupKFold construction as
`subject_kfold`, the configured seed and inner fold count. The standalone split
command still generates outer plans with `tune=false`; enable tuning for evaluation.
All memberships and training-class support are checked before any fitting.
Infeasible group counts or invalid supplied inner assignments fail explicitly;
the runner never changes the seed, fold count or assignments to repair them.

The inner objective is unseen participants, including when the outer objective
holds out sites or phases. Inner folds protect declared transitive dependence
components but do not claim unseen-site/phase evaluation. Outer domain separation
still applies. A derived private `actual_plan` retains the exact inner memberships
and its digest; the supplied plan is not modified. Outer origin/scheme/seed remain
those of the supplied plan; generated inner memberships use the evaluation
configuration seed recorded in result provenance. No new schema fields are used.

Every sorted C uses the same inner memberships and fresh pipeline clones. Inner
validation probabilities are averaged per participant, then pooled across all
outer-training participants to compute balanced accuracy. Selection does not use
an average of fold scores or weight participants by their visit counts.

Scores within `1e-12` of the maximum are tied; the smallest numeric C wins.
Private `candidate_scores`, `selected_C` and the recorded selection policy retain
the scores and tie resolution. Every candidate is evaluated, including when a
different candidate fails. Any required inner fit/prediction failure makes that
candidate score null with a reason and prevents selection/refitting for that outer
fold, even if other candidates succeeded. No default-C fallback occurs. Other
outer folds remain visible, but complete pooled metrics are withheld.

After successful selection, a fresh pipeline fits all and only outer training at
the selected C, then predicts the untouched outer test observations. Neither outer
test labels nor scores determine C. Controlled runtime events include each inner
candidate's C, inner-fold reference, actual fit IDs and completion/failure status.
The public projection omits candidate scores and identity-bearing memberships.

## Participant metrics

Average each participant's held-out probability vectors arithmetically, then pick
the largest mean. This is not majority voting across observations. Ties select the
first class in the recorded lexically sorted class order. The runner independently
requires exactly one out-of-fold participant prediction per ordinary complete run.
In the narrow diagnostic exception, each observation must occur in exactly one
outer test fold. Pool all raw held-out observation probabilities across folds
before taking one mean per participant; never average fold means with unequal
visit counts. This aggregation does not remove training leakage.

Accuracy is defined for any nonempty scored set. Balanced accuracy averages recall
across the entire declared class set; macro-F1 uses that same class set. Both are
null when a true class is absent, with reason `missing_true_class`. A supported
class never predicted has real F1/recall zero. Per-class support and confusion
matrices use the recorded class order and participant denominator.

Binary ROC-AUC requires explicit `evaluation.positive_class`. Without it AUC is
null with `positive_class_unspecified`; other supported metrics still compute.
With a specified positive class, absent true classes give `missing_true_class`.
Multiclass AUC is macro one-vs-rest and requires all classes. An empty scored set
uses `empty_scored_set`. Metric records retain value, reason and denominator;
undefined values never become NaN or substituted zero.

Feature, probability and confusion matrix allocations are checked against the
configured dense-memory guardrail. This is not a bound on total process memory.

Pooled scores use all participant out-of-fold predictions, not a fold-score
average. Convergence warnings fail the affected fit; iteration limits never change
automatically. Expected numeric/fit errors retain a fixed sanitized reason. Any
failed outer fold makes the run incomplete and pooled metrics null. Other folds
and diagnostics remain visible. Unexpected defects propagate to the CLI's
sanitized internal-error handling. No inferential CI or p-value is produced.

## Outputs and privacy

The CLI warns before writing `evaluation.private.json`, which retains complete
metrics, integrity digests, actual memberships and fit IDs. It also writes
`README.SENSITIVE.txt`. Protect these private records; they are not public-sharing
artifacts. No separate participant prediction table is written by default.

`report.json`, `report.html` and the report manifest are separately projected.
The manifest describes that report pair, not the private record beside it.
Its report coverage remains partial when upstream checks are unassessable, even
when `evaluation_summary.execution_status` correctly says completed.
If a confusion matrix has a positive cell below `report.small_cell_threshold`,
its whole public MetricSet is suppressed with `privacy_small_cells`; the private
record retains the result. Privacy suppression is different from mathematical
undefinedness. Explicit `--sensitive-details` or configuration can enable visibly
marked detailed reports. Existing files require a fresh destination or explicit
`--overwrite`. All evaluation exports share one staged write/rollback boundary.

Preflight checks retain role coverage and upstream limitations. NCG-COHORT-001
carries prerequisite `input_summary` in private evidence so reloaded evaluations
retain that coverage. Controlled fits cannot authenticate earlier preprocessing;
a Pipeline cannot repair earlier global learning. Freeze your evaluation plan
before using test results to redesign it. This is a research baseline, not a
clinical system.

Exit 0 means completed evaluation, not scientific certification. Exit 2 means
malformed inputs/output conflicts; exit 3 means an infeasible/unsupported design;
exit 4 means expected runtime failure with an incomplete record. Internal defects
use exit 1. A detected internal boundary defect retains an incomplete record;
an unexpected exception may prevent any result from being produced.

## Private schema migration

{download}`ADR-S10-001 <../state/decisions/ADR-S10-001-evaluation-plan.md>` adds paired
optional `plan_digest` and `actual_plan` fields to the private schema. The runner always
populates them. The digest covers canonical operational plan JSON; validation
checks digest, objective, cohort, fold references and fit boundaries. Public
reports omit both fields.

Updated readers accept old schema 1.0 records without those fields and leave them
absent. Older closed-schema readers reject extended records: update the reader.
Never fabricate memberships when migrating an old record. This extension does
not enable diagnostic overlap evaluation or make private records safe to publish.
Nested tuning uses the same fields to retain inner-fold memberships.
