# Release procedure and verification

S16 assembled local distributions and a release dossier. During S17 the owner
approved the exact release files, accepted the S00–S16 technical outputs and
authorized public repository/history publication. The
[repository](https://github.com/Alireza2177/NeuroCVguard) is public. Package
upload and fresh public-wheel verification succeeded; no DOI exists.

## Public GitHub release

[Version 0.1.0](https://github.com/Alireza2177/NeuroCVguard/releases/tag/v0.1.0)
was published on 2026-09-27 at 06:27:02 UTC from commit
deac163cdc05412c3ab05beebbb91e2e0b928d7c. Both downloaded GitHub assets match
the exact approved SHA256 values. All six jobs in the
[corrected CI run](https://github.com/Alireza2177/NeuroCVguard/actions/runs/36299543058)
passed, including source tests and clean-wheel checks on Linux, Windows and macOS.
[PyPI 0.1.0](https://pypi.org/project/neurocvguard/0.1.0/) was published at
06:36:55–57 UTC. Both public files match the approved hashes. A fresh external
Windows Python 3.11.7 environment passed import/version/console/assets and the
offline synthetic demo; all 53 installed runtime payloads match the published wheel. The {download}`citation metadata <../CITATION.cff>` uses
the actual author, version, release date and working GitHub release URL, with no DOI.

1. Obtain actual human acceptance of stages and resolve every result-changing bug.
2. Confirm author/maintainer identity, copyright, adoption of proposed BSD-3-Clause,
   private security contact, repository ownership and package namespace.
3. Run the quality suite, strict docs build, coverage/mutations, offline demos and
   privacy/security review. Record exact commands, versions and limitations.
4. In S16, build wheel/sdist with `python -m build`, check metadata with twine,
   inspect archive contents and hashes, and install the wheel outside the source
   tree. Verify imports, templates, schemas, console and demo without editable paths.
5. Execute the intended Python/OS and lowest-dependency matrix. Unavailable runs
   remain NOT RUN; do not advertise unverified lower bounds or support.
6. Record the independent-user exercise and maintainer walkthrough. The owner
   explicitly deferred both for the first release; they remain unfinished
   release-readiness limitations, not independent human validation.
7. Obtain explicit approval before pushes, visibility changes, uploads, tags,
   releases or DOI registration. Verify the published bytes and a fresh install
   afterward. Never add citation metadata until actual author/version/date are known.

Publication workflows must use least privilege, audited full action SHAs and a
manual protected gate; no secrets in PR jobs or untrusted pull_request_target runs.
The manual publication workflow requires an approved
artifact manifest and protected environment. Runtime has no network dependency.
The owner adopted BSD-3-Clause during S17 and supplied the maintainer and private
security contact. The exact publication decision is recorded in the owner ledger.

## Local S16 candidate

S16 built version 0.1.0 as a wheel and source archive under `dist/s16/`. The wheel
is built from the sdist and all 53 runtime payloads match the selected source.
Both pass strict Twine metadata validation. Fresh Windows/Linux wheel environments
exercise the actual console entry point, all schemas/assets and default demo;
an audit hook blocks source-tree reads and networking during the demo.

The Linux WSL2 matrix passed 712 existing tests per interpreter (3.11.16,
3.12.14, 3.13.15), followed by 9 new archive regression tests on each. Windows
3.12.3 and the Windows 3.11.7 dependency-floor environment exercise the installed
wheel's runtime tests. The S16 dossier records setup failures and corrective runs
instead of relabeling the first attempts successful. macOS and hosted CI are
NOT RUN in S16; the S17 hosted matrix subsequently passed. A WSL2 result does not imply every Linux distribution was tested.

The {download}`S16 dossier <../state/release/S16_DOSSIER.md>` and
{download}`release checklist <../state/release/S16_CHECKLIST.md>` record hashes,
test scope, privacy review and historical owner decisions. Later owner acceptance
and exact S17 publication authorization are recorded in the S17 plan. A passing
local build alone never authorizes public actions.

## S17 owner checkpoint

S17 publication and public-install verification are complete. Alireza Emad confirmed the author/copyright name,
BSD-3-Clause and the security contact. The scoped PyPI pending publisher and
GitHub environment exist. Publication requires Alireza2177 review, allows only
main and disallows administrator bypass. The final commit/artifact decision is
recorded. The {download}`publication plan
<../state/release/S17_PUBLICATION_PLAN.md>`, {download}`release notes
<../state/release/S17_RELEASE_NOTES.md>` and {download}`maintenance backlog
<../state/release/MAINTENANCE.md>` record the release and remaining maintenance work.

The read-only `tools/release_preflight.py` checks local owner gates and drift from
the selected archive manifest (`--manifest`, defaulting to S16). Exit 3 means a gate remains blocked; exit 0
never grants publication permission. Finalizing license/author metadata changes
the package bytes and requires a newly reviewed candidate. The final candidate
passed 733 local tests and a fresh external wheel check. Hosted CI passed and the
GitHub and PyPI releases exist; fresh installation of the public wheel passed.

The manually dispatched candidate-check workflow is in
`.github/workflows/ci.yml`: Linux Python 3.11/3.12/3.13, Windows/macOS Python 3.12
and a Python 3.11 direct-dependency-floor job. Each job runs source tests and a
fresh external wheel check. Linux 3.12 runs lint, format and strict docs; Linux
3.11 runs mypy with the configured 3.11 target. The first hosted run exposed
3.12-only syntax in NumPy stubs when mypy ran on 3.12; the corrected run retains
the target and all assertions. CI permissions are read-only. Publication uses a
separate manual protected workflow and uploads verified existing files without
rebuilding them. See the S17 handoff for actual hosted outcomes.

Post-release README, citation and evidence updates do not rebuild the approved
archives or move tag v0.1.0. That tag remains at deac163; the publishing-tool-only
fix is 098c4f6. The first publishing attempt rejected metadata 2.5 before upload.
The corrected, SHA-pinned v1.14.2 action succeeded with the identical package bytes.
