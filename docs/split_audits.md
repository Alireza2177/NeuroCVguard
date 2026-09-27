# Importing and auditing split plans

Use `load_split_plan(source, *, cohort, config) -> SplitPlan` and
`audit_splits(cohort, plan, *, config) -> AuditReport`. Both are available from
`neurocvguard` through lazy imports, preserving the small side-effect-free root
import. Implementations live in `io.py` and `audit.py`; literal partition checks
live in `checks/partitions.py`.

These APIs accept a validated `Cohort` from [load_cohort](input_tables.md) and
check participant and dependence-component membership. Use
[split generation](split_generation.md) to create assignments and the
[CLI](cli.md) to save audit reports.

## Executed synthetic example

The example supplies explicit assignments; it is not a split generator.

```python
import pandas as pd

from neurocvguard import audit_splits, load_split_plan
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.models import Cohort

data = pd.DataFrame(
    {
        "observation_id": ["o1", "o2", "o3", "o4"],
        "subject_id": ["p1", "p2", "p3", "p4"],
        "diagnosis": ["A", "B", "A", "B"],
        "site": ["site-X", "site-X", "site-X", "site-X"],
    }
)
config = AuditConfig(columns=ColumnMap(session=None))
cohort = Cohort(data, None, config.columns, ("o1", "o2", "o3", "o4"))
assignments = {
    "schema_version": "1.0",
    "plan_id": "synthetic-explicit",
    "origin": "imported",
    "cohort_digest": None,
    "objective": "unseen_participant",
    "scheme": "imported",
    "seed": None,
    "folds": [
        {"repeat_id": "r0", "fold_id": "f0", "train_ids": ["o1", "o2"], "test_ids": ["o3", "o4"]},
        {"repeat_id": "r0", "fold_id": "f1", "train_ids": ["o3", "o4"], "test_ids": ["o1", "o2"]},
    ],
}
plan = load_split_plan(assignments, cohort=cohort, config=config)
assert assignments["cohort_digest"] is None  # input not mutated
assert plan.cohort_digest is not None and plan.origin == "imported"
report = audit_splits(cohort, plan, config=config)
summary = next(
    check.evidence
    for check in report.checks
    if check.rule_id == "NCG-SPLIT-011" and check.scope.get("field") == "split_summary"
)
assert summary["valid_for_objective"] and summary["complete_cv"]
public_report = report.to_dict()
assert any(
    check["evidence"].get("evaluation_permitted") is True for check in public_report["checks"]
)
assert any(
    check.rule_id == "NCG-PROV-001" and check.status == "not_assessable" for check in report.checks
)
```

The summary's `evaluation_permitted` is ordinary **split-level eligibility**.
It does not claim features exist, preprocessing is correct, an estimator ran,
or the later evaluator has been implemented. The example computes no score.

## Import and binding

Source is a local `.json`/`.tsv` path or a schema-shaped dictionary. A string is
a path, not JSON text or executable code. UTF-8/BOM is supported. URLs, archives
and unsafe serialization formats are unsupported. Files are byte-bounded before
parsing by `limits.max_input_mb`, including a bounded read after the size check.
TSV assignment rows are bounded by `limits.max_rows`; folds repeat observations,
so assignment row count differs from cohort row count. Raise limits explicitly
when needed; no seed search, truncation or fallback occurs.

JSON uses the unchanged packaged split schema and duplicate-key/finite-JSON
validation. Schema version, unknown keys, empty partitions, duplicate memberships
and duplicate fold keys fail. Observation IDs are strings, never row positions.
Padding/control characters or missing tokens in assignment identities are rejected
without normalization. The import verifies all outer and inner IDs against the
cohort, plus objective equality, role-map equality and any supplied cohort digest.

TSV requires this exact unique header order:

```text
repeat_id<TAB>fold_id<TAB>role<TAB>observation_id
```

Only `train` and `test` roles are accepted. Extra/missing columns, malformed
quoting/rows, invalid roles and duplicate `(repeat, fold, role, observation)`
memberships fail. No broad NA vocabulary is used: `NA` remains a literal ID;
empty strings and `n/a` are missing. TSV cannot express inner folds; use JSON.
TSV retains first-encounter fold order, sorts each membership list and omits the
optional `inner_folds` field. Its plan ID is `imported-` plus the canonical hash
of those outer fold records; seed is null, scheme/origin are imported and the
objective is explicitly taken from config. JSON retains its supplied fold order,
origin, seed and optional-field presence under the existing record contract.

`cohort_digest(cohort)` in `neurocvguard.io` provides the minimal metadata binding
used to bind the plan to its cohort. It hashes canonical JSON with keys `columns` (the full role map)
and `records` (unique mapped columns, records sorted by observation ID). Missing
cells and absent mapped columns are explicit nulls. Mapped identities, target,
session, site, phase, independence and covariates are included. Feature values
and unrelated columns are excluded. Mapping/list order stays explicit; object
keys are sorted, output is compact UTF-8 and Unicode is not normalized. This is
the representation the cohort loader also uses; no second digest format
or cohort/feature reader was introduced.

