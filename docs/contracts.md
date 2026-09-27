# Configuration and record contracts

Records validate and serialize inputs for the implemented audit, split,
evaluation and comparison APIs. Schemas under `contracts/` remain normative and
are packaged for offline validation. See the complete [API](api.rst) and
[configuration key reference](configuration.md). Import classes from
`neurocvguard.config` or `neurocvguard.models`; the root import stays small.

## Configuration

`AuditConfig.from_dict(mapping)` and `AuditConfig.from_json(text)` require all
fields marked required by `config.schema.json`. `load_config(path)` reads a
local UTF-8/BOM `.json` file with a pre-read size bound of 128 MiB, overridable
by an explicit positive `max_input_mb` argument. It refuses URLs, missing files,
other suffixes, invalid UTF-8, malformed JSON and oversized input.

Only two missing file fields are filled: `evaluation.positive_class=None` and
`limits.max_input_mb=128`. An explicit null role remains absent; no role is
inferred. `AuditConfig()` is an explicit request for the specification's example
defaults, including example feature names; it is not a fallback for incomplete
JSON. Users must select their real roles/features before later data operations.

| Record/section | Fields and meaning |
|---|---|
| `ColumnMap` / `columns` | `observation_id`, `subject_id`: mandatory source columns. `target`, `session`, `site`, `phase`: source column or null. `independence`, `categorical_covariates`: explicit tuples of columns. |
| `StudyConfig` / `study` | `objective`: `unseen_participant`, `unseen_site`, `unseen_phase`, or `audit_only`. |
| `SplitConfig` / `split` | `scheme`: `subject_kfold`, `leave_one_site_out`, `leave_one_phase_out`, `imported`; `n_splits`: 2–20 for subject_kfold, null otherwise; `seed`: explicit unsigned 32-bit integer. |
| `AssociationConfig` / `association` | `review_threshold` defaults 0.3; `min_cell_count` defaults 5. These are descriptive software guardrails. |
| `EvaluationConfig` / `evaluation` | `feature_columns`, `tune`, `C`, `C_grid`, `inner_splits`, `max_iter`, `diagnostic_allow_subject_overlap`, `positive_class`. Example defaults: two example features, false, 1.0, (0.1, 1.0, 10.0), 3, 2000, false, null. |
| `ReportConfig` / `report` | `sensitive_details=False`; `small_cell_threshold=5` (at least 2). |
| `LimitsConfig` / `limits` | `max_rows=100000`, `max_features=10000`, `max_dense_mb=512`, `max_input_mb=128`; all positive integers. |
| `AuditConfig` | `schema_version="1.0"` plus the seven sections above. |

Scalar role collisions and predictor overlap with roles/independence/covariates
are rejected. A generation scheme must match the non-audit objective. An
audit-only configuration may carry unused split settings, empty features and
no target; this does not authorize generation/evaluation. Column existence and
actual cohort feasibility are checked by later data/design stages, not guessed
while parsing configuration.

Unknown keys, duplicate keys, boolean numbers and unsupported schema versions
fail. Configuration errors use `ConfigurationError` and identify the affected
field/key without echoing research-row values. Required field values are never
silently coerced, dropped, relabeled, or selected by heuristic.

## Records and fields

All schema records are frozen dataclasses. Their constructors and `from_dict`
validate structure and the implemented record semantics. Nested arrays become
tuples and open JSON objects become read-only mappings. `to_dict` or the
explicit operational serializer returns independently owned JSON containers.
Changing source mappings or exported dictionaries cannot change a record.
These records are not a promise that an untrusted experiment really ran as stated.

