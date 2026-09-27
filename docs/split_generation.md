# S05 deterministic outer split generation

`make_splits(cohort, *, config) -> SplitPlan` now generates supplied-cohort outer
plans with standard sklearn splitters and audits the result before returning.
It writes nothing and fits no estimator. Pass a validated `Cohort` from
`load_cohort`; the CLI `split` command also writes operational artifacts.

## Executed example

All identities in this example are fictitious. This creates six participants,
then writes sensitive local artifacts explicitly.

```python
import pandas as pd

from neurocvguard import make_splits
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.models import Cohort

metadata = pd.DataFrame(
    {
        "observation_id": ["o1", "o2", "o3", "o4", "o5", "o6"],
        "subject_id": ["p1", "p2", "p3", "p4", "p5", "p6"],
        "diagnosis": ["A", "B", "A", "B", "A", "B"],
    }
)
config = AuditConfig(columns=ColumnMap(session=None, site=None))
cohort = Cohort(metadata, None, config.columns, tuple(metadata.observation_id))
plan = make_splits(cohort, config=config)
assert plan.origin == "generated" and len(plan.folds) == 3
assert plan.generation_report is not None
summary = next(
    check.evidence
    for check in plan.generation_report.checks
    if check.scope.get("field") == "split_summary"
)
assert summary["complete_cv"] and summary["valid_for_objective"]
paths = plan.write("local-splits")
assert paths["plan"].name == "plan.json"
assert paths["generation_report"].name == "generation.private.json"
```

A clean split audit does not verify upstream preprocessing or establish clinical
validity. `evaluation_permitted` in the S04 summary remains split-level eligibility,
not a claim that features exist or an evaluator ran. Technical report completion
remains `partial` because upstream history is unassessable.

## Participant and domain schemes

For `subject_kfold` / `unseen_participant`, the planner constructs a canonical
participant table sorted by participant ID. Each person contributes exactly one
constant target and one protected-component label. It calls
`StratifiedGroupKFold(n_splits=..., shuffle=True, random_state=...)` once, then
expands participant membership to all observation IDs. Visit multiplicity cannot
weight the stratification objective. Mixed-class families retain each person's
target; no single family label is guessed. Components include participant identity
and transitive relationships from S03.

At least two classes, complete constant participant targets and at least n_splits
independent components are required. Missing declared relationships block strict
planning. The report records each class's number of supporting components. Fewer
than n_splits supporting components rules out class-complete test folds; fewer
than two is a strong warning. Sufficient component counts are only a necessary
condition, not proof that every desired balance is achievable. Actual training
and test support is recorded by the independent S04 audit. Stratification is
approximate under indivisible groups. A missing training class rejects the whole
requested plan; missing test classes can remain as warnings with undefined
class-complete metrics. No scores are computed.

For `leave_one_site_out` / `unseen_site`, use `split.n_splits=null`; for
`leave_one_phase_out` / `unseen_phase`, do the same with phase. The requested role
must be mapped, complete and constant within every participant and protected
component. Crossing participants/families cause an explicit refusal. At least
two domains are required. `LeaveOneGroupOut` holds out every represented domain
exactly once; domain count determines fold count. The seed is still recorded,
although this splitter uses no randomness.

Generated repeat_id is `0`; fold IDs are `fold-000`, `fold-001`, etc. Observation
membership arrays are sorted. Role-mapped metadata uses the S04 canonical cohort
digest. plan_id is SHA-256 of canonical plan contents excluding plan_id itself.
Fixed supported dependency versions, input and seed give reproducible artifacts;
NumPy's global RNG state is untouched. No seed search, splitter fallback, class
merging, row dropping or automatic fold-count reduction is performed.

S05 generates outer folds only. `evaluation.tune=true` is explicitly refused:
inner generation belongs to S11. Existing supplied nested plans can still be
imported, audited and exported through S04/S05. `audit_only` and `imported` are
not generation schemes. Invalid seed ranges are rejected by the existing strict
configuration schema, without normalization.

## Diagnostics and model boundaries

A successful return has passed the same `audit_splits()` used for imported plans.
An independently detected failure rejects the result; the generator's own counts
are insufficient to approve it. Actual test-class warnings are retained.

`plan.generation_report` is an immutable AuditReport captured in memory, including
NCG-PLAN-001/002/003 diagnostics where relevant, complete S04 scoped checks and
NumPy/sklearn/software versions. Requested settings and the successful plan ID
are recorded as private evidence. Its `.to_dict()` uses the existing conservative
public projection; `.to_dict(sensitive_details=True)` retains local diagnostics.

The canonical SplitPlan JSON contract is unchanged. generation_report is a
nonserialized, nonconstructor, noncomparing runtime field. Deserializing or
replacing a plan clears that field: imported text cannot authenticate internal
generation history. It neither changes plan IDs nor adds unknown schema keys.
Saving an in-memory generated plan writes the captured report separately so the
original dependency versions are retained. A loaded plan without that report
never acquires current dependency versions as alleged historical provenance.

A scientifically infeasible request raises `PlanningError`, a subclass of
`UnsupportedDesignError`, with a blocked `error.report`. Save it explicitly with
`neurocvguard.io.write_rejected_plan(error.report, output_dir="rejected")`.
No candidate plan is returned or exported as usable. Structural input errors
retain the existing ConfigurationError/InputValidationError boundary; unsupported
objectives or nested-generation requests use UnsupportedDesignError. This API
does not write, print or exit on an error automatically.

## Sensitive exports and overwrite behavior

`plan.write(output_dir, overwrite=False)` delegates to `io.write_split_plan`:

| Returned key | Filename | Meaning |
|---|---|---|
| plan | plan.json | Canonical identity-bearing operational plan, including supplied inner folds. |
| assignments | assignments.tsv | Exact `repeat_id`, `fold_id`, `role`, `observation_id` header; outer train/test rows only. |
| generation_report | generation.private.json | Captured sensitive audit/support/version record, only when available. |
| notice | README.SENSITIVE.txt | Explicit privacy and interpretation notice. |

TSV is a convenience view; JSON is canonical. Neither is anonymized. Use TSV as
an operational text table, not as executable spreadsheet content. Default report
privacy does not strip identities from plans because that would destroy their
operational meaning. No public report renderer is implemented by this stage.

All named output conflicts are checked before artifact writes. Default exclusive
creation also protects against a competing writer after the initial check.
`overwrite=True` explicitly permits replacement of the writer's named regular
artifacts; unrelated files are preserved. Output symlinks are refused. Staging
completes before replacement; individual replacements are atomic, but a bundle
is not a filesystem transaction. A storage failure during replacement may leave
partial outputs and raises an explicit error. Permissions depend on the local
filesystem; the sensitivity notice is not an access-control guarantee.

Rejected diagnostics use `rejected-plan.private.json` and `REJECTED.SENSITIVE.txt`
in a separate directory, with no plan.json or assignments.tsv. The writers refuse
to mix rejected and usable artifacts. A loaded plan cannot overwrite a directory
containing generation.private.json because its unknown history cannot be safely
attributed to that file. Choose a fresh destination in that case.

No new runtime dependency, dataset download, model fitting, telemetry, publication
or later-stage workflow was introduced. Tests and actual environment limitations
are recorded in `state/handoffs/S05.md`.
