# 15 — Synthetic fixtures, examples and reproducibility

## 15.1 Data separation

Everything distributed in the foundation, package, tests and documentation must be synthetic or explicitly licensed for redistribution. Do not package ADNI/AIBL participant rows, private paths, clinical labels tied to real identities, downloaded restricted files or screenshots containing them. A public URL alone is not a redistribution license.

Foundation fixtures are hand-checkable contracts, not measured NeuroCVguard results. They are labeled as expected cases. Product demos are generated and executed by the implementation, and their actual outputs are captured separately after code exists.

## 15.2 Required fixture families

Use tiny known-answer fixtures for structural invariants: six or more participants with two visits, disjoint and leaky splits, unknown IDs, target changes, repeated session names, cross-site participants, cross-field transitive families, missing protected labels, single-class folds, shuffled feature rows and exact feature collisions. Add independent 2×2 contingency examples with V=0 and V=1. The accompanying fixtures directory supplies starting tables and plans; Codex must add the remaining adversarial cases in tests.

Known answers must be calculated independently, by explicit set arithmetic or a trusted reference routine. Do not generate expected JSON by calling the function under test and commit it as an oracle.

## 15.3 Reproducible generators

Implement local NumPy Generator-based synthetic cohort creation with explicit seed, participant count, observations per participant, class count, site count, signal strength, participant random-effect strength and site effect. Use documented defaults and validate inputs. Avoid heavy neuroimaging simulation claims: these are tabular mechanisms inspired by neuroimaging workflow structure, not biologically realistic brain models.

A clean scenario has one or repeated observations with correct participant grouping. A repeated scenario creates within-person feature similarity for educational split comparison. A site_shift scenario introduces a controlled site/target distribution difference and site-associated features; the generator records exactly what it changed. All labels/IDs are fictitious. Changing one parameter should not secretly change another mechanism.

## 15.4 Examples to ship

Example 01: map a generic cohort TSV, audit, generate subject-disjoint folds, open an HTML report.
Example 02: compare observation-random diagnostic evaluation with participant-disjoint evaluation on synthetic repeated observations; show the invalid-design banner.
Example 03: leave one site out, demonstrate domain constraints and missing-class metric handling.
Example 04: show a declared globally fitted transformation versus unknown upstream provenance; explain why neither can be certified from feature values.
Example 05: Python integration with a local extracted-feature table using explicit joins and named feature columns.

Provide runnable Python scripts as the primary reproducible form. One optional tutorial notebook can improve accessibility, but it must be generated from or tested against the same script behavior, have no real data, and run top to bottom in a clean kernel. Do not make notebooks the implementation core.

## 15.5 Evidence capture

Record generator parameters, input digests in private manifests, package/dependency versions, actual command lines, seeds and output checksums. Public demo records may include full synthetic identifiers because they are visibly synthetic. A screenshot is evidence of presentation only, not computational correctness.

Do not copy example performance numbers from the prior conversation. They were illustrations, not experimental results. Generate actual demo results after the code passes the invariant and reference tests; retain negative or unimpressive results rather than tuning the demo seed to promise an effect.
