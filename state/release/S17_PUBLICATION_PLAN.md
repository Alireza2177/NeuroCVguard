# S17 publication plan — reviewed local candidate

Prepared 2026-09-27. S17 is IN_PROGRESS. Nothing has been pushed or published by
S17. Owner identity, BSD-3-Clause adoption, security contact and intended public
repository are confirmed in S17_OWNER_DECISIONS.md. Signed-in browser checks
verified ownership of the currently private GitHub repository and PyPI account.
No human scientific walkthrough or independent-user exercise is claimed.

## Candidate and destinations

Repository: https://github.com/Alireza2177/NeuroCVguard.
Distribution/import/CLI: neurocvguard; version 0.1.0; proposed tag v0.1.0.
Source base: eb0559d90b94ef2dda2f847bb0fe72c69112e173.
Local candidate directory: dist/s17-candidate; exact metadata and content manifest:
0.1.0-artifacts.json. Earlier builds remain historical checks, not publication files.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| neurocvguard-0.1.0-py3-none-any.whl | 132475 | a40936fb615b86fcb31a0e212bae8075318f1b43bd8950cecebf3a549d5b74b9 |
| neurocvguard-0.1.0.tar.gz | 103407 | d12b8ba53bed76293e54bdccb43fb849873a5f6cd89adc3341f6966b0a33020b |

Both pass strict metadata and exact archive-content checks. A fresh external
Windows Python 3.11.7 installation matches all 53 runtime payloads and completes
the synthetic demo with networking and source-tree reads blocked. Evidence:
qa/evidence/S17/candidate-wheel.json. Scientific runtime and schemas are unchanged.

## Remaining release sequence

1. Present the local candidate commit and these hashes for the owner's decision,
   including publication of existing development history. A bounded scan of 1,272
   reachable Git blobs found zero credential-shaped hits and 20 path-pattern hits
   in qa/tests. This scan is not an exhaustive privacy guarantee. History includes
   internal stage documentation and machine paths.
2. Record explicit core-stage acceptance or a release-entry waiver. All existing
   human acceptance flags remain false. Maintainer and independent-user exercises
   stay unperformed unless actually completed; any allowed deferral must be
   described as a limitation, not a completed exercise.
3. Push the approved candidate and run the manual read-only six-job CI matrix:
   Linux Python 3.11/3.12/3.13, Windows/macOS Python 3.12 and the Python 3.11 direct
   dependency floor. Hosted results are currently NOT RUN. A failed required job
   blocks publication until fixed and rechecked.
4. Make the repository public as requested and configure the already-approved
   pypi environment with Alireza2177 as required reviewer. Reviewer controls are
   currently unavailable on the private repository. Verify protection before
   dispatching publication. PyPI already lists the approved pending publisher for
   Alireza2177/NeuroCVguard, publish.yml, environment pypi; this does not reserve
   the package name or upload anything.
5. Publish the approved v0.1.0 tag/release and the exact two files above. The manual
   publish workflow downloads them, checks hashes and separately recorded owner
   authorization, then uses scoped OIDC. It does not rebuild. Its protected job
   requires the owner's review.
6. Download actual public files, verify hashes and perform a fresh public install,
   import, console and offline demo. Record real URLs and release timestamp. Add
   citation metadata with actual author/version/date and verified repository URL.
7. Update acceptance evidence and handoff with actual outcomes. Keep maintenance
   tasks in MAINTENANCE.md; no public issues, hosted documentation deployment or
   DOI registration are requested or authorized by this plan.

## External action ledger

| Action | Consent recorded | Performed |
|---|---|---|
| Scoped PyPI pending publisher | Explicit user approval | Yes |
| GitHub pypi environment with required reviewer | Explicit user approval | Environment created; reviewer protection pending |
| Public repository visibility | User explicitly requested public repository | No |
| Push candidate / run CI | Final candidate decision pending | No |
| Public version tag / GitHub release | Final candidate decision pending | No |
| PyPI upload of exact candidate bytes | Final candidate decision pending | No |
| Hosted docs / DOI / public issues | Not requested | No |

The read-only preflight accepts --manifest state/release/0.1.0-artifacts.json
and --dist dist/s17-candidate. Exit 0 only reports local checks; it never grants
permission. No build, local Boolean or agent review constitutes human approval.