| Record | Fields / boundary |
|---|---|
| `Cohort` | `metadata`, optional `features`, `columns`, `observation_order`. Takes copies of already validated pandas tables and requires their observation-key order to match the explicit order. No row-order join or automatic alignment. Properties return copies. Tables remain sensitive; pandas deep copying does not recursively clone arbitrary object cells, so validated cells must be scalars. |
| `SplitPlan` | `schema_version`, `plan_id`, `origin`, `cohort_digest`, `objective`, `scheme`, `seed`, `folds`. Operational only. Imported digests/seeds may be null. Generated digests are mandatory. |
| `SplitFold` | `repeat_id`, `fold_id`, `train_ids`, `test_ids`, optional `inner_folds`. Repeat/fold pairs are unique; an omitted inner_folds stays omitted. |
| `InnerFold` | `inner_fold_id`, `train_ids`, `validation_ids`. Inner identifiers are unique within each outer fold. |
| `CheckResult` | `instance_id`, `rule_id`, `status`, `severity`, `evidence_kind`, `scope`, `message`, `recommendation`, `evidence`. Free text, scope values and open evidence may carry private details. |
| `MetricValue` | `value`, `reason`, `n`. Undefined values are null with a nonblank reason; a defined value has a null reason. `n` is nonnegative. |
| `ClassMetric` | `class_label`, `support`, `recall`. Class order is explicit, not alphabetically guessed. |
| `MetricSet` | `accuracy`, `balanced_accuracy`, `macro_f1`, `roc_auc`, `n_participants`, `per_class`, `confusion_matrix`. Requires square class-aligned dimensions and consistent row/participant supports. |
| `CandidateScore` | `C`, `balanced_accuracy`, `reason`. An undefined supplied candidate score needs a reason. No search or selection runs here. |
| `EvaluationFold` | `repeat_id`, `fold_id`, `status`, `reason`, `train_participants`, `test_participants`, `selected_C`, `metrics`, `candidate_scores`. A failed fold remains present, with reason and null metrics. |
| `FitEvent` | `event_id`, `repeat_id`, `fold_id`, `inner_fold_id`, `C`, `fit_ids`, `status`, `scope`. Sensitive supplied fit metadata; parsing does not authenticate execution. |
| `EvaluationResult` | `format`, `schema_version`, `tool_version`, `sensitive`, `execution_status`, `objective`, `diagnostic_only`, three integrity digests (`cohort`, `feature`, `config`), `class_order`, `positive_class`, `feature_columns`, `metric_unit`, observation/participant counts, `folds`, `fit_events`, `pooled_metrics`, `preflight_checks`, `limitations`, `provenance`. Uses the exact evaluation-result schema field names. |
| `ComparisonDesign` | `name`, `objective`, `diagnostic_only`, `metrics`. |
| `MetricDifference` | `design_a`, `design_b`, `metric`, `difference`, `reasons`. Undefined differences require reasons; names must reference declared designs. |
| `ComparisonResult` | `designs`, `differences`, `interpretation`. Uses comparison-summary schema. No difference is computed by constructing this record. |
| `AuditReport` | `schema_version`, `tool_version`, `result_type`, `objective`, `execution_status`, `input_summary`, `checks`, `limitations`, `provenance`, optional `evaluation_summary` or `comparison_summary`. The summary must match result_type. |
| `LedgerEvent` | `event_id`, `transform`, `data_dependent`, repeat/fold/inner IDs or null, `fit_scope`, `fit_ids`, `uses_target`, `note`. |
| `PreprocessingLedger` | `schema_version`, `source="user_declaration"`, `events`. Operational only; imported assertions cannot become observed history. |

Enums: `Objective`, `SplitScheme`, `CheckStatus`, `Severity`, `EvidenceKind`,
`ReportStatus`, `EvaluationStatus`, `FoldStatus`, and `PlanOrigin`. Unknown
enum values fail rather than receiving a fallback.

`not_assessable` requires `unassessable` evidence. Unassessable evidence cannot
establish a pass/fail. Declared preprocessing rules stay declared. A report with
unassessable requested checks cannot claim completed coverage. A completed
evaluation requires at least two completed folds in one repeat and pooled
metrics; incomplete/blocked evaluations cannot carry pooled metrics. These are
record consistency checks, not verification of fold membership or actual fits.

