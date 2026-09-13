# 05 — Public models, schemas and deterministic serialization

## 5.1 Public records

Implement typed records `ColumnMap`, `AuditConfig`, `Cohort`, `SplitPlan`, `CheckResult`, `AuditReport`, `EvaluationResult`, and `ComparisonResult`. A record has one documented meaning across API, CLI and JSON. Avoid a second ad hoc dictionary format in HTML generation. The structural JSON schemas in `contracts/` must be copied into the installed package and versioned.

`Cohort` contains the validated metadata table, optional aligned feature table, role mapping and canonical observation order. Keep raw values in memory for computation; default report serialization uses a privacy projection. Do not promise that an in-memory Cohort is anonymized.

## 5.2 Split plan

The canonical JSON plan has `schema_version`, `plan_id`, `cohort_digest`, `objective`, `scheme`, `seed`, and `folds`. Each fold contains `repeat_id`, `fold_id`, `train_ids`, `test_ids`, and optional `inner_folds`. An inner fold contains `inner_fold_id`, `train_ids`, and `validation_ids`. IDs are observation IDs, never integer row positions. Repeat/fold identifiers are strings and form a unique pair. Each list has unique IDs and deterministic sorting.

Train and test must jointly cover the complete cohort once within each outer fold. Inner train and validation must jointly cover exactly their outer training set. Unsupported exclusions require an explicitly curated cohort before planning; they must not be hidden inside assignments. Across ordinary outer CV folds, training sets overlap by design. Do not flag that as leakage. Within each repeat, every observation must occur in test exactly once for the complete-CV evaluator. Imported one-off holdout plans can be audited but are not evaluated as complete CV in v0.1.0.

Import outer-only TSV with exact columns `repeat_id`, `fold_id`, `role`, `observation_id`, where role is train or test. Reject duplicate memberships, additional columns, missing IDs and invalid roles. TSV does not express inner folds in v0.1.0; use JSON. Export `assignments.tsv` as a convenience view of outer folds. The plan JSON remains canonical.

## 5.3 Hashes and binding

Compute `cohort_digest` as SHA-256 of a deterministic UTF-8 JSON encoding of the role mapping and required metadata records sorted by observation ID, using compact separators, sorted object keys, and explicit nulls. Include mapped identity, target, session, site, phase, independence and covariate fields; exclude feature values and unrelated columns. Do not rely on Python's randomized hash or pandas object memory representation. Reordering rows must not change this digest; changing a mapped value must.

Compute a separate feature digest over explicit selected feature names and aligned values for evaluation provenance. Reject a split plan whose non-null cohort digest differs from the current data. Imported TSV may initially lack a digest; bind it only after validation and record its imported origin. A digest is an integrity aid, not anonymization and not proof that source data are authentic.

## 5.4 Audit report contract

Required top-level fields: `schema_version`, `tool_version`, `objective`, `execution_status`, `input_summary`, `checks`, `limitations`, `provenance`. `execution_status` is `completed`, `partial` or `blocked`. It describes technical coverage, not study validity. Completed reports may contain serious observed violations. Partial means one or more requested checks were unassessable while others ran. Blocked means a prerequisite prevented meaningful requested execution.

Each check requires `instance_id`, `rule_id`, `status`, `severity`, `evidence_kind`, `scope`, `message`, `recommendation`, and `evidence`. Severity is info, warning or error. Scope uses role names and fold identifiers without raw participant IDs by default. Evidence has a documented JSON-compatible structure, never a serialized dataframe or object repr. Sort checks by stable rule order, then fold and field, not hash iteration order.

The message for a clean partition should be “No participant overlap detected in this supplied split.” It must not be “Your experiment is leakage-free.” The unassessable preprocessing check remains present even when split checks pass.

## 5.5 Metrics and nulls

JSON must comply with standard JSON: no NaN, Infinity, negative Infinity or Python-specific literals. Undefined metric values are null accompanied by a reason code and denominator/coverage fields. A numeric zero is a real score, not a missing result. Probabilities retain enough precision for reproducible scoring; display rounding is separate.

Record global class order, binary positive class when applicable, metric unit, participant and observation counts, per-fold class support, folds attempted/completed, failed folds, and whether the run is diagnostic-invalid-for-the-stated-objective. Timestamps, elapsed time and machine descriptors belong in a separate provenance block and are excluded from deterministic numerical equality assertions.

## 5.6 Forward compatibility

Do not reinterpret an existing rule ID or enum value in a patch release. Unknown schema major versions fail with a migration message. New optional fields require schema tests and a migration note. `additionalProperties: false` is the default for structural objects; tightly defined evidence objects may permit JSON-compatible additions only where the corresponding schema explicitly says so.

The master specification, schemas and examples must be checked for drift. A change to one requires updating the others plus contract tests in the same stage.
