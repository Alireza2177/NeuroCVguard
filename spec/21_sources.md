# 21 — Source register and evidence boundaries

All sources were consulted on **12 September 2026**. Live documentation can change. Verify APIs in the supported environment and re-check publication rules at submission time. These sources support background and established primitives, not a claim that the proposed package has been implemented or validated.

## R01 — OpenAI — Custom instructions with AGENTS.md

Source: https://developers.openai.com/codex/guides/agents-md/

Use in this foundation: Project instruction loading and bounded instruction size; motivates short AGENTS plus explicit stage documents.

## R02 — OpenAI — Codex prompting guidance

Source: https://developers.openai.com/codex/prompting/

Use in this foundation: Official task-context and implementation guidance; does not guarantee autonomous correctness.

## R03 — scikit-learn — Common pitfalls and recommended practices

Source: https://scikit-learn.org/stable/common_pitfalls.html

Use in this foundation: Background for data-dependent preprocessing boundaries and data leakage.

## R04 — scikit-learn — StratifiedGroupKFold

Source: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html

Use in this foundation: Established grouped stratification primitive; project adds explicit identity and feasibility rules.

## R05 — scikit-learn — Pipeline

Source: https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html

Use in this foundation: Established transformation/estimator composition; not proof of unknown upstream history.

## R06 — scikit-learn — LeaveOneGroupOut

Source: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html

Use in this foundation: Established group holdout primitive.

## R07 — BIDS specification — Data summary files

Source: https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/data-summary-files.html

Use in this foundation: Participant and related tabular conventions; not a new BIDS validation claim.

## R08 — SciPy — contingency.association

Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.association.html

Use in this foundation: Documented categorical association implementation and terminology.

## R09 — mlconfound — Project documentation

Source: https://mlconfound.readthedocs.io/

Use in this foundation: Adjacent confound/prediction-testing software; relevant prior work, not replaced here.

## R10 — Python Packaging Authority — Packaging Python Projects

Source: https://packaging.python.org/en/latest/tutorials/packaging-projects/

Use in this foundation: Conventional package layout, build and distribution practices.

## R11 — Python Packaging Authority — Writing pyproject.toml

Source: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

Use in this foundation: Standard package metadata/configuration.

## R12 — pytest — Good integration practices

Source: https://docs.pytest.org/en/stable/explanation/goodpractices.html

Use in this foundation: Test organization and installation conventions.

## R13 — Hypothesis — Official documentation

Source: https://hypothesis.readthedocs.io/en/latest/

Use in this foundation: Property-based testing tool reference.

## R14 — Sphinx — Getting started

Source: https://www.sphinx-doc.org/en/master/usage/quickstart.html

Use in this foundation: Standard documentation build and structure.

## R15 — GitHub Docs — Secure use reference

Source: https://docs.github.com/en/actions/reference/security/secure-use

Use in this foundation: Workflow permissions and security practices.

## R16 — PyPI — Trusted Publishing

Source: https://docs.pypi.org/trusted-publishers/

Use in this foundation: Publication authentication mechanism; requires actual owner configuration.

## R17 — Rosenblatt et al. (2024) — Data leakage inflates prediction performance in connectome-based machine learning models

Source: https://www.nature.com/articles/s41467-024-46150-w

Use in this foundation: Direct prior empirical work on leakage in neuroimaging; effects should not be presumed identical across mechanisms. DOI: 10.1038/s41467-024-46150-w.

## R18 — JOSS — AI usage and other policies

Source: https://joss.readthedocs.io/en/latest/policies.html

Use in this foundation: Current disclosure and human-accountability requirements; re-check before submission.

## R19 — JOSS — Submitting a paper: scope and significance

Source: https://joss.readthedocs.io/en/latest/submitting.html

Use in this foundation: Current public-history and research-impact requirements; no promise of eligibility/acceptance.

## R20 — scikit-learn — SimpleImputer

Source: https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html

Use in this foundation: Training-fold missing-value handling and keep_empty_features behavior.

## R21 — scikit-learn — LogisticRegression

Source: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

Use in this foundation: Baseline estimator API, solver and sample-weight support.

## R22 — scikit-learn — roc_auc_score

Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html

Use in this foundation: Probability ordering and AUC variants.

## R23 — scikit-learn — Metrics and scoring

Source: https://scikit-learn.org/stable/modules/model_evaluation.html

Use in this foundation: Metric primitives; the complete-class null policy here is an explicit project decision.

## R24 — Spisak (2022) — Statistical quantification of confounding bias in machine learning models

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC9412867/

Use in this foundation: Prior inferential confound-testing work associated with mlconfound. DOI: 10.1093/gigascience/giac082.
