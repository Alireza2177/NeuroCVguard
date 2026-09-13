# 12 — Design comparisons and intentional negative examples

## 12.1 API meaning

`compare_designs(results)` creates a side-by-side comparison of completed EvaluationResult objects. It does not choose a winning evaluation design and does not train extra models. Display each design's objective, cohort/feature identity, folds, participants, observations, class support, training-size ranges, model specification, metric unit, diagnostic status and upstream limitations.

Show a numeric delta only when both values are defined and feature/cohort digests, class definitions and metric units match. Otherwise show null with explicit mismatch reasons. Even matching IDs do not establish causal comparability: site-held-out and subject-held-out fits can have different training distributions. Preserve these design differences beside any number.

## 12.2 Narrow diagnostic exception

The educational row-random example partitions observations with StratifiedKFold and can place a participant on both sides. It is deliberately invalid for the unseen-participant objective. It is never the default generator and must never be offered as a recommended fix.

The evaluator may run a plan with participant overlap only when `evaluation.diagnostic_allow_subject_overlap=true`, the configured objective is unseen_participant, no extra independence columns are declared, every observation is still disjoint between train/test, and all other structural/class constraints hold. The output is prominently `diagnostic_only=true`, `valid_for_objective=false`, and “Do not report as evidence for unseen-participant generalization.” This switch cannot waive site/phase violations, family overlap requirements, unknown IDs, duplicated observations across roles, class failure or missing mandatory information.

For diagnostic row-random complete CV, each observation still receives exactly one out-of-fold prediction. A participant can appear in several test folds; aggregate all its held-out observation probabilities into one diagnostic participant vector. Explicitly state that grouping these scores does not remove the training leakage already present. Participant-level aggregation is not a repair.

## 12.3 Scientific interpretation

Call the difference `score_difference`, not `leakage_amount` or `corrected_accuracy`. Report signed differences in metric units; display percentage points when multiplying a [0,1] metric by 100 and label that transformation. Do not force a positive difference or report a negative value as zero.

A simple result can say: “The observation-random design scored 0.12 higher than the participant-disjoint design in this synthetic scenario. The former violated participant separation. These estimates differ in design and must not be treated as a causal estimate for an unrelated real dataset.” Example numbers in documentation must be produced by actual runs or clearly marked hypothetical; the release demo must use recorded outputs.

## 12.4 No fragile performance assertions

The unit suite checks correct memberships, correct reference metrics, validity flags, preservation of negative differences, and warnings. It does not require every random synthetic seed to produce a larger naive score. A selected pedagogical scenario may show an effect, but all simulation parameters and seeds must be public, and the documentation must not imply the illustration establishes a universal effect size.

Paired inferential testing, cluster bootstrap confidence intervals, repeated-CV uncertainty, leakage severity curves and independent external holdouts belong to a later research plan with a predeclared estimand. They must not enter the product merely to create a publishable-looking table.
