# Synthetic test fixtures

All people, observations, values and sites here are fictitious. These small tables are contract inputs and independent known-answer expectations. They exercise input contracts and validation behavior, rather than measure performance on real studies.

The clean cohort has 18 participants, two visits each, two classes and three sites. The clean 3-fold plan is participant-disjoint; the leaky 2-fold plan splits visits so every person crosses train/test. The shuffled feature table tests a keyed join. Target-changing and cross-site variants test explicit scope/feasibility behavior. The global-PCA ledger is a declared-history test. The example public report tests a schema only and is labeled accordingly.

`config_invalid_unknown_key.json` is intentionally structurally invalid. `splits_unknown_id.json` is structurally valid JSON but intentionally semantically invalid for the cohort. A validator must distinguish these two failure classes.

These files can be committed as synthetic tests. Never replace them with restricted ADNI, AIBL or identifiable clinical records.
