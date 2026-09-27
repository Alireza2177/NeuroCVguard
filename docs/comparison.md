# Descriptive design comparison

Compare previously evaluated designs without refitting models or choosing a
scientific winner. Freeze designs before evaluating them; comparisons do not
authorize seed hunting or selecting a split because it gave a preferred score.

```python
from neurocvguard import compare_designs, write_report
from neurocvguard.comparison import load_evaluation

# These paths must contain your existing local operational evaluation records.
results = {
    "A": load_evaluation("local_outputs/a/evaluation.private.json"),
    "B": load_evaluation("local_outputs/b/evaluation.private.json"),
}
comparison = compare_designs(results)
write_report(comparison, output_dir="local_outputs/comparison")
```

The equivalent CLI is:

```text
neurocvguard compare --result A=local_outputs/a/evaluation.private.json --result B=local_outputs/b/evaluation.private.json --out local_outputs/comparison
```

Supply at least two unique names. The loader accepts bounded strict local JSON
(128 MiB default), rejects executable formats, duplicate keys and nonfinite
numbers, and validates the private format. Public reports omit identity metadata;
request the original private record rather than reconstructing digests.

## Reading differences and context

Names sort lexically. Each unordered pair shows A minus B for participant accuracy,
balanced accuracy, macro-F1 and ROC-AUC on the 0–1 scale. Negative values remain
negative. For example, hypothetical accuracy 0.60 minus 0.75 is -0.15.

Cohort/feature digests, recorded counts, feature columns and class definitions
(including positive class) must match for a numeric difference. Incomplete runs
remain visible with null differences and reasons. Undefined metrics are null.
The v1 private contract supports only participant metrics; an unsupported unit is
rejected during validation rather than paired with a participant score.

Equal input identities do not establish equal scientific estimands. Holding out
sites instead of participants can change the test distribution, training sizes and
class coverage. Differences are descriptive, not a causal amount of leakage.
Unknown upstream preprocessing stays unassessable; controlled pipelines cannot
repair earlier global fitting.

Each design displays its objective, diagnostic status, execution/fold counts,
participant/observation/feature counts, training participant range, class order,
positive class, metric unit and prescribed imputer/scaler/logistic model family.
Recorded C values and whether candidate scores exist are shown; unrecorded settings
such as max_iter require the original configuration and are never inferred.
Class support comes from pooled metrics when available.

The optional `context` schema extension is documented in
{download}`ADR-S12-001 <../state/decisions/ADR-S12-001-comparison-context.md>`. Updated readers
accept old records without context and leave it absent. Older closed-schema
readers must be updated before reading extended records. Both standalone and
embedded comparison schemas carry the same extension.

## Narrow participant-overlap diagnostic

Evaluation rejects participant overlap by default. Set
`evaluation.diagnostic_allow_subject_overlap=true` explicitly only for a
row-disjoint, complete single-repeat CV plan with objective `unseen_participant`
and no extra independence columns. Supply the row-random plan explicitly; the
normal split generator continues to make protected participant splits.

Observation overlap, unknown membership, missing training classes, incomplete CV,
multiple repeats, family dependence, site/phase objectives and invalid inner
partitions are never waived. Constant participant targets and all other evaluator
prerequisites remain required. Setting the flag for an otherwise valid ordinary
plan does not relabel it diagnostic.

For an actually permitted overlap run, original failed split checks remain,
`diagnostic_only=true`, and `valid_for_objective=false`. CLI and HTML prominently
state: **Do not report as evidence for unseen-participant generalization.**
Participant aggregation does not remove the training leakage already present.
Tuning still uses participant-disjoint inner folds restricted to outer training.

Each observation receives exactly one held-out prediction. A participant can
appear in several outer test folds: pool all their raw held-out row probabilities,
then average once per participant. Averaging fold means would weight unequal visit
counts incorrectly. Metrics use one final vector per participant. Failed folds
remain visible and prevent complete pooled metrics.

## Privacy and saved reports

Default reports replace design names and cohort/feature digests with local aliases;
aliases indicate equality of recorded digests only within this comparison.
Private digests, memberships, feature names and fit IDs are omitted. Class labels
use the existing public label projection. Small positive confusion cells suppress
the entire MetricSet and every dependent difference (`privacy_small_cells`),
including on rerendering. Missing context is never fabricated.

`write_report` and `compare` use threshold 5 by default. Python report APIs support
an explicit threshold. Sensitive detail requires explicit opt-in and is visibly
marked; treat detailed outputs as private. Public JSON plus its manifest can be
rerendered with `report` without fitting or recovering hidden data. Existing output
files require a fresh directory or explicit overwrite permission.
