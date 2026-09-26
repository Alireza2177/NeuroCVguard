# Participant-level acquisition/target association

S06 provides `neurocvguard.checks.associations.check_associations(cohort,
config=config)`. It returns immutable `CheckResult` records for mapped site,
phase and explicitly declared categorical covariates, each paired with target.
It consumes an already constructed `Cohort`; S02 file ingestion remains absent.
It does not fit models, change cohorts or splits, or write files. Ledger checks,
combined audit orchestration and report rendering belong to later stages.

## Executable synthetic example

```python
import pandas as pd

from neurocvguard.checks.associations import check_associations
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.models import Cohort

metadata = pd.DataFrame(
    {
        "observation_id": [f"observation-{i}" for i in range(20)],
        "subject_id": [f"participant-{i}" for i in range(20)],
        "site": ["site-A"] * 10 + ["site-B"] * 10,
        "diagnosis": (["class-A"] * 5 + ["class-B"] * 5) * 2,
    }
)
config = AuditConfig(columns=ColumnMap(session=None))
cohort = Cohort(metadata, None, config.columns, tuple(metadata.observation_id))
checks = check_associations(cohort, config=config)
review = next(check for check in checks if check.rule_id == "NCG-ASSOC-001")
assert review.evidence["table"] == ((5, 5), (5, 5))
assert review.evidence["statistic"] == {"value": 0.0, "reason": None, "n": 20}
assert review.to_dict()["evidence"] == {"details_omitted": True}
private = review.to_dict(sensitive_details=True)
assert private["evidence"]["n_complete"] == 20
```

## Counting and undefined results

Each participant contributes at most one complete pair, regardless of repeated
observations or their order. Any within-participant change in either variable
makes the entire requested pair unassessable. Stable participants are not used
to rescue an unstable pair. Family members are counted as participants; this
does not assert independent samples or an exchangeability design.

A participant with any missing visit value on either side is excluded only
from this diagnostic's complete pairs. No known visit is selected to fill a
missing one. Sensitive evidence records `n_original`, `n_complete`, `n_excluded`,
missing/invalid/unstable participant counts on each side and `n_in_table`.
The exclusion count is a union, so field/target missingness counts may overlap.
`n_complete` describes potential complete, stable records even when instability
elsewhere blocks the entire pair; `n_in_table` and statistic `n` are then zero.
Missing target values are disclosed, not repaired or approved for classification.

The table uses sorted string levels, removes unused categories and retains
observed zero cells. The estimator is Cramer's V from uncorrected Pearson
chi-square, using SciPy `association(table, method="cramer", correction=False)`.
This is not a small-sample bias correction. No p-value or significance stars
are produced. Non-finite expected counts or V raise `InputValidationError`.

Undefined statistics have `value=None` and an explicit reason:
`unstable_within_participant`, `invalid_values`, `missing_field`, `missing_target`,
`no_complete_pairs`, `too_many_categories` or `constant_variable`.
Mapped absent columns are reported; unmapped acquisition fields are not requested.
More than 100 observed levels on either axis skips table allocation and V,
including levels observed only in otherwise incomplete pairs. Levels are never
merged. A constant axis retains its table/support but has null V; a separate
sparse-table check can still apply.

## Interpretation and privacy

`NCG-ASSOC-001` uses the configured inclusive review threshold (default 0.3).
Its warning is: “Acquisition/target association warrants review under the stated
generalization objective.” The threshold is an operational review trigger,
not a universal effect-size or clinical cutoff. A below-threshold result is
not a validity verdict. Recommendations for held-out sites or phases are
conditional on a claim about generalization to those domains.

`NCG-ASSOC-002` warns when any observed or expected cell is below
`association.min_cell_count` (default 5), including observed zeros.
`NCG-ASSOC-003` records an unassessable pair. The existing check status `fail`
means that the scoped warning was triggered; association alone does not prove
causal confounding, leakage, model bias or model shortcut use.

Internal evidence and `to_dict(sensitive_details=True)` retain exact category
labels, source columns, tables, expected counts, denominators and V. Treat them
as sensitive local records. Individual check serialization conservatively omits
the entire linked numeric evidence, even for non-sparse tables. S08 whole-report
projection can display validated tables with local aliases when every cell meets
the report threshold. A suppressed table omits its linked cells, totals and V;
safe null reasons remain. Privacy projection never changes the internal statistic.
See [the reporting guide](reporting.md) for the S08 display boundary.

The foundation acknowledges mlconfound's adjacent inferential work; these
descriptive diagnostics do not implement or claim equivalent tests. See
[the normative association specification](../spec/09_association_diagnostics.md)
and its [R08/R09 source register](../spec/21_sources.md).

S06 is local research software awaiting human review. The exact commands,
environments and results are in [the S06 handoff](../state/handoffs/S06.md).
