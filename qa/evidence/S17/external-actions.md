# S17 external-action evidence

Recorded 2026-09-27 from actual command results and signed-in browser observations.

- Local candidate commit: 06c14b64776faf6ccce7c80aa9703db6490f4dd9.
- Approval-record commit: f694268432e9aeacf8c6315b2f806596fa20b906.
- `git push origin HEAD:main` exited 0, advancing eb0559d to f694268.
- After the user's scoped release approval, GitHub's visibility confirmation
  completed and General settings displayed “This repository is currently public.”
  Unauthenticated API verification is saved in public-repository.json.
- The pypi environment saved Alireza2177 as required reviewer, with administrator
  bypass disabled. Prevent self-review remains unchecked so the sole owner can
  review a run they triggered. The actual decision/submission actors are recorded
  per run in S17_OWNER_DECISIONS.md; no independent human review is implied.
- Deployment branch rule main saved successfully; UI showed one allowed branch,
  zero allowed tags. No secrets or environment variables were added.
- Manual Candidate checks dispatch on main created run 36299183458 at f694268.
  https://github.com/Alireza2177/NeuroCVguard/actions/runs/36299183458
  Its result is pending; this record does not claim CI passed.
- No version tag, GitHub release, package upload or DOI operation has occurred yet.

Corrected CI: deac163cdc05412c3ab05beebbb91e2e0b928d7c changes only the workflow's
mypy job selection and its failure evidence. `git push origin HEAD:main` exited 0.
A manual dispatch created run 36299543058 at deac163. Approved package bytes
remain unchanged; no tag or package upload occurred during the failed CI run.

## Completed publication

- Corrected CI run 36299543058 succeeded in all six jobs at deac163.
- Annotated v0.1.0 points to deac163; GitHub release was published at
  2026-09-27T06:27:02Z. Downloaded release assets match the manifest.
- First PyPI run 36300178736 failed before upload on metadata 2.5 support.
  The owner completed its deployment review directly.
- Publishing-tool correction 098c4f6 pins official action v1.14.2 and was pushed
  to main. Corrected run 36300511287 succeeded. The owner explicitly approved
  it in conversation; the agent submitted that decision via GitHub UI, after
  informing the user. Required reviewer/admin-bypass protections remained intact.
- PyPI wheel/sdist uploads completed at 06:36:55.856348Z / 06:36:57.172537Z
  on 2026-09-27. Public JSON, downloaded bytes and index resolution verified.
- Fresh installation of the public downloaded wheel passed in a clean external
  Windows Python 3.11.7 environment. See public-wheel-install.json.
- No DOI, hosted-docs deployment or public issue creation was performed.
