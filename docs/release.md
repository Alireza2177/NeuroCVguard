# Releases and verification

Version 0.1.0 was published on 2026-09-27:

- [GitHub release](https://github.com/Alireza2177/NeuroCVguard/releases/tag/v0.1.0)
- [PyPI package](https://pypi.org/project/neurocvguard/0.1.0/)
- {download}`Citation metadata <../CITATION.cff>`

## Verification for 0.1.0

The release passed 733 local tests and all six jobs in the
[CI run](https://github.com/Alireza2177/NeuroCVguard/actions/runs/36299543058):
Linux with Python 3.11, 3.12 and 3.13; Windows and macOS with Python 3.12; and
Python 3.11 with the direct dependency floor. Each job included source tests and
an installation check outside the source tree. Lint, formatting, type checking
and the strict documentation build also passed.

Both GitHub and PyPI downloads match the SHA256 values in
{download}`the artifact manifest <../state/release/0.1.0-artifacts.json>`.
A fresh Windows Python 3.11.7 environment installed the downloaded PyPI wheel
and passed version, import, console, schema, asset and synthetic-demo checks.
All 53 installed runtime files matched the wheel. The demo ran with network access
and source-tree reads blocked.

The maintainer walkthrough and independent-user trial were deferred for this
release. They remain open follow-ups; automated tests do not replace that
feedback. See [review status](ownership.md) and [limitations](limitations.md).

Detailed commands, environments, failures and corrections are in
{download}`the release record <../state/handoffs/S17.md>`. The
{download}`maintenance backlog <../state/release/MAINTENANCE.md>` tracks follow-up
work. Development assistance is described in
{download}`AI_ASSISTANCE.md <../AI_ASSISTANCE.md>`.

## Preparing a release

1. Resolve known bugs that change results. Review scientific invariants, privacy
   handling, compatibility changes and release notes.
2. Run tests, lint, formatting, type checks and the strict documentation build.
   Check the supported Python/OS combinations and dependency floor. Record any
   missing checks and unresolved limitations.
3. Build the source archive and wheel with `python -m build`. Validate metadata
   with Twine, inspect archive contents and record their SHA256 values.
4. Install the wheel in a clean environment outside the checkout. Verify imports,
   the console entry point, packaged schemas/templates and the offline demo.
5. Confirm maintainer, license, security-contact and citation metadata. Obtain
   maintainer sign-off on the exact release files and publication destinations.
6. Publish the tag and those files, then download them to verify their hashes and
   test a fresh installation. Update citation metadata with the actual release
   date and working links.

## Publishing workflow

`.github/workflows/ci.yml` runs candidate checks manually. The separate
`.github/workflows/publish.yml` uses PyPI Trusted Publishing through the protected
`pypi` environment. It permits only `main`, requires maintainer review and disables
administrator bypass. Actions are pinned to full commit hashes and permissions
are limited to what each job needs.

The publishing job downloads existing GitHub release assets, verifies their
manifest and publication authorization, then uploads them without rebuilding.
`tools/release_preflight.py` checks local release conditions and source drift;
exit 3 means a condition is unmet. Its result does not replace maintainer sign-off.

The 0.1.0 tag remains at `deac163`. The publishing-tool fix at `098c4f6` added
support for package metadata 2.5; the initial attempt stopped before upload.
Later README, citation and documentation edits do not change the published files
or move the tag. No DOI has been registered.
