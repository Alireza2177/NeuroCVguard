# Strict local cohort and feature input

Use `neurocvguard.load_cohort(metadata, *, config, features=None)` to read local tables.
Inputs are local uncompressed CSV/TSV files or scalar pandas DataFrames. File
delimiters follow their extensions; UTF-8 with or without BOM is accepted.
No URLs, Excel, archives, pickle/joblib, downloads or format guessing are supported.

From the repository root, this loads the supplied synthetic fixtures:

```python
from neurocvguard import load_cohort
from neurocvguard.config import load_config
from neurocvguard.io import cohort_digest, feature_digest

config = load_config("fixtures/config.json")
cohort = load_cohort(
    "fixtures/cohort_clean.tsv",
    config=config,
    features="fixtures/features_shuffled.tsv",
)
assert tuple(cohort.features[config.columns.observation_id]) == cohort.observation_order
metadata_integrity = cohort_digest(cohort)
feature_integrity = feature_digest(cohort)
```

Map roles explicitly in config. Required observation and participant identities
must be nonempty strings without surrounding whitespace or control characters.
`001`, `1`, `sub-1` and distinct Unicode spellings remain distinct. File missing
tokens are exactly empty text and `n/a`; `NA` is a legitimate string. DataFrame
missing scalars are also supported. Numeric identity/categorical columns are
rejected rather than converted. Optional absent fields remain absent so audits
report incomplete coverage; missing protected relationships still block strict
planning through the existing component checks. No observation is silently dropped.

Feature names must be explicitly selected and cannot be mapped roles, target,
protected relationships or declared categorical covariates. Feature rows must have
exactly the cohort key set with one row per key. Missing/extra/duplicate keys fail;
row order and DataFrame index never determine alignment. Selected cells become
finite floats or missing values. Text, infinity, booleans and complex values are
rejected. Entirely missing features remain missing; loading performs no fitting,
normalization, imputation or outcome-dependent filtering.

The loader preserves metadata observation order and owns detached table copies.
Digest serialization sorts by key, so row reordering does not change either hash.
The metadata digest includes mapped roles only; the feature digest includes
explicit feature names, observation keys and aligned values, with missing values
encoded as JSON null. Digests and in-memory tables remain sensitive, not anonymized.

Input bytes and row counts are bounded. Selected feature count and approximate
float64 matrix size are checked before avoidable frame/dense copies; these are
allocation guardrails, not total-process memory guarantees. Limits may be raised
explicitly after reviewing the dataset. Errors report roles/counts and repair
instructions without echoing row values.

Global participant identity remains the caller's responsibility. Do not blindly
prefix site names to IDs: a traveling participant must remain one person. For
BIDS-style exports, map participant/session columns explicitly and supply an
observation manifest; this is not full BIDS validation or scan discovery.
