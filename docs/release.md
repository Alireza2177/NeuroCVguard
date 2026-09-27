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
No publication workflow is enabled here. Runtime has no network dependency.
The proposed license notice is not yet a finalized license grant.
