# Release procedure and pending ownership

This is guidance, not publication authorization. S16 assembles local distributions
and a release dossier; S17 requires explicit owner authorization for each external
action. No public URL, package reservation, DOI or release badge is claimed.

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
6. Complete the independent-user exercise and maintainer walkthrough below.
7. Obtain explicit approval before pushes, visibility changes, uploads, tags,
   releases or DOI registration. Verify the published bytes and a fresh install
   afterward. Never add citation metadata until actual author/version/date are known.

Publication workflows must use least privilege, audited full action SHAs and a
manual protected gate; no secrets in PR jobs or untrusted pull_request_target runs.
A manual publication workflow is prepared locally and requires an approved
artifact manifest and protected environment. Runtime has no network dependency.
The owner adopted BSD-3-Clause during S17 and supplied the maintainer and private
security contact. The final publication decision remains separate.

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
NOT RUN. A WSL2 result does not imply every Linux distribution was tested.

The {download}`S16 dossier <../state/release/S16_DOSSIER.md>` and
{download}`release checklist <../state/release/S16_CHECKLIST.md>` record hashes,
test scope, privacy review and historical owner decisions. Human acceptance,
independent-user review and explicit S17
authorization are still required before public release. No public action is
authorized by a passing local build.

## S17 owner checkpoint

S17 preparation has started. Alireza Emad confirmed the author/copyright name,
BSD-3-Clause and the security contact. The scoped PyPI pending publisher and
GitHub environment exist; required reviewer protection and the final
commit/artifact decision remain pending. The {download}`publication plan
<../state/release/S17_PUBLICATION_PLAN.md>`, {download}`draft release notes
<../state/release/S17_RELEASE_NOTES.md>` and {download}`maintenance backlog
<../state/release/MAINTENANCE.md>` contain the concrete remaining work.

The read-only `tools/release_preflight.py` checks local owner gates and drift from
the selected archive manifest (`--manifest`, defaulting to S16). Exit 3 means a gate remains blocked; exit 0
never grants publication permission. Finalizing license/author metadata changes
the package bytes and requires a newly reviewed candidate. No S17 public release,
public fresh-install verification, hosted CI or DOI has been performed.

A manually dispatched candidate-check workflow is prepared in
`.github/workflows/ci.yml`: Linux Python 3.11/3.12/3.13, Windows/macOS Python 3.12
and a Python 3.11 direct-dependency-floor job. Each job runs source tests and a
fresh external wheel check; one Linux job also runs lint, format, types and strict
docs. Permissions are read-only and there is no publishing job. The workflow is
prepared locally; its presence does not mean hosted CI or macOS checks passed.
