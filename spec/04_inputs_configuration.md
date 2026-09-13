# 04 — Input tables and configuration contract

## 4.1 Formats and identities

Accept local uncompressed `.csv` and `.tsv` text files encoded as UTF-8 or UTF-8 with BOM. Choose delimiter from extension; do not guess formats from arbitrary content. Forbid duplicate headers before a dataframe library can rename them. Reject malformed records and duplicate observation IDs. Do not load Excel workbooks, arbitrary archives, URLs, pickle files, joblib objects or serialized Python code in v0.1.0.

Each observation has a non-empty, globally unique string key. Every observation has a non-empty participant key. Read identity and categorical columns as strings: `001` and `1` are different IDs. Do not automatically strip `sub-`, collapse case, normalize Unicode, concatenate site to participant ID, or trim whitespace. Reject leading/trailing whitespace and control characters in identity fields with a useful repair instruction. Preserve other legitimate Unicode. DataFrame callers must provide string identity columns; refuse lossy automatic conversions.

`subject_id` must mean the same physical person throughout the supplied cohort, including across sites. The software cannot resolve a person assigned unrelated aliases. Warn users to resolve source namespaces upstream. If unrelated source datasets reuse `001`, an explicit, documented global identity mapping is needed. Blindly prefixing the acquisition site can hide a traveling participant and is not a general remedy.

## 4.2 Required and optional roles

`columns.observation_id` and `columns.subject_id` are mandatory role mappings. `target` is required for classification/split stratification but may be null for an audit-only inventory. `session`, `site` and `phase` may be null when not supplied. `independence` is a list of additional source columns whose equal values connect participants into protected components. `categorical_covariates` is an explicit list; no automatic classification of every numeric column as a scanner or clinical variable.

Default missing tokens in text input are exactly `""` and `"n/a"`. Do not use pandas' broad default NA vocabulary because an identifier such as `NA` may be real. JSON null and pandas missing scalars are missing in their respective APIs. A missing participant or observation ID is fatal. A missing optional field produces documented incomplete coverage. A missing value in a declared independence column blocks strict splitting/evaluation, because the relationship cannot be verified; do not connect all missing values together or silently regard them as unrelated.

No cohort row is dropped automatically for missing target, site, features, or metadata. Describe the problem and require an explicit upstream inclusion decision. The original and curated cohort must remain separately traceable.

## 4.3 Feature table

A feature table contains the same configured observation-key column and explicitly selected numeric feature columns. It has one record per cohort observation. Join by observation key with validated one-to-one cardinality, never by row order or dataframe index. Missing IDs, extra IDs, duplicates or ambiguous joins are errors; there is no silent intersection. Feature-table row order may differ.

Predictors are an explicit non-empty list under `evaluation.feature_columns`. Reject any selected role column, any independence/categorical-covariate column, a selected duplicate name, and the target column. No “all numeric columns” fallback is allowed. Coerce declared feature cells to finite floats or recognized missing values; reject text and infinity. Entirely missing training-fold features remain representable through the prescribed imputer; missing values alone do not authorize global imputation.

The tool cannot prove that a column with an innocent name is not a target proxy or globally derived feature. Feature selection by explicit name is a guardrail, not a completeness guarantee.

## 4.4 Configuration model

Use strict JSON, schema version `1.0`. Unknown keys fail. Reject bool where an integer is required. Configuration carries behavior, not executable expressions. File paths are supplied as CLI/API arguments, not embedded execution hooks. Paths passed on the command line are resolved relative to the current working directory; log sanitized basenames and preserve full paths only in a local private manifest when explicitly requested.

The accompanying `contracts/config.schema.json` is the structural contract. Runtime semantic validation adds role-existence, role-collision and cross-field checks. Required defaults are:

```json
{
  "schema_version": "1.0",
  "columns": {
    "observation_id": "observation_id",
    "subject_id": "subject_id",
    "target": "diagnosis",
    "session": "session_id",
    "site": "site",
    "phase": null,
    "independence": [],
    "categorical_covariates": []
  },
  "study": {"objective": "unseen_participant"},
  "split": {"scheme": "subject_kfold", "n_splits": 3, "seed": 2026},
  "association": {"review_threshold": 0.3, "min_cell_count": 5},
  "evaluation": {
    "feature_columns": ["feature_1", "feature_2"],
    "tune": false,
    "C": 1.0,
    "C_grid": [0.1, 1.0, 10.0],
    "inner_splits": 3,
    "max_iter": 2000,
    "diagnostic_allow_subject_overlap": false
  },
  "report": {"sensitive_details": false, "small_cell_threshold": 5},
  "limits": {"max_rows": 100000, "max_features": 10000, "max_dense_mb": 512}
}
```

These numbers are software defaults and resource guardrails, not validated scientific thresholds. The 0.3 association review threshold is configurable and never converted to a diagnosis of causal bias.

`split.scheme` is `subject_kfold`, `leave_one_site_out`, `leave_one_phase_out`, or `imported`. `n_splits` is an integer from 2 to 20 only for subject_kfold and is null otherwise. Domain schemes must match the stated domain objective; subject_kfold requires unseen_participant. Imported plans are checked against the selected objective. An audit-only call may carry a split config but must not generate/evaluate a plan until a supported objective is selected.

## 4.5 Limits and errors

Check file size and declared dimensions before large allocations. Estimate dense numeric storage from row count × feature count × dtype size and reject work above the configured guardrail before constructing unnecessary copies. Values may be raised explicitly; report actual dimensions and measured resource use in benchmarks. Do not claim this estimate bounds total process memory.

Error text should say what is wrong, which role or column is affected, how many rows are involved and how to resolve it. Default errors must not echo raw participant IDs or feature values. `--debug` enables a traceback, not blanket sensitive-data logging.

## 4.6 Neuroimaging interoperability

Accept ordinary exported neuroimaging feature tables without imposing an atlas or pipeline. Document `participant_id` and `session_id` mapping for BIDS-style tables. A BIDS participants file normally describes participants rather than every scan; the tool must not invent visit-level rows from it [R07]. Users provide a harmonized observation manifest when multiple scans or sessions exist. Label reading this table as “BIDS-style column mapping,” not full BIDS validation or derivative provenance verification.
