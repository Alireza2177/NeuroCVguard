# 20 — Cross-contract clarifications and precedence

This chapter fixes details that otherwise tend to drift when separate agents implement different modules. It is normative, not optional commentary.

## 20.1 Public reports versus operational evaluation records

The evaluator CLI writes `evaluation.private.json` as a sensitive local operational record containing integrity digests, actual fold/fit metadata and the structured evaluation values needed for reproducibility. It separately writes privacy-projected `report.json` and `report.html`. The CLI warns that the private file is not a public-sharing artifact. The `compare --result name=path` command consumes evaluation.private.json, not the stripped public report. Reject an incomplete public projection with a clear instruction instead of guessing missing digests or fit metadata.

`write_report()` writes only privacy-projected report artifacts unless sensitive_details was explicitly requested. A public model `.to_dict(sensitive_details=False)` follows that policy. The evaluator has a distinct `.to_operational_dict()` for its private record. SplitPlan serialization is always an operational identity-bearing artifact, and is named/documented as such. Do not conflate these serialization methods.

A public evaluation report uses the same AuditReport envelope schema with a `result_type` value and an optional schema-validated `evaluation_summary` or `comparison_summary`. The private EvaluationResult schema is separate. Every result must include the applicable scientific limitations; the renderer must not accept arbitrary loosely typed HTML fragments.

## 20.2 Imported plans

SplitPlan carries an `origin` field equal to imported or generated. Imported plans may initially have a null cohort_digest; after successful identity validation, create a bound copy with the current digest and retain origin=imported. Generated plans require a non-null digest and a deterministic hash-derived plan_id. An imported plan_id can be a user label matching the documented safe string pattern. A null seed is allowed for imported assignments whose seed is unknown.

A complete-CV evaluator requires at least two outer folds, exactly one repeat and test coverage exactly once per observation. One-fold holdout plans are auditable, not complete-CV runs. The structural schema permits them so auditing is not artificially restricted.

## 20.3 Metric and report schemas

Metric values carry value (number or null), reason (null for defined values) and n. MetricSet includes accuracy, balanced_accuracy, macro_f1, roc_auc, per_class and confusion_matrix. Runtime validators enforce matrix size/class alignment and meaningful null reasons beyond what JSON Schema alone can express.

All schema references must resolve locally from packaged schemas. No runtime network fetch is allowed. An evaluator's public summary strips raw fit IDs/digests and uses only the explicit allowed summary fields. A comparison's public summary carries design names, objectives, metric values/deltas and explanations, not private data keys.

## 20.4 Configuration and error precedence

Optional `evaluation.positive_class` defaults to null. Binary AUC stays null without an explicit positive class, while other valid metrics still compute. The standard configuration example omitting that optional key is valid. Unknown optional keys are still rejected.

An error in invocation, JSON syntax, duplicate JSON key or schema structure is CLI code 2. A well-formed split with an observed design violation can be audited and written, then yields code 3 under the default fail-on=error. A planner/evaluator that refuses a scientifically infeasible well-formed request yields code 3 before fitting. A fit that starts and fails yields code 4. Do not turn malformed input into a fake completed scientific audit.

## 20.5 Check coverage and result aggregation

Compute checks on unprojected valid data, then project the report. A privacy-suppressed cell cannot change a split verdict or statistic internally. A failed check may have evidence_kind=declared; no wording may portray it as observed history. Not_assessable is always included in limitations/coverage, not silently dropped by severity filters.

The first version does not support repeated-CV evaluation, holdout-only scoring, target-changing longitudinal classification or nonclassification outcomes. Report these as explicit scope limits, not implementation bugs to work around automatically. They remain auditable where the available information supports a narrower check.

## 20.6 Input-size option

`limits.max_input_mb` is an optional positive integer, default 128, bounding each local input file before parsing. It is separate from max_dense_mb, which is an approximate numeric matrix allocation guard. The strict schema recognizes this optional key; the minimal configuration example is valid without it. All resource values are implementation guardrails, not medical/scientific thresholds.


## 20.7 Public metric privacy

A public evaluation summary may include fold_metrics and metrics_hidden_reason. If a confusion table has a positive cell below the report suppression threshold, hide that entire public MetricSet (set it to null) and record privacy_small_cells. Do not leave enough per-class support, confusion cells or derived scores in another public field to reconstruct the hidden table. The private evaluation record retains complete metrics for authorized local use.

Apply the same rule to public comparison metrics and derived deltas. Acquisition tables follow chapter 13. Counts of observations/participants and class names remain summary information, so the software still does not promise formal anonymization. A user can explicitly request a sensitive local detailed report. Synthetic demos may explicitly enable details because their generator creates fictitious data; they must label that choice and never infer synthetic status from an arbitrary input filename.

Public report schema summary fields are projections, not substitutes for private operational evaluation records. Per-fold public metrics are included when available and not suppressed. A hidden metric and a mathematically undefined metric have different reason strings and must be explained differently.

## 20.8 Private evaluated-plan retention (approved ADR-S10-001)

The private evaluation schema additionally permits paired optional `plan_digest`
and `actual_plan` fields. `actual_plan` follows the complete split-plan contract;
`plan_digest` is SHA-256 of its canonical operational JSON. The controlled runner
always emits both, including for incomplete runs. Its fold references, objective,
cohort digest and recorded fit memberships must agree with the retained plan.
Neither field is included in the public report projection.

Existing schema 1.0 records without both fields remain readable by the updated
reader and must not be assigned invented memberships or digests. Older readers
with the original closed schema reject extended records; update those readers.
This additive extension resolves the missing plan provenance required by §11.8.
It changes no scientific rule and does not authenticate imported history.
