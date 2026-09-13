# 19 — Paper-readiness and post-v0.1 research boundaries

## 19.1 Separate product correctness from publication merit

The first deliverable is useful, correct software with documented limitations. A publication is a later research outcome, not an acceptance criterion that can be manufactured by generating a manuscript. Neither package size nor test count proves novelty. Compare relevant existing software and studies honestly before making a contribution claim.

The literature already includes direct investigations of leakage in connectome-based machine learning and specialized confound-testing software [R17, R09]. Do not rediscover these results and describe them as wholly new. A defensible contribution could be the explicit audit contracts, evidence classifications, interoperability and validated workflow, but its value needs demonstration.

## 19.2 Research plan to consider after release

Predeclare the mechanism being manipulated, intended generalization population, model families, metrics, data-generating processes, seeds, parameter grid and aggregation before executing a performance study. Separate repeated-subject contamination from genuine domain shift and declared preprocessing leakage. Use clean matched negative controls and real licensed datasets only after independent access/permission review.

Measure diagnostic behavior with known injected violations: sensitivity to supported overlap errors, false-positive rate on valid designs, coverage/unassessable behavior, computational cost and agreement with manually verified audit cases. For model performance experiments, distinguish different estimands and do not present a raw score difference as a universal causal leakage estimate.

Uncertainty must respect participants/components and the sampling design. Do not perform naive row-wise permutations or t-tests on overlapping CV folds. Research-level bootstrap/permutation methods require a separate approved statistical specification, not an improvised v0.1 helper.

## 19.3 Candidate later features

Consider regression, additional declared dependency types, baseline-visit selection as an explicit curation utility, temporal objectives, calibrated predictions, user-supplied estimator protocols, extended BIDS adapters, exact input-file hashing, provenance-ledger interoperability and stronger confound diagnostics only in response to evidence and use cases. Add one feature family at a time with a versioned contract and tests.

A graphical interface is optional. No raw image processing, federated learning platform or disease-specific architecture should be added merely to enlarge the project. The user's existing publication and PhD priorities remain separate from this tool's technical requirements.

## 19.4 Software-paper route

As checked on 12 September 2026, JOSS describes public development-history and demonstrated-research-impact requirements, including more than six months of public development for eligibility [R19]. A rapid repository dump is therefore not a guaranteed submission route. Re-check the rules when considering submission; eligibility and acceptance are never promised.

Record genuine releases, issues, reproducible uses and external engagement as they happen. Do not manufacture public history, user testimonials or a fictional contributor community. A methods article must likewise provide a real scientific result beyond announcing an implementation.

## 19.5 Research artifacts to preserve

Preserve experiment plans, immutable release tags, exact input licenses, data extraction instructions, dataset access restrictions, synthetic generators, test/benchmark scripts, full parameter configurations, negative results and known failure cases. Share only authorized data. Keep manuscript claims traceable to a specific software version and actual output file.

This foundation authorizes preparation for reproducible research, not claims of publication, clinical readiness, or novelty that have not been established.
