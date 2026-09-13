# 09 — Acquisition and target association diagnostics

## 9.1 Descriptive, not causal

The first release provides categorical distribution tables and Cramer's V, not a statistical test of causal confounding. Relevant fields are site, phase and explicitly declared categorical covariates such as scanner model. Use SciPy's documented association calculation rather than introducing a novel correction [R08]. A separate existing project, mlconfound, provides specialized tests concerning confounders and predictions; NeuroCVguard must acknowledge that adjacent work and must not imply equivalent inferential functionality [R09].

## 9.2 Unit of analysis

Construct one record per participant for each field–target pair. Both target and the chosen field must be constant within each participant for that participant-level diagnostic. If either varies for any participant, mark the requested pair not_assessable with a reason rather than arbitrarily selecting a visit or silently excluding the difficult people. Audit descriptive observation counts separately without using them as independent evidence.

For missing covariate values, a complete-pair descriptive calculation is allowed only with the original/complete/excluded participant counts recorded. It does not modify the cohort or split. Missing target values prevent classification/split generation; descriptive complete-pair association must clearly disclose them. Additional protected relationships do not turn family members into independent samples; because v0.1.0 performs no inferential test, describe the counting unit without claiming independence for a p-value.

## 9.3 Exact statistic

Create the observed contingency table with sorted string levels. Remove unused categories that have zero marginal support, but do not erase observed zero cells. Require at least two non-empty categories on each axis and a positive total. Compute:

`scipy.stats.contingency.association(table, method="cramer", correction=False)`.

For explanation, this is V = sqrt(chi_squared / (n * min(r-1, c-1))) using Pearson's uncorrected chi-square statistic. `correction=False` is not a small-sample bias-corrected Cramer's V. Label the estimator exactly. Constant axes return null with reason `constant_variable`, not zero. Non-finite results are errors to investigate, not values to display.

No p-value is generated in v0.1.0. Do not use a naive row-wise permutation on repeated observations. Inferential tests require a separate exchangeability design and review.

## 9.4 Review warnings

When V is at or above `association.review_threshold`, emit “Acquisition/target association warrants review under the stated generalization objective.” Do not say “The model is biased,” “Leakage detected,” or “Disease is caused by site.” The default 0.3 is an operational review threshold, not a universal effect-size classification or an evidence-based clinical cutoff.

Flag observed or expected cell counts below `association.min_cell_count` and show that sparse samples can make descriptive estimates unstable. Do not attach significance stars. If a field has more than 100 observed levels, skip the table/statistic with `too_many_categories` and suggest reviewing whether this is an identifier. Do not silently bin categories or combine rare sites into an artificial Other class.

## 9.5 Known-answer tests

A 2×2 table [[5,5],[5,5]] gives V=0 within numerical tolerance. [[10,0],[0,10]] gives V=1. A one-category axis is not_assessable. Repeating each participant's row ten times must not change a participant-level table or V. A participant with different sites across visits makes that pair unassessable rather than contributing two independent records. Renaming category labels must not change the statistic. Permuting input rows must not change table values or ordering conventions.

Sparse privacy suppression applies only to exported display/projection, not to the internal mathematical calculation. A suppressed report must not reveal the omitted table through embedded JSON or hidden HTML fields.
