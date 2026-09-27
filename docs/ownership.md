# Maintainer walkthrough and external-user exercise

**Human walkthrough: pending. External-user trial: not performed.**
Both exercises were deferred for version 0.1.0. This page outlines the remaining
review work; the release tests are documented separately in [release verification](release.md).

| Question | Explanation to discuss |
|---|---|
| Why are repeated visits alone not leakage? | Check actual train/test membership and objective. All visits of a person can remain in training; crossing into test violates unseen-person evaluation. |
| Why can a traveling participant make site holdout impossible? | Holding out a site puts that person's rows on both sides. Protecting both the complete cohort and person/component disjointness can be incompatible. Refuse rather than silently curate. |
| Which rows may inner tuning fit on? | Each inner training subset inside its current outer training set; inner validation and all outer-test rows remain excluded. Final outer refit uses outer training only. |
| When must AUC be null? | Binary positive class unspecified, missing required true classes or other explicit undefined conditions. A failed run has no complete pooled metrics. Privacy suppression is a separate reason. |
| Why is a projected report not guaranteed anonymous? | Summary counts and combinations can disclose information even when IDs and small cells are removed; operational files retain identities. |

For the independent-user trial, a technically competent tester should install a
reviewed clean wheel outside the source tree, run the default synthetic demo,
locate its limitations/private artifacts, remap a fictitious observation/participant
column pair, and complete validate/audit/split without verbal coaching. Record the
actual tester, environment, commands, time/friction and findings with their consent.
Keep the results alongside the release records so later changes can address the findings.

The maintainer accepted the technical release outputs on 2026-09-27. Independent
scientific review and the exercises above remain separate from that release decision.
