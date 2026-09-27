# AI assistance record

| Date | Tool/model | Assistance | Human review actually performed | Revision |
|---|---|---|---|---|
| 2026-09-13 | Codex, GPT-6 (system-reported model family; exact build unavailable) | Read the S00 foundation sources; drafted the minimal package, tests, configuration, README, and proposed license record; executed local installation/checks; recorded evidence and performed an AI scope/privacy review. | None recorded. The user authorized S00 implementation; acceptance remains pending. | Local S00 working files; no Git repository or commit. |
| 2026-09-13 | Codex, GPT-6 (system-reported model family; exact build unavailable) | Read S01 sources and S00 evidence; implemented typed records, configuration, offline schemas and serialization; drafted contract/privacy tests and documentation; ran local verification and performed an implementing-agent review. | None recorded. The user explicitly instructed proceeding to S01 and stopping afterward; no human acceptance is inferred for either stage. | Local S01 working files; no Git repository or commit. |
| 2026-09-13 | Codex, GPT-6 (system-reported model family; exact build unavailable) | Read S03 sources and existing S01 records; implemented in-memory inventory, protected components, exact-feature equality, fixed rule wording, tests and docs; ran local checks and implementation-AI review. | None recorded. The user explicitly selected S03 only; S02 remains unimplemented and prior acceptance is not inferred. | Local S03 working files; no Git repository or commit. |
| 2026-09-13 | Codex, GPT-6 (system-reported model family; exact build unavailable) | Read S04 sources; implemented strict plan import/binding, outer/inner invariant audits and scoped public flags; drafted tests/docs; executed local QA and implementation-AI review. | None recorded. The user selected S04 only; previous acceptance remains pending and S02 remains unimplemented. | Local S04 files; no Git repository or commit. |
| 2026-09-13 | Codex, GPT-6 (system-reported model family; exact build unavailable) | Read S05 sources; implemented standard participant/domain split generation, independent post-audit, sensitive exports and separate diagnostics; drafted tests/docs and performed implementation-AI review. | None recorded. The user selected S05 only; prior acceptance remains pending and S02 ingestion is unimplemented. | Local S05 files; no Git repository or commit. |

| 2026-09-13 | Codex, GPT-6 (system-reported model family; exact build unavailable) | Read S06 sources; implemented participant-level association views, SciPy statistics, warnings and conservative privacy projection; drafted tests/docs and performed implementation-AI review. | None recorded. The user selected S06 only; prior acceptance remains pending and S02 ingestion is unimplemented. | Local S06 files; no Git repository or commit. |

| 2026-09-25 | Codex, GPT-6 (system-reported family; exact build unavailable) | Read S07 sources; implemented strict declaration loading, scoped checks, cohort audit integration and planned fit validation; drafted tests/docs, ran local checks and performed implementation-agent review. | None recorded. The user authorized S07; no predecessor acceptance or human review is inferred. | Local S07 working changes from Git HEAD 2224dfd. |

| 2026-09-26 | Codex, GPT-6 (system-reported family; exact build unavailable) | Implemented S08 shared privacy projection, offline reports, safe writes and optional findings CSV; drafted tests/docs, executed checks, inspected actual rendered synthetic reports and reviewed the diff. | None recorded. The user authorized S08 only; predecessor acceptance and human review are not inferred. | Local S08 working changes from Git HEAD 3769299. |

| 2026-09-26 | Codex, GPT-6 (system-reported family; exact build unavailable) | Implemented the explicitly authorized S02 prerequisite: strict table input, keyed feature alignment, limits and digests; added tests/docs and ran local regression checks. | None recorded; the user authorized S02 followed by S09, without granting human acceptance. | Local S02 changes from f4adbe1. |

| 2026-09-26 | Codex, GPT-6 (system-reported family; exact build unavailable) | Implemented S09 command handlers, shared orchestration, exit/output policy and configured report projection; drafted tests and docs, ran local command journeys and regression checks, and reviewed the implementation diff. | None recorded. The user authorized S02 then S09; acceptance remains pending and S10 is not authorized. | Local S09 changes from f4adbe1, following the local S02 prerequisite. |

