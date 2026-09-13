# Stage map and acceptance boundaries

The plan has 18 stages and 54 bounded work packages. Work sequentially by default. S09 is a useful audit milestone; S16 is the complete local release candidate; S17 requires explicit public-release authorization. These are deliverables, not calendar-time estimates.

| Stage | Goal | Entry | Prompt |
|---|---|---|---|
| S00 | Repository bootstrap and environment evidence | Start | `prompts/S00_bootstrap.md` |
| S01 | Typed models, configuration and serialization contracts | S00 | `prompts/S01_models_contracts.md` |
| S02 | Strict tables, identities and keyed feature joins | S01 | `prompts/S02_table_io.md` |
| S03 | Participant, dependency and cohort checks | S02 | `prompts/S03_identity_cohort.md` |
| S04 | Split import and independent invariant auditing | S03 | `prompts/S04_split_audits.md` |
| S05 | Group-aware and held-out-domain plan generation | S04 | `prompts/S05_split_generation.md` |
| S06 | Descriptive acquisition–target association checks | S05 | `prompts/S06_associations.md` |
| S07 | Declared preprocessing and runtime evidence model | S06 | `prompts/S07_provenance.md` |
| S08 | Shared JSON/HTML reporting and privacy boundaries | S07 | `prompts/S08_reports.md` |
| S09 | CLI and usable audit milestone | S08 | `prompts/S09_audit_cli.md` |
| S10 | Fixed-parameter controlled evaluator | S09 | `prompts/S10_baseline.md` |
| S11 | Nested participant-aware regularization selection | S10 | `prompts/S11_nested_tuning.md` |
| S12 | Design comparison and gated diagnostic examples | S11 | `prompts/S12_comparison.md` |
| S13 | Synthetic generators and reproducible end-to-end demos | S12 | `prompts/S13_synthetic_demo.md` |
| S14 | Complete documentation and contributor materials | S13 | `prompts/S14_documentation.md` |
| S15 | Adversarial, property, security and scientific review | S14 | `prompts/S15_hardening.md` |
| S16 | Build, clean installation and release-readiness dossier | S15 | `prompts/S16_release_candidate.md` |
| S17 | Human-approved public release and maintenance handoff | S16 | `prompts/S17_public_release.md` |

## Final definition of done

A researcher can install the reviewed wheel, run an offline synthetic example, map their own authorized table, see supported and unassessable checks, create independently checked splits, optionally evaluate a controlled baseline, and understand the report without hidden data or undocumented setup. Tests, docs and installation evidence must support those claims. Public release still needs owner approval.
