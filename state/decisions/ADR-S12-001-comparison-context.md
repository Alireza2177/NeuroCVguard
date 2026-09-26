# ADR-S12-001 — Optional structured comparison context

Status: accepted
Date: 2026-09-26  
Human decision owner: user in this task
Affected: REQ-S12, comparison-summary and its embedded audit-report schema

## Problem and counterexample

Specification 12.1 requires display of cohort/feature identity, fold counts,
participant/observation counts, training-size ranges, model specification and
metric units beside differences. ComparisonDesign currently permits only name,
objective, diagnostic_only and metrics, with additionalProperties=false.
Adding n_folds=3 to a design is rejected. Existing interpretation is free text
and the public projection deliberately replaces it to avoid leaking identifiers.
It cannot safely carry structured per-design context through public rerendering.

## Proposed decision

Add one optional closed `context` object to each comparison design. Fields:

- execution_status: completed/incomplete/blocked; metric_unit: participant.
- cohort_reference and feature_reference: local equivalence aliases matching
  `cohort-[0-9]+` and `features-[0-9]+`; never raw digests or observation keys.
- n_folds, n_completed_folds, n_participants, n_observations, n_features:
  nonnegative integer counts.
- training_participants_min and training_participants_max: nonnegative integers.
- class_order: unique nonempty class labels; positive_class: a label or null.
- model: fixed text `prescribed_logistic_baseline`; recorded_C_values: unique
  positive numbers from recorded fits/selections; tuning_recorded: boolean.

No max_iter, seed or unrecorded configuration is inferred from a digest. State
that complete model settings require the original configuration. Class support
remains in existing MetricSet and follows whole-metric privacy suppression.
Public context aliases class labels using the existing class-label projection;
it contains no raw cohort/feature digests, feature names or input free text.
Upstream and causal limitations remain fixed interpretation/report text.

Update normative and packaged standalone/embedded schemas together. Old records
without context remain readable and must not gain fabricated context. Older
closed-schema readers require an update before reading extended records. No
scientific separation rule, metric definition, diagnostic waiver or threshold
changes. Regenerate reading editions after the approved clarification.

## Alternatives

Leaving the schema unchanged loses required design context in default reports.
Encoding it in free text would obstruct validation and privacy projection. A new
general private comparison format would exceed this stage's need.

## Validation

Schema migration/parity tests, old-record round trips, typed context consistency,
public omission of private digests/identifiers, escaped rendering, suppression and
stable rerendering, alongside the nine existing S12 acceptance cases.

## Approval and consequences

The user explicitly answered “Approve compatible context extension (Recommended)”
in this task on 2026-09-26. This approves this compatible extension, not scientific
review, stage acceptance or publication.
