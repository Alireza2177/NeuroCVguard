# 06 — Cohort and dependency auditing

## 6.1 Inventory before conclusions

After structural validation, compute observation count, participant count, observations per participant, class counts at observation and participant levels, mapped-field availability, missingness, participant-local session counts, site/phase counts and target stability within participants. Store counts separately from display suppression. A cohort inventory must not turn rows into independent people.

Repeated observations trigger an informational notice: “This cohort has repeated participant observations; evaluate separation in the actual splits.” A participant/session pair with multiple rows is not automatically an error because there may be several runs or modalities. `observation_id` is what distinguishes those rows. A global session label such as `ses-01` is not a grouping key across people.

Changing diagnosis within a participant can be scientifically meaningful. Describe it and block the constant-target baseline/split generator; do not call it an incorrect label or select the earliest visit automatically. A researcher may curate a baseline cohort explicitly outside this tool.

## 6.2 Protected independence components

Always protect participant identity. Additional declared independence fields protect relationships such as family identity or externally verified duplicate clusters. Compute connected components using union–find over participants: for each field, union all participants sharing that non-missing value. A participant with multiple values links those groups transitively. Field namespaces are distinct; family `A` must not be equated with duplicate-cluster `A` merely because the text matches.

Do not group by tuples of participant/family/cluster. Tuple grouping can split two siblings who have different participant IDs, and it can miss transitive connections. Do not reset identities by site. Reject missing values in a declared protected field for strict planning/evaluation. An audit can still report observed components but marks incomplete relationship coverage.

Stable component labels are derived from deterministic sorting of participant IDs and component membership. They are internal identifiers, not anonymous patient IDs. Tests must verify transitive links, field namespaces, missing-value handling, row-order invariance and singletons.

## 6.3 Exact numeric feature equality

When features are supplied, optionally group rows that have exactly equal values over the explicitly selected numeric columns, using a deterministic hash followed by exact equality verification to rule out hash collisions. Treat two NaNs at the same positions as equal for this check, and canonicalize signed zero. Skip all-missing feature vectors and report the skip. Do not perform an O(n²) pairwise comparison or rounding-based fuzzy matching.

Identical feature vectors across participants are a warning that requires investigation. They do not prove duplicated images: low-dimensional or discretized features can legitimately be identical. The package must not merge identities, change groups, drop rows or force a particular interpretation on this basis. If the user verifies a duplicate relationship, they can supply an explicit protected duplicate-cluster column in a subsequent documented run.

## 6.4 Acquisition variation

Describe participants who span multiple sites or phases. This is not an error in the cohort, but it may make strict unseen-domain evaluation impossible while preserving participant independence. Defer the design decision to the split planner: it must reject that particular strict plan rather than remove the crossing observations silently.

For acquisition metadata not supplied, list exactly which checks were not assessable. Do not infer scanner manufacturer from a filename or infer diagnosis from a directory name. No medical term dictionary or hidden pattern extraction belongs here.

## 6.5 Implementation rules

Cohort checks are pure functions of validated input. They do not train models, load images, write output, modify input tables or use random numbers. Run checks in a documented stable order. One malformed field should not erase independent results that remain meaningful; however, structural identity corruption must stop set-based conclusions because the units cannot be trusted.

Known-answer examples must include a repeated-measure cohort with perfectly subject-disjoint splits that does not generate a confirmed-leakage finding; distinct people all having `ses-01`; a target that changes between visits; an exact feature collision that is not treated as verified identity; and a participant with legitimate cross-site visits.
