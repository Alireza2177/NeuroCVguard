# Maintenance and optional research backlog

Prepared during S17 on 2026-09-27. Local backlog only; no public issues opened,
owners assigned, deadlines promised or support commitments invented.

| ID | Actual finding / basis | Next action and completion evidence |
|---|---|---|
| M01 | Owner/license/security metadata supplied in S17 | Resolved: owner-approved metadata applied; final candidate rebuilt and clean-install verified |
| M02 | Initial unauthenticated namespace checks returned 404 | Resolved: authenticated ownership and successful public GitHub/PyPI release verified |
| M03 | S00–S16 technical outputs accepted by owner; two human exercises deferred | Record actual human scientific review, maintainer walkthrough and independent tester's synthetic mapping/demo exercise; do not relabel AI checks |
| M04 | macOS and hosted CI were unexecuted at S16 | Resolved: all six S17 hosted jobs passed; initial typing-environment failure retained |
| M05 | Retained history contains local paths/internal evidence | Resolved: owner explicitly approved existing history, internal evidence and machine paths; history preserved |
| M06 | README platform paragraph predated S16 matrix | Resolved: updated with measured S16 scope and rebuilt final candidate; historical S16 archive preserved |
| M07 | ADR-S15-001 first dependency import consumes Python global RNG | Recheck on dependency upgrades; keep seeded behavior regressions; remove exception only with a demonstrated fix |
| M08 | Backward-compatible private plan/context additions still reject on old closed-schema readers | Keep migration notes and legacy-reader tests; do not silently redefine schemas/metric units in patch releases |
| M09 | Public release verification | Resolved: GitHub/PyPI bytes match approved hashes; fresh public-wheel installation and citation validation passed |

For an incoming scientific defect, request a minimal synthetic reproduction and
the affected version/configuration. Do not request patient files in public issues.
Reproduce the defect, add a regression that catches it, fix the smallest affected
boundary and record compatibility/limitations in the next semantic release notes.
Handle security reports through the owner's approved private contact in SECURITY.md.
Response-time and long-term maintenance commitments require a real maintainer.

Optional research work is separate and not started: assess actual demand for
regression/temporal objectives or stronger confound diagnostics before extending
contracts. A performance study needs a predeclared estimand, mechanisms, controls,
seeds, aggregation and uncertainty respecting participants/components, plus an
independent data-license/access review. Compare prior work before novelty claims.
Do not use naive row-wise uncertainty or treat raw design score differences as
causal leakage effects. Recheck journal policies only when a real submission is
being considered; this backlog promises neither eligibility nor publication.