## Deterministic serialization

`strict_json_loads`, `canonical_json` and `json_digest` live in
`neurocvguard.serialization`. Standard JSON only: finite numbers, string keys,
explicit nulls, sorted object keys, compact separators, UTF-8 without Unicode
normalization. No NaN, Infinity, custom Python objects, or display rounding.
`canonical_json` requires an explicitly chosen projection, including for nested
record values; it cannot accidentally serialize a whole private dataclass.

Class order, feature order, candidate order and fold order are preserved.
Split observation memberships are canonically sorted as required by spec/05;
the source lists are not mutated. Duplicate memberships/identifiers are not
silently repaired. Structurally valid unknown-ID/participant-overlap fixtures
remain structurally loadable; audit_splits checks their actual cohort memberships.

For a generated plan, `plan_id` equals SHA-256 of the canonical plan dictionary
with `plan_id` removed, after membership sorting. This defines an integrity
representation, not a split-generation algorithm. Cohort/feature digest
construction and binding to actual tables are implemented in the input loader. Digests do not
anonymize identities or authenticate source data.

## Public versus operational output

- `EvaluationResult.to_operational_dict()` returns the complete record with
  `format="neurocvguard.evaluation.private"` and `sensitive=true`, including
  fit IDs and digests. A public report is rejected by this record loader.
- `EvaluationResult.to_dict()` returns an AuditReport envelope with a projected
  evaluation_summary; it cannot replace the private comparison input.
- `SplitPlan.to_operational_dict()` and
  `PreprocessingLedger.to_operational_dict()` are explicitly sensitive local
  representations. They have no default public report serializer.
- `AuditReport.to_dict()` and `CheckResult.to_dict()` exclude open evidence and
  free-form input text by default. Serialization uses fixed status/rule wording and safe
  structural scope aliases. Reporting implements rule-specific evidence/table
  projections; omitted details remain in the local record.
- `ComparisonResult.to_dict()` aliases design names and omits free-form reasons
  and interpretation text. Supplied raw labels/text are available only through
  an explicit `sensitive_details=True` call. Differences remain descriptive.

Public provenance excludes raw hashes, user paths and arbitrary version text.
Target class names remain visible. Unrecognized version text is `withheld`,
and free-form metric reasons become `undefined_metric`; precise reasons stay in
the operational record. Public limitations explain what was omitted and retain
the unknown-upstream boundary. A record's provenance flag does not override the
explicit serializer argument or authenticate an imported declaration.

Any positive confusion cell below `small_cell_threshold` (default 5) hides its
entire MetricSet. Linked pooled and fold MetricSets are suppressed together to
prevent subtraction from revealing a hidden fold. Comparison differences that
depend on a hidden design are null with `privacy_small_cells` reasons. Zero cells
alone do not trigger suppression. The sensitive report option retains original
metrics and displays an explicit sensitive-output limitation and provenance flag.
Public summaries cannot restore previously suppressed data.

This is a conservative projection, not formal anonymization. Standalone metric
components and in-memory objects are local research data; use a result/report
projection when preparing report JSON. No serializer writes or uploads a file.

## Errors and verification

`NeuroCVguardError` is the base for `ConfigurationError`, `InputValidationError`,
`SplitValidationError`, `UnsupportedDesignError`, and `EvaluationError`.
Record inconsistency errors are distinct from performing a cohort/design audit.
Full schema field definitions remain in the six packaged contracts; callers can
use `load_schema(name)` or `validate_document(name, mapping)` offline.

Run `python -m pytest -q --strict-markers --strict-config` from the editable
developer environment. Contract cases are linked to test IDs and command logs
in `qa/case_to_test_map.json` and `qa/evidence/S01/`. Use the foundation validator's
`--mode artifacts` option for document/schema/fixture consistency; it does not
run application tests.
