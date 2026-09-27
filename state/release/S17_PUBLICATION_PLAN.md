# S17 publication plan — reviewed local candidate

Prepared 2026-09-27. Publication and public-install verification succeeded; final S17 review remains separate. Candidate 06c14b6 and approval records
f694268 have been pushed to main; the repository is now public. Owner identity,
BSD-3-Clause adoption, security contact and exact release scope are confirmed in
S17_OWNER_DECISIONS.md. Signed-in checks verified GitHub and PyPI ownership.
No human scientific walkthrough or independent-user exercise is claimed.

## Candidate and destinations

Repository: https://github.com/Alireza2177/NeuroCVguard.
Distribution/import/CLI: neurocvguard; version 0.1.0; published tag v0.1.0.
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

## Release sequence and current status

1. Owner approved candidate 06c14b6, these hashes and publication of existing
   development history. A bounded scan of 1,272
   reachable Git blobs found zero credential-shaped hits and 20 path-pattern hits
   in qa/tests. This scan is not an exhaustive privacy guarantee. History includes
   internal stage documentation and machine paths.
2. Owner explicitly accepted S00–S16 technical outputs for the initial research
   release and deferred the two human exercises. Those exercises remain unfinished
   and disclosed as a limitation, not completed human scientific validation.
3. Approved candidate pushed. Initial run 36299183458 exposed a typing-environment
   error; the corrected six-job run 36299543058 passed at deac163:
   Linux Python 3.11/3.12/3.13, Windows/macOS Python 3.12 and the Python 3.11 direct
   dependency floor. A failed required job
   blocks publication until fixed and rechecked.
4. Repository is public; pypi environment requires Alireza2177 review, disables
   administrator bypass and permits only main. PyPI lists the approved pending publisher for
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
| GitHub pypi environment with required reviewer | Explicit user approval | Yes; main-only, no admin bypass |
| Public repository visibility | Explicit scoped release approval | Yes |
| Push candidate / run CI | Explicit scoped release approval | Pushed; all six corrected jobs passed |
| Public version tag / GitHub release | Approved after passing required checks | v0.1.0 at deac163, published 2026-09-27T06:27:02Z; public hashes verified |
| PyPI upload of exact candidate bytes | Approved after passing required checks | Corrected run 36300511287 succeeded; public hashes and fresh installation verified |
| Hosted docs / DOI / public issues | Not requested | No |

The read-only preflight accepts --manifest state/release/0.1.0-artifacts.json
and --dist dist/s17-candidate. Exit 0 only reports local checks; it never grants
permission. No build, local Boolean or agent review constitutes human approval.

Post-release README, citation and evidence updates do not rebuild the approved
archives or move tag v0.1.0. That tag remains at deac163; the publishing-tool-only
fix is 098c4f6. The first publishing attempt rejected metadata 2.5 before upload.
The corrected, SHA-pinned v1.14.2 action succeeded with the identical package bytes.
