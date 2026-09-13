# 11 — Controlled classification baseline and nested tuning

## 11.1 Why the evaluator is deliberately small

The evaluator demonstrates an auditable workflow, not competitive disease diagnosis. It consumes a validated cohort, explicitly selected numeric features and a complete outer-CV plan with exactly one repeat. It supports binary/multiclass classification only, requires constant target per participant, and uses a fixed family of logistic-regression pipelines. Audit-only users need not run it.

Do not implement an arbitrary estimator factory from config strings. Python users may inspect/use generated splits in their own code, but v0.1.0 controlled evaluation is the specified baseline. Do not load a pickled estimator or arbitrary module named in a config file.

## 11.2 Preflight

Before fitting, validate keyed feature alignment, explicit feature roles, finite numeric values/missing tokens, resource limits, split digest, complete per-repeat test coverage and all mandatory separation checks. Verify that each training fold contains every global class. Verify one target per participant. Reject more than one repeat and one-off holdout evaluation with an actionable UnsupportedDesignError; their partition audit remains supported.

Ordinary evaluation refuses participant/component/domain overlap. The diagnostic exception in chapter 12 is narrow and never overrides observation overlap, unknown IDs, invalid features or class-training impossibility. No partial successful-looking benchmark may be produced from structurally invalid partitions.

## 11.3 Pipeline

Construct a fresh sklearn Pipeline for every fit:

1. `SimpleImputer(strategy="median", keep_empty_features=True)`.
2. `StandardScaler()`.
3. `LogisticRegression(C=<chosen>, solver="lbfgs", max_iter=<configured>, random_state=<seed>)`.

Use the installed supported API, not deprecated parameters copied from old examples. Stage S00 records the exercised versions. Missing entire training-fold features are handled by the documented imputer behavior, with a diagnostic that the feature supplied no training information. Do not fit any component globally before the outer or inner loop.

Provide classifier loss weights of `1 / number_of_training_observations_for_that_participant` through the classifier step's sample_weight parameter, so each training participant has equal total loss weight. Record that imputation and scaling are still fitted on training observations rather than subject-weighted statistics. Do not claim every part of the pipeline is participant-balanced. All weights use the current fitting subset only; no test distribution enters their calculation.

Default class_weight is None. Adding class weighting changes the objective and is a future explicit configuration decision. The initial C is 1.0 unless configured. There is no feature selection, PCA, harmonization, resampling, threshold optimization, probability calibration or model selection beyond the permitted C grid.

## 11.4 Fit execution and failure

Process folds in deterministic order. Clone the pipeline for each outer fit. Slice by observation IDs, not positional assumptions. Record actual training/test IDs internally, class order, seed and environment; restrict public output according to privacy settings. Train once, then predict held-out probabilities. Map estimator classes to the global class order explicitly.

Do not catch ConvergenceWarning and silently continue as a successful result. Mark a non-converged fit as failed with a recommendation to review scale/iterations. Do not automatically raise max_iter until the warning disappears. Other expected fitting errors produce a failed fold with a precise reason; unexpected errors remain visible.

If any required outer fold fails, set the evaluation status incomplete and do not show an aggregate complete-CV score. Per-fold diagnostics and completed-fold outputs may be retained under clearly incomplete sections. Do not silently average only the easy folds.

## 11.5 Participant-level predictions

The primary metric unit is participant. For each participant in the outer test set, arithmetic-mean the probability vectors across that participant's test observations, then choose the class with highest mean probability. A tie resolves using the recorded global class order. Because targets must be constant, participant truth is unambiguous.

In ordinary group-disjoint complete CV, each participant is tested in one outer fold. Verify this independently. Collect exactly one out-of-fold probability vector per participant across the complete run. Also provide clearly labeled observation-level diagnostics if useful, but never mix observation and participant denominators.

Default global class order is lexicographically sorted target strings. Binary positive class must be explicitly configured via optional `evaluation.positive_class`; if absent, binary AUC is null with reason `positive_class_unspecified`. Class labels and their order are always written to the result.

## 11.6 Metric definitions

Required metrics are accuracy, balanced accuracy, macro-F1, per-class support/recall, confusion matrix, and ROC-AUC where defined. Accuracy is defined for any non-empty scored set. Balanced accuracy is the mean recall across the **entire declared class set**, and is null if any required class has zero true support in the scored set. Macro-F1 follows the same class-coverage requirement; a supported class that is never predicted has F1=0, not null.

Use sklearn metric primitives with explicit labels and probability ordering. Binary AUC requires an explicit positive class and both true classes. Multiclass AUC uses macro one-vs-rest only when all global classes have support and the full probability matrix is available. An undefined metric is null plus a reason; do not coerce undefined values to zero or pretend that a single-class test fold has an ordinary AUC.

For a complete run, compute pooled participant-level metrics from all out-of-fold predictions. Fold-level metrics are supplementary and retain their coverage limitations. Do not calculate a conventional confidence interval by treating folds as independent observations. No inferential CI or p-value is part of v0.1.0.

## 11.7 Optional nested C selection

When tune=false, skip all inner splits. When tune=true, use inner splits already present in the plan or generate participant/component-disjoint inner folds from the outer training subset only using the configured inner_splits. Use the same participant-level construction as ordinary subject_kfold. Store actual generated inner memberships in the evaluation provenance/derived plan. Do not mutate the originally supplied plan in place.

Use an explicit small loop over the sorted unique positive C_grid values rather than a generic AutoML engine. For each candidate, fit fresh pipelines on each inner training subset and predict inner validation. Aggregate inner out-of-fold probabilities at participant level and compute pooled balanced accuracy across outer-training participants. All candidates use exactly the same inner memberships. If required inner fitting fails, tuning for that outer fold fails; no silent default-C fallback.

Choose the candidate with maximum pooled inner balanced accuracy. Treat scores within 1e-12 as tied and choose the smallest C. Record all candidate scores and tie resolution. Refit a fresh pipeline at that C on the full outer training subset, then predict the untouched outer test data. Outer test labels/scores cannot choose C, preprocessing or stopping rules.

Tests must use a memorizing/spying transformer to catch any fit on inner validation or outer test rows, and a case where a global scaler would differ from the training-only scaler. Test that every candidate uses a fresh object, folds have fresh estimators, and input arrays are not mutated.

## 11.8 Outputs

The structured evaluation result contains plan/config/feature digests, feature names, target ordering, actual folds, fit events, candidate selections, per-fold metric records, pooled metrics if complete, counts, convergence/failure reasons, limitations and an explicit `diagnostic_only` flag. Sensitive out-of-fold records may be written only to a requested local file and are excluded from the default HTML/public JSON projection.

Do not serialize fitted models by default. The purpose is auditability, not deployment. Production model training or clinical validation is outside this release.