A null-digest imported plan gets a new bound copy only after identity validation.
Its origin remains imported. A non-null mismatch is rejected, never overwritten.
Generated records retain their existing hash-derived plan-ID validation. Digests
and plan files are sensitive integrity artifacts, not authentication/anonymization.
Binding does not approve separation or coverage: well-formed violating plans must
still be auditable. Use `audit_splits` after import.

## Audit checks and evidence

The audit verifies global objective/mapping/digest compatibility before inspecting
folds. A structurally valid plan with unknown IDs may be passed directly to
the auditor to obtain scoped diagnostics. Import is stricter and rejects those
unknown IDs. Duplicate/empty structural memberships fail at record construction,
before any set conversion; no duplicate is silently collapsed.

| Rule | Scoped meaning |
|---|---|
| NCG-SPLIT-001 | Outer observation overlap is an error for every objective, including diagnostic requests. |
| NCG-SPLIT-002 | Participant intersection, with participant-local session overlap as explanatory evidence. No separate global session failure is invented. |
| NCG-SPLIT-003 | Protected-component intersection; incomplete relationships remain unassessable and block strict eligibility. Known overlap can coexist with an additional incomplete-coverage notice. |
| NCG-SPLIT-004 | Site/phase separation only for the corresponding held-out-domain objective. Missing required domains remain unassessable; observed overlap is additionally reported when known. Shared domains under unseen_participant are informational/not_applicable. |
| NCG-SPLIT-005 | Global class order and participant-level training support. Missing training classes or fewer than two global classes block ordinary evaluation; incomplete/changing targets are unassessable. |
| NCG-SPLIT-006 | Global class order and participant-level test/validation support. Missing test classes are warnings: class-complete metrics are undefined, never invented as zero. |
| NCG-SPLIT-007 | Unknown observation keys. Dependent identity/domain/class checks for that partition are unassessable; there is no partial/positional join. |
| NCG-SPLIT-008 | Outer train/test union must equal the supplied cohort; omitted and extra IDs remain explicit. |
| NCG-SPLIT-009 | Every inner membership belongs to outer training and excludes outer test. |
| NCG-SPLIT-010 | Inner observation disjointness/coverage and exactly-once validation coverage. Scoped 002/003 separately check inner participants/components. Missing requested inner assignments remain unassessable. |
| NCG-SPLIT-011 | Per-repeat test coverage, plus the separate derived split summary described below. |

Checks use unsuppressed data. They are sorted by rule, repeat, outer fold, inner
fold and field scope, independent of input fold order. Unknown keys block only
the dependent checks; other folds and literal observation/coverage diagnostics
remain present. Under audit_only, participant/component overlaps are warnings,
but the absence of a supported objective can never produce a true validity flag.
The diagnostic option does not weaken any split-audit invariant; the separate narrow
diagnostic evaluator exception must keep the original invalid-for-objective audit.

Training sets can overlap across ordinary folds. Only within-partition boundaries
and per-repeat test coverage are checked. Inner tuning explicitly protects unseen
participants/components even for domain-held-out outer evaluation. It does not
inherit a site/phase-held-out claim. Each inner record reports this objective in
containment/coverage evidence. Supplied inner plans are checked even when tuning
is disabled; when tuning is requested, missing inner assignments block eligibility
and are never generated automatically.

## Summary, completion and privacy

The API returns the existing `AuditReport`, not a second external format. Its
NCG-SPLIT-011 check with `scope.field == "split_summary"` stores:

| Field | Meaning |
|---|---|
| `valid_for_objective` | False for audit_only or any failed/unassessable required separation, training, nesting, structural or requested complete-CV coverage prerequisite. A test-class warning alone does not invalidate a split. |
| `complete_cv` | Exactly one repeat, at least two outer folds and every observation in test exactly once. This can be true even when identity separation is invalid. |
| `evaluation_permitted` | Valid-for-objective, complete-CV and constant-target prerequisites passed at this stage. This is ordinary split-level eligibility, not authorization or a model fit. |
| `n_repeats`, `n_outer_folds` | Supplied repeat/fold counts. |
| `diagnostic_requested` | The explicit config flag; it does not waive findings. |
| `class_order` | Sorted global observed class labels; private summary evidence retains it. |

Per-repeat 011 checks retain their own `complete_cv`. A one-fold holdout has
complete_cv=false and not_applicable complete-CV coverage, without a false
failure for untested training rows. Multiple complete repeats are audited
independently and may be valid for their stated objective, while overall
complete_cv/evaluation_permitted remain false. Malformed multi-fold CV coverage
is a warning/failure and cannot use the one-fold exception.

The fixed NCG-PROV-001 unknown-upstream check remains present and unassessable.
Consequently this split-only report has technical execution status `partial`,
even if all split prerequisites pass. Ledger checks are available separately
through audit_cohort; a Pipeline cannot repair earlier fitting.

`report.to_dict()` conservatively omits membership IDs, component hashes, raw
domain labels, free text and class-support tables. It aliases repeat/fold scopes
and retains only explicitly typed 011 boolean/count summary fields. No raw
identity can be substituted into those fields through a string or bool-as-count.
Sensitive in-memory evidence retains exact memberships/supports; use
`report.to_dict(sensitive_details=True)` explicitly for local detailed JSON.
Plan serialization remains the separate sensitive operational representation.
No files are written by these APIs. Reporting supplies rich table projection/rendering;
the current public report does not promise formal anonymization.
