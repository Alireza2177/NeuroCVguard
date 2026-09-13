# Independent technical/scientific review prompt

Review the selected stage as a critical reviewer, not as the implementer defending its decisions. Read AGENTS.md, the stage prompt, relevant specs, acceptance cases, actual changed code/tests and evidence. Do not treat a green test count as proof of the intended scientific behavior.

Look specifically for row-order joins, identity/session confusion, incomplete transitive groups, objective-independent site rules, globally fitted preprocessing, inner/outer contamination, silent exclusions/fallbacks, missing-class score fabrication, incomplete-fold averaging, causal interpretations of score gaps, false provenance verification, and sensitive-data leakage through secondary outputs.

For each finding provide severity, exact file/line or function, violated requirement/case, a minimal reproducible counterexample, scientific/user impact, and a proposed correction. Add a failing regression test when feasible. Distinguish confirmed defects from questions. Do not rewrite unrelated modules or publish anything.

Conclude with blockers, nonblocking issues, checks actually executed and checks not run. Do not mark human acceptance; state whether the implementation is technically ready for human review.
