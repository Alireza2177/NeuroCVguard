# Preprocessing declarations and fit boundaries (S07)

`audit_cohort(cohort, *, config, ledger=None)` now combines cohort checks,
categorical association and preprocessing declarations in an `AuditReport`.
It accepts validated `Cohort` objects returned by `load_cohort`.
It does not execute transforms or fit a model. Its coverage stays partial:
upstream execution cannot be authenticated from a feature matrix or plain JSON.

## Synthetic example

```python
import pandas as pd

from neurocvguard import audit_cohort, make_splits
from neurocvguard.checks.preprocessing import check_preprocessing
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.fit_boundaries import prepare_fit_boundary, validate_fit_ids
from neurocvguard.models import Cohort
from neurocvguard.provenance import load_preprocessing_ledger

data = pd.DataFrame(
    {
        "observation_id": [f"o{i}" for i in range(6)],
        "subject_id": [f"p{i}" for i in range(6)],
        "diagnosis": ["A", "B"] * 3,
    }
)
config = AuditConfig(columns=ColumnMap(session=None, site=None))
cohort = Cohort(data, None, config.columns, tuple(data.observation_id))
plan = make_splits(cohort, config=config)
fold = plan.folds[0]
declaration = {
    "schema_version": "1.0",
    "source": "user_declaration",
    "events": [
        {
            "event_id": "declared-scale",
            "transform": "StandardScaler",
            "data_dependent": True,
            "repeat_id": fold.repeat_id,
            "fold_id": fold.fold_id,
            "inner_fold_id": None,
            "fit_scope": "outer_train",
            "fit_ids": list(fold.train_ids),
            "uses_target": False,
            "note": "Synthetic declaration; no scaler was fitted.",
        }
    ],
}
ledger = load_preprocessing_ledger(declaration, cohort=cohort, config=config, plan=plan)
checks = check_preprocessing(cohort, config=config, ledger=ledger.to_operational_dict(), plan=plan)
scoped = next(item for item in checks if item.rule_id == "NCG-PROV-003")
assert scoped.status.value == "pass" and scoped.evidence_kind.value == "declared"

report = audit_cohort(cohort, config=config, ledger=declaration)
assert report.provenance["upstream_preprocessing_verified"] is False
assert report.execution_status.value == "partial"
# The exact audit_cohort signature has no plan: its fold-boundary check is unassessable.
assert not any(item.rule_id == "NCG-PROV-003" for item in report.checks)

boundary = prepare_fit_boundary(
    cohort,
    plan,
    config=config,
    event_id="planned-fit",
    repeat_id=fold.repeat_id,
    fold_id=fold.fold_id,
    C=1.0,
)
validate_fit_ids(boundary, fold.train_ids)
assert not hasattr(boundary, "status")
assert "fit_events" not in report.to_dict(sensitive_details=True)
```

## Loading and context

`neurocvguard.provenance.load_preprocessing_ledger` accepts a schema-shaped dict
or local uncompressed UTF-8 `.json` file, bounded by `limits.max_input_mb`.
It rejects duplicate JSON keys, nonfinite literals, unknown keys, duplicate
event/fit IDs, invalid identity labels and observation IDs absent from the cohort.
Imported source must be exactly `user_declaration`; `runtime_verified` is rejected.
Neither a transform name nor a note executes anything or authenticates history.

`outer_train` requires repeat/fold and no inner reference. `inner_train` requires
all three references. Optional context on other scopes must also be consistent.
With a plan, references are resolved by their full repeat/outer/inner keys;
partitions must be disjoint and cover the appropriate cohort/training set.
This structural context check does not replace the scientific split audit.
Without a plan, structurally valid references remain unresolved; no training
membership is inferred from a scope string. Unknown references in a supplied
plan are input errors. Known IDs outside training remain valid declarations
to audit, rather than being dropped or treated as malformed history.

## Findings and interpretation

| Rule | Meaning |
|---|---|
| NCG-PROV-001 | Upstream execution is unverified; also records unknown/external scope or missing plan/fit-ID context as unassessable. |
| NCG-PROV-002 | Declared data-dependent all-cohort fitting warrants a warning; it is not observed historical proof. |
| NCG-PROV-003 | Explicit fit IDs are compared to the relevant supplied training set. Pass/fail remains declared evidence. |
| NCG-PROV-005 | Fixed non-learning row-local conversions have no training-fit isolation requirement solely on that basis. The declaration itself is unverified. |

Global learning is flagged even without IDs or fold context. When a global event
also names a fold and explicit IDs, its membership can additionally be compared.
The global declaration warning remains even if those IDs conflict with its
all-cohort description. Inner fits are compared with inner train, excluding both
inner validation and outer test. An explicit strict training subset is allowed.

An external learned transform is unassessable: source overlap and deployment
availability are not established. A non-learning declaration is not automatic
safety approval; confirm row-local behavior and examine any declared target use
separately. Empty ledgers, all declared passes and fixed conversions never remove
the persistent upstream limitation. A later Pipeline cannot repair earlier global
learning. Auditing never reconstructs notebook history or executes user code.

`audit_splits` retains its split-only signature and the same unknown-upstream
limitation. Use `check_preprocessing(..., plan=plan)` for fold-specific ledger
comparison; the CLI combines these checks and renders HTML.

## Planned versus recorded fitting

The existing schema-backed `models.FitEvent` records actual fit IDs, fold, outer
or inner role, baseline parameter C and completed/failed status. Parsing this
record cannot authenticate its origin. S07 reuses that contract without changing
schemas or creating an observed event.

`prepare_fit_boundary` produces an immutable `FitBoundary` with permitted IDs
and model/fold context, but no execution status. `validate_fit_ids` rejects
empty, duplicate or outside-training IDs; a strict subset is permitted.
`validate_fit_event` checks a supplied completed/failed record against that
boundary. Validation is not proof a call happened. The controlled evaluator must
capture actual fit calls and outcomes, use fresh pipelines, and fail on an
internal boundary violation. No callback, estimator runner or logging mechanism
is implemented here.

## Sensitive evidence

Ledgers, FitEvent records and in-memory evidence can contain observation IDs,
transform names and notes. Operational serialization is sensitive. Default
check/report projections replace user text with fixed qualified wording, omit
event names/memberships and alias fold references. A declared violation is never
presented as observed execution. Explicit sensitive report serialization retains
the diagnostic evidence and its sensitivity notice. No report files are written
by S07 and no public release is authorized.

See {download}`the S07 handoff <../state/handoffs/S07.md>` for exact checks and limitations.
