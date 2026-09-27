# Maintenance and optional research backlog

Prepared during S17 on 2026-09-27. Local backlog only; no public issues opened,
owners assigned, deadlines promised or support commitments invented.

| ID | Actual finding / basis | Next action and completion evidence |
|---|---|---|
| M01 | Owner/license/security metadata supplied in S17 | Resolved: owner-approved metadata applied; final candidate rebuilt and clean-install verified |
| M02 | Initial unauthenticated namespace checks returned 404 | Authenticated GitHub ownership and PyPI account/pending publisher verified; final project registration still pending |
| M03 | All human acceptance flags false; exercises pending | Record actual human scientific review, maintainer walkthrough and independent tester's synthetic mapping/demo exercise; do not relabel AI checks |
| M04 | macOS and hosted CI unexecuted | Configure reviewed CI and run the documented matrix when authorized; record real logs and failures |
| M05 | Retained history contains local paths/internal evidence | Review intended public history/surface; obtain explicit scope decision without automatic history rewriting |
| M06 | README platform paragraph predated S16 matrix | Resolved: updated with measured S16 scope and rebuilt final candidate; historical S16 archive preserved |
| M07 | ADR-S15-001 first dependency import consumes Python global RNG | Recheck on dependency upgrades; keep seeded behavior regressions; remove exception only with a demonstrated fix |
| M08 | Backward-compatible private plan/context additions still reject on old closed-schema readers | Keep migration notes and legacy-reader tests; do not silently redefine schemas/metric units in patch releases |
| M09 | Public release not yet performed | Verify final artifact digests and fresh public installation, docs/citation links and actual timestamps after approved publishing |

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
