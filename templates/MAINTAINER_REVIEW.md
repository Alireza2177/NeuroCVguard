# Maintainer understanding and usability review

Before public release, the human maintainer should demonstrate the following with the real implementation and fixtures:

1. Explain why a repeated participant in the cohort is not automatically leakage, then identify an actual train/test overlap.
2. Explain why a traveling participant can make a strict site-held-out plan infeasible without dropping data.
3. Identify where each imputer/scaler/classifier is fitted in an outer and inner loop and show the corresponding test.
4. Explain a single-class test fold's undefined AUC and how the report represents it.
5. Find the sensitive operational outputs and explain why a suppressed public report is not a formal anonymization guarantee.

Record who performed this review, concrete findings and fixes. For a separate user trial, record an actual newcomer completing install/demo/mapping without coaching. Agent-only review must remain labeled agent-only.
