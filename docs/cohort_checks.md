# S03 cohort checks

S03 provides pure in-memory checks on an explicitly constructed `Cohort`. It was
originally implemented before S02 using synthetic in-memory records. The completed
[S02 loader](input_tables.md) now supplies strict local inputs; split audits,
planning and reporting are provided by later implemented stages. Human acceptance
remains separate, and no evaluator is claimed here.

## Complete synthetic example

```python
import pandas as pd

from neurocvguard.config import ColumnMap
from neurocvguard.models import Cohort
from neurocvguard.checks.cohort import check_cohort

metadata = pd.DataFrame(
    {
        "observation_id": ["o1", "o2", "o3"],
        "subject_id": ["person-A", "person-A", "person-B"],
        "diagnosis": ["class-A", "class-A", "class-B"],
        "session_id": ["ses-01", "ses-02", "ses-01"],
        "site": ["site-X", "site-X", "site-X"],
        "family": ["family-A", "family-A", "family-B"],
    }
)
features = pd.DataFrame(
    {
        "observation_id": ["o1", "o2", "o3"],
        "feature_1": [1.0, 2.0, 3.0],
        "feature_2": [4.0, 5.0, 6.0],
    }
)
cohort = Cohort(metadata, features, ColumnMap(independence=("family",)), ("o1", "o2", "o3"))
result = check_cohort(cohort, ("feature_1", "feature_2"))
assert (result.inventory.n_observations, result.inventory.n_participants) == (3, 2)
assert len(result.components.components) == 2
assert result.feature_equality.groups == ()
result.components.require_complete()
result.inventory.require_constant_target()
public_checks = [check.to_dict() for check in result.checks]
assert any(check["rule_id"] == "NCG-COHORT-001" for check in public_checks)
```

The two guards enforce only their named prerequisites. Passing them does not
establish sufficient classes/groups, split feasibility, training correctness or
scientific validity. No fitting, file write, random-number generation or network
operation occurs. Constructing `Cohort` requires explicit observation-key alignment;
this example supplies already aligned synthetic tables and performs no join.

## Functions and results

| Function | Result and meaning |
|---|---|
| `inventory_cohort(cohort)` | `CohortInventory`: observation/participant counts, counts per participant, mapped-field coverage and constant-target prerequisite. |
| `inventory_checks(inventory)` | Stable `CheckResult` records for repeats, target/domain variation and incomplete metadata. |
| `build_components(cohort)` in `neurocvguard.identity` | `ProtectedComponents`: deterministic participant components, relationship coverage and strict-use guard. |
| `exact_feature_equality(cohort, feature_columns, enabled=True)` | `FeatureEquality`: exact cross-participant groups and assessed/skipped coverage. |
| `check_cohort(cohort, feature_columns=(), check_features=True)` | `CohortAudit`: inventory, components, equality and sorted S03 checks. It does not create an overall AuditReport or assess partitions. |
| `get_rule(rule_id)` in `neurocvguard.rules` | One immutable implemented catalog entry; unknown IDs raise `KeyError`. `COHORT_RULES` follows catalog order. |

`CohortInventory.observations_per_participant` contains sorted `(ID, count)`
pairs. `fields` contains one `FieldInventory` per scalar role, then indexed
independence/covariate roles in their explicit mapping order. Use
`inventory.field_for("session")` to inspect participant-local sessions.

Each `FieldInventory` records role, column name (or null), availability, missing
and malformed row counts, observation label counts, nonexclusive participant
label counts and sorted `ParticipantValues`. Each participant record contains
their distinct known labels and missing/malformed observation counts. These
records preserve known information even when coverage is incomplete. Site/phase
participant counts can sum above the cohort participant count when people span
domains. Session counts are lengths of each person's distinct session values;
the same session text in another person has no identity significance. Several
observations with the same person/session pair are retained.

`participant_class_counts` counts only participants with exactly one known label
and complete target coverage. A class observed only in excluded, ambiguous
participants has count zero. All participants remain in total counts; missing or
varying target records remain explicit. `constant_target_eligible` is false for
empty cohorts, missing/unmapped/malformed targets and within-person variation.
`require_constant_target()` raises `UnsupportedDesignError` in those cases;
changing targets are a scope limit, not a diagnosis of incorrect labeling.

