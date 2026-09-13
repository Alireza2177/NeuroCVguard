# 10 — Preprocessing declarations and observed fitting boundaries

## 10.1 Two different evidence sources

A feature CSV cannot reveal where an upstream transformation was fitted. Require reports to include an upstream limitation unless the relevant history is supplied, and continue to label imported history as declared. A column of PCA values is not sufficient to infer whether PCA was fit inside cross-validation.

The optional JSON preprocessing ledger records declarations, not executable operations. Each event identifies a transform, whether it learns from data, the relevant outer/inner fold, a declared fit scope and optional explicit fit observation IDs. The source is fixed to `user_declaration` for imported ledgers. An unknown scope is allowed and produces not_assessable evidence.

## 10.2 Ledger schema semantics

Top-level: schema_version and events. Event fields: event_id; transform; data_dependent; repeat_id; fold_id; inner_fold_id or null; fit_scope (`outer_train`, `inner_train`, `all_cohort`, `external`, `unknown`); fit_ids or null; uses_target; note. Unknown IDs or a scope inconsistent with the named fold make the declaration invalid. An `external` transform must not be automatically called safe: its source, overlap and deployment availability remain unassessable unless separately established.

For a declared data-dependent operation fitted on all_cohort, warn about declared global fitting. For explicit declared fit_ids outside the permitted training set, report a declared boundary violation. A declaration is not magically observed evidence simply because the ID sets can be compared.

For a data-independent row-local operation, such as a fixed unit conversion that learns nothing from the cohort, training isolation is not required on that basis. A user checking data_dependent=false is still a declaration, not proof. Do not mark every operation performed before splitting as leakage.

## 10.3 Controlled evaluator

The baseline runner captures observed events at actual fit call boundaries: the IDs provided to each pipeline fit, role (outer fitting or inner candidate fitting), model specification and fold. Record an event only when the call occurs; record failure if it fails. This proves the runner supplied the stated subset to that controlled pipeline. It does not prove all earlier feature extraction was isolated.

Use ordinary sklearn Pipeline with a fresh clone for each fit. Do not build a new branded LeakagePipeline that claims to guarantee everything. The test suite uses spy estimators/transformers or an instrumented pipeline factory to establish that validation and outer-test rows never reach fit/fit_transform in the controlled execution.

## 10.4 Block and report rules

A completed ordinary evaluation cannot have a known internal fit-boundary violation. Treat one as a defect and fail the run. Declared upstream global learning produces a warning and a conspicuous limitation; the baseline may still run to help inspect the experiment, but the report cannot promote its score as fully isolated. Include `upstream_preprocessing_verified=false` unless actual evidence supports a narrower statement, which v0.1.0 imported declarations do not.

Do not inspect arbitrary Python source with string matching and claim comprehensive leakage detection. Do not execute notebook cells or deserialize model files to discover provenance. Such functionality is outside scope and expands the threat model substantially.
