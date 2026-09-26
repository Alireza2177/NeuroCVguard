# ADR-S13-001 — Required screenshot blocked by browser security

Status: accepted by explicit user decision  
Date: 2026-09-26  
Affected: S13.C screenshot deliverable and presentation portion of AT-S13-07

## Constraint and concrete evidence

S13.C requires a genuine report screenshot. The implemented demo has actual HTML
reports, JSON, configurations, private results and checked output digests. Opening
the local smoke report with the browser tool was rejected by its URL security
policy. The rejection explicitly prohibits alternate-surface, indirect or raw
browser-command workarounds. No such workaround was attempted and no screenshot
was fabricated. The exact observed blocker is recorded under
`qa/evidence/S13/screenshot-blocked.md`.

## Proposed bounded exception

If explicitly approved by the user, close S13 with the screenshot artifact waived
for this stage. Keep its attempted capture marked BLOCKED/NOT CAPTURED, retain
actual executable reports and automated value/checksum verification, and do not
claim any successful visual browser review. Human scientific review and stage
acceptance remain pending. S14 is not authorized by this exception.

The alternative is to retain S13 as BLOCKED until a human supplies a genuine
capture of the recorded report for comparison with its actual contents. This does
not authorize bypassing the browser policy, uploading local reports or changing
any scientific or privacy requirement.

## Decision

The user explicitly answered **“Approve screenshot-only exception”** in this task
on 2026-09-26. The screenshot artifact is waived for S13 only. Its attempted
capture remains BLOCKED/NOT CAPTURED; no image or visual review is claimed.
The passing automated report-value checks and actual executed reports remain the
evidence for displayed numerical values. S13 may be READY_FOR_REVIEW under this
exception. Human scientific review, stage acceptance and S14 authorization are
not granted by this decision.
