# Configuration reference

Source: `contracts/config.schema.json` and `neurocvguard.config.AuditConfig`.
Verified by `tests/test_documentation.py` and the strict config/contract tests.

JSON input requires every required field. Constructor/starter defaults below
are not missing-key fallbacks. Only `evaluation.positive_class` and
`limits.max_input_mb` may be omitted. Unknown/duplicate keys and booleans
used as numbers fail. Resource quantities in MB use 1024² bytes.

| Key | Default in starter | Structural type and constraints | Required in JSON |
|---|---|---|---|
| `schema_version` | `"1.0"` | `{"const": "1.0"}` | True |
| `columns.observation_id` | `"observation_id"` | `{"type": "string", "minLength": 1}` | True |
| `columns.subject_id` | `"subject_id"` | `{"type": "string", "minLength": 1}` | True |
| `columns.target` | `"diagnosis"` | `{"type": ["string", "null"]}` | True |
| `columns.session` | `"session_id"` | `{"type": ["string", "null"]}` | True |
| `columns.site` | `"site"` | `{"type": ["string", "null"]}` | True |
| `columns.phase` | `null` | `{"type": ["string", "null"]}` | True |
| `columns.independence` | `[]` | `{"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 0, "uniqueItems": true}` | True |
| `columns.categorical_covariates` | `[]` | `{"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 0, "uniqueItems": true}` | True |
| `study.objective` | `"unseen_participant"` | `{"enum": ["unseen_participant", "unseen_site", "unseen_phase", "audit_only"]}` | True |
| `split.scheme` | `"subject_kfold"` | `{"enum": ["subject_kfold", "leave_one_site_out", "leave_one_phase_out", "imported"]}` | True |
| `split.n_splits` | `3` | `{"type": ["integer", "null"], "minimum": 2, "maximum": 20}` | True |
| `split.seed` | `2026` | `{"type": "integer", "minimum": 0, "maximum": 4294967295}` | True |
| `association.review_threshold` | `0.3` | `{"type": "number", "minimum": 0, "maximum": 1}` | True |
| `association.min_cell_count` | `5` | `{"type": "integer", "minimum": 1}` | True |
| `evaluation.feature_columns` | `["feature_1", "feature_2"]` | `{"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 0, "uniqueItems": true}` | True |
| `evaluation.tune` | `false` | `{"type": "boolean"}` | True |
| `evaluation.C` | `1.0` | `{"type": "number", "exclusiveMinimum": 0}` | True |
| `evaluation.C_grid` | `[0.1, 1.0, 10.0]` | `{"type": "array", "items": {"type": "number", "exclusiveMinimum": 0}, "minItems": 1, "uniqueItems": true}` | True |
| `evaluation.inner_splits` | `3` | `{"type": "integer", "minimum": 2, "maximum": 20}` | True |
| `evaluation.max_iter` | `2000` | `{"type": "integer", "minimum": 1}` | True |
| `evaluation.diagnostic_allow_subject_overlap` | `false` | `{"type": "boolean"}` | True |
| `evaluation.positive_class` | `null` | `{"type": ["string", "null"]}` | False |
| `report.sensitive_details` | `false` | `{"type": "boolean"}` | True |
| `report.small_cell_threshold` | `5` | `{"type": "integer", "minimum": 2}` | True |
| `limits.max_rows` | `100000` | `{"type": "integer", "minimum": 1}` | True |
| `limits.max_features` | `10000` | `{"type": "integer", "minimum": 1}` | True |
| `limits.max_dense_mb` | `512` | `{"type": "integer", "minimum": 1}` | True |
| `limits.max_input_mb` | `128` | `{"type": "integer", "minimum": 1}` | False |

## Meaning and semantic constraints

`schema_version` is the string 1.0. `columns` maps actual input names:
observation/participant IDs are mandatory; null optional roles mean absent.
Scalar roles must differ. Independence columns connect participants by
transitive equality within each field; categorical covariates feed descriptive
association diagnostics. Feature names must be explicit and exclude every role,
protected field and covariate. Empty features are allowed for inventory only.

`study.objective` specifies the generalization claim. `split.scheme` must match
that objective except under audit_only; imported plans are independently checked.
`n_splits` must be an integer for subject_kfold and null otherwise. The seed is
fixed explicitly, never searched. See [objectives](objectives.md).

`association.review_threshold` flags descriptive Cramer's V for review; it is
not a causal threshold. `min_cell_count` flags sparse observed/expected tables.

`evaluation.C` is fixed inverse regularization strength when tune=false.
With tune=true, C_grid candidates use participant-aware inner_splits and
balanced accuracy; max_iter bounds logistic fitting. Positive_class explicitly
defines binary AUC; null leaves binary AUC undefined. Diagnostic subject overlap
is narrowly limited to imported unseen-participant plans without protected
relationships or tuning; it never waives observation overlap or domain rules.
See [evaluation](evaluation.md) and [comparison](comparison.md).

`report.sensitive_details` explicitly enables sensitive local reporting.
`small_cell_threshold` suppresses public cells/linked metric sets; it never
changes scientific calculations. The root write_report API uses its own explicit
sensitive_details argument and default threshold; see [reporting](reporting.md).

`limits.max_rows` bounds observations; max_features bounds selected predictors;
max_dense_mb bounds estimated float64 rows × features storage before allocation;
max_input_mb bounds each file before parsing. These are guardrails, not an upper
bound on total process memory. Limits never authorize silently truncating data.