## Identity and relationships

Mandatory observation/participant identities are defensively checked before
set-based conclusions. Missing, non-string, surrounding-whitespace or control-
character IDs raise `InputValidationError`, with a role/count and no raw IDs.
Legitimate Unicode, case, prefixes and `001` versus `1` remain distinct. No
source alias resolution or site-prefix rewriting is performed. Unknown physical
aliases still require upstream identity curation.

Components use union–find over participant IDs. Equal non-missing values connect
participants only within the same declared relationship column; different columns
have separate namespaces. A person with multiple relationship values bridges
them transitively. Every participant appears, including singletons. The mapped
session column cannot be declared a global relationship key: that produces an
actionable `ConfigurationError` rather than linking people by `ses-01`. Sites and
phases add no links automatically; an explicit protected relationship declaration
remains the user's input, not independently verified biology.

Missing scalars, empty strings and `n/a` represent missing values; `NA` is a
legitimate label. Malformed optional categorical/relationship values remain
unassessable, without erasing other inventory results. Missing or malformed
relationship values add no union operations. `coverage` has a
`RelationshipCoverage` record for each column; any incomplete record makes
`complete=False`. `require_complete()` raises `SplitValidationError`, preventing
strict use of these partial components by planning/evaluation callers.
The planner and evaluator call this guard before strict use.

Component members are sorted without normalization. Component IDs are
`component-` plus SHA-256 of canonical JSON for that membership tuple. Both
membership and labels are invariant to row permutations. Labels are internal
integrity representations, not anonymous patient IDs. `participant_to_component`
returns a read-only mapping. Feature equality never contributes union operations.

## Exact feature equality

Selection must be explicit, unique and exclude mapped roles, independence and
covariates. Features must already be aligned, finite numeric scalars or missing.
Numeric text, infinity and lossy float conversions are refused. No numeric-column
inference or fuzzy rounding occurs. Nonselected feature columns are not examined.

Canonical numeric tuples use `None` for missing positions and positive zero for
either signed zero. A deterministic SHA-256 bucket is followed by a full-tuple
dictionary lookup that confirms exact equality. Primary hash collisions cannot
create matches. There is no all-pairs scan; storage is proportional to the
selected vectors and observation memberships. Hashing does not remove the need
for S02 input resource guards or bound total process memory.

All-missing vectors are skipped, never treated as matching acquisitions. The
result records `skipped_all_missing` and each finding records `skip_reason`.
If nothing is assessable, `reason` is `all_missing_vectors` or `no_observations`.
Absent features yield `features_not_supplied`; explicitly disabling the check
yields `not_requested`. Equal vectors from only one participant are not a
cross-participant finding. Groups contain sorted observation and participant IDs
and are sorted by their observation memberships. Matching partial vectors require
the same missing positions. Equality is heuristic evidence requiring review;
it never proves duplicated images or authorizes a merge/drop.

## Check meaning, order and privacy

The six stable IDs and catalog metadata are exercised against `qa/rule_catalog.json`.
Checks sort by rule ID, then structural field scope. Repeats and domain crossings
are informational observations. Target variation fails the constant-target
prerequisite. Feature equality uses warning/heuristic evidence; its `fail` status
denotes a review finding, not an observed split violation. Missing input checks
use `not_assessable` and `unassessable` evidence. Missing relationships are errors
because strict use must be blocked. Partial domain/target variation can be observed
while a separate missing-metadata notice retains incomplete coverage.

Raw inventories, component maps and equality memberships are sensitive in-memory
records. Frozen tuple-based outputs and caller-owned table copies prevent input
mutation; there is no raw public JSON serializer for these records. Use existing
`CheckResult.to_dict()` for conservative public messages with open evidence and
identifiers omitted. S03 supplies fixed public wording so equality cannot be
misrepresented as an observed identity violation. Explicit
`check.to_dict(sensitive_details=True)` retains detailed local evidence.

No statistic is calculated from privacy-suppressed values. Rich evidence tables,
small-cell display treatment and report rendering are implemented in reporting. A public check
list is not a complete research report, upstream-provenance assessment, anonymity
guarantee or global leakage-free verdict.