| 2026-09-26 | Codex, GPT-6 (system-reported family; exact build unavailable) | Implemented S10 fixed-C evaluation, observed fit boundaries, participant metrics, private/public exports and evaluate CLI; added independent fit/metric tests, docs and actual local verification. Identified a schema conflict and implemented only the extension explicitly approved in ADR-S10-001. | The user approved the optional private plan-provenance schema extension. No scientific code review or stage acceptance is recorded; S11 remains unstarted. | Local S10 changes from f2d995d. |

| 2026-09-26 | Codex, GPT-6 (system-reported family; exact build unavailable) | Implemented S11 inner-plan derivation, explicit nested C selection and fresh outer refitting; added adversarial isolation and scoring tests, documentation and recorded local verification. | User requested S11. No human scientific review or stage acceptance is recorded. S12 remains unstarted. | Local S11 changes on top of uncommitted S10 work from f2d995d. |

| 2026-09-26 | Codex, GPT-6 (system-reported family; exact build unavailable) | Implemented S12 private-record comparisons, narrow diagnostic eligibility and raw observation pooling, CLI/report context and privacy handling; added adversarial tests, docs and recorded local checks. Performed implementing-agent scientific/privacy review. | User requested S12 and explicitly approved the optional comparison context extension in ADR-S12-001. No human code/scientific review or stage acceptance is recorded. | Local S12 changes from 6acfed4. |

| 2026-09-26 | Codex, GPT-6 (system-reported family; exact build unavailable) | Implemented S13 local RNG generators, offline demo, five packaged tutorials, fixed synthetic labeling, tests and documentation; executed real synthetic workflows and recorded their outputs. Browser screenshot capture was rejected by the browser security policy; no screenshot or visual review is claimed. | User requested S13 and explicitly approved the screenshot-only exception in ADR-S13-001. No human scientific review or stage acceptance is recorded. | Local S13 changes from e8eef64. |

Through S13, no independent reviewer, human authorship approval, public release
approval, or comprehensive scientific validation was claimed. Later changes to review
status must reflect actual review of the specified files.
# S14–S15 assistance record — 2026-09-26 UTC / 2026-09-27 local

The user requested both stages sequentially. Codex drafted/updated documentation,
contributor materials, executable documentation checks, hardening properties,
mutation/resource/security evidence and the fixes described in the S15 review.
Tools used included local Python/PowerShell, pytest/Hypothesis/Coverage.py,
Ruff/mypy, Sphinx/MyST and the web tool for four external documentation links
after shell linkcheck was blocked by the sandbox proxy. No public push/upload,
release, real participant data or telemetry was involved.

The user explicitly authorized a separate AI reviewer. That fresh-context agent
read source/contracts, reproduced UNC-path and privacy-alias defects, reviewed
their fixes and reproduced the dependency first-import RNG limitation. It was
AI review, not human scientific review. Exact findings and boundaries are in
qa/evidence/S15/review.md. Tests/measurements are reported from actual command
records, including failures; no exhaustive correctness claim is made.

The maintainer walkthrough was asked; the user queried its purpose. Explanations
were provided and the human walkthrough/external-user trial remain pending.
The user approved the narrow first-import exception in ADR-S15-001. This is not
stage acceptance or approval of a later phase. Copyright/license/contact and
release metadata remain unconfirmed; no author, tester or review is fabricated.

S15 follow-up (2026-09-26 UTC): on the user's request for the most defensible
approach, Codex repaired the standalone foundation validator's Windows keys,
added explicit artifact-only scope while retaining default snapshot assertions,
protected historical outputs and added focused regression tests. An unknown-ID
fixture crash found by those tests was corrected. Contributor guidance, strict
docs and lint/format checks were updated. No new independent or human review is
claimed; the prior scientific package, RNG exception and stage boundary remain.
