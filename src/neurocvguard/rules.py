"""Fixed implemented rule metadata, not a dynamic registry or user-code mechanism."""

from dataclasses import dataclass

from neurocvguard.models import CheckStatus, EvidenceKind, Severity


@dataclass(frozen=True)
class RuleDefinition:
    """A stable catalog entry and scoped public wording; no research identifiers."""

    id: str
    name: str
    trigger_severity: Severity
    evidence_kind: EvidenceKind
    meaning: str
    trigger_message: str
    clear_message: str
    recommendation: str
    stage: str = "S03"


COHORT_RULES = (
    RuleDefinition(
        "NCG-COHORT-001",
        "Repeated observations",
        Severity.INFO,
        EvidenceKind.OBSERVED,
        "Inventory notice; repeated people are not by themselves a split violation.",
        "This cohort has repeated participant observations; "
        "evaluate separation in the actual splits.",
        "No repeated participant observations were observed.",
        "Evaluate participant separation in the actual supplied splits.",
    ),
    RuleDefinition(
        "NCG-COHORT-002",
        "Within-participant target variation",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Valid longitudinal possibility; baseline/stratified planning unsupported "
        "without explicit curation.",
        "Targets vary within participants. This may be meaningful; the constant-target baseline "
        "and stratified planner do not support this cohort.",
        "Targets are constant within participants in the supplied cohort.",
        "For the constant-target baseline, explicitly curate a supported cohort upstream; "
        "do not automatically relabel visits.",
    ),
    RuleDefinition(
        "NCG-COHORT-003",
        "Within-participant domain variation",
        Severity.INFO,
        EvidenceKind.OBSERVED,
        "Describe crossing sites/phases; strict domain planning must assess feasibility.",
        "Within-participant site/phase variation is descriptive; assess strict domain feasibility "
        "while preserving participant identity.",
        "No within-participant variation was observed for this supplied domain field.",
        "Preserve cross-domain identities; assess the requested held-out-domain plan separately.",
    ),
    RuleDefinition(
        "NCG-COHORT-004",
        "Exact feature equality across IDs",
        Severity.WARNING,
        EvidenceKind.HEURISTIC,
        "Observed equal vectors suggest review, not verified duplicate identity.",
        "Exact selected-feature vectors match across participants. Review this heuristic finding; "
        "it does not establish duplicate identity or duplicated images.",
        "No exact cross-participant equality was found among the assessed feature vectors. "
        "This does not prove that acquisitions are distinct.",
        "Investigate equality without merging identities or dropping rows; add a protected "
        "relationship only after independent verification.",
    ),
    RuleDefinition(
        "NCG-COHORT-005",
        "Missing optional metadata",
        Severity.WARNING,
        EvidenceKind.UNASSESSABLE,
        "Requested checks without required metadata are not_assessable.",
        "A metadata-dependent check has incomplete coverage; absent values were not inferred.",
        "This metadata coverage notice is not applicable.",
        "Supply the explicitly mapped metadata or retain incomplete assessment coverage.",
    ),
    RuleDefinition(
        "NCG-COHORT-006",
        "Missing protected relationship data",
        Severity.ERROR,
        EvidenceKind.UNASSESSABLE,
        "Strict splitting/evaluation blocked; unknown values not treated as independent.",
        "Protected relationship coverage is incomplete. Strict planning/evaluation is blocked; "
        "unknown values are not grouped or assumed independent.",
        "No incomplete protected relationship was found.",
        "Resolve the declared relationship values upstream before strict planning/evaluation.",
    ),
)


SPLIT_RULES = (
    RuleDefinition(
        "NCG-SPLIT-001",
        "Observation train/test overlap",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Never waived, including diagnostic evaluation.",
        "Observation membership overlaps across this split; this is invalid even in "
        "diagnostic runs.",
        "No observation overlap detected in this supplied split.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-002",
        "Participant train/test overlap",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Violation for supported unseen-person objectives; warning under audit_only.",
        "Participant overlap was detected; interpret severity under the stated objective.",
        "No participant overlap detected in this supplied split.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-003",
        "Protected-component overlap",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Crossing a declared dependence component invalidates the stated independent-unit design.",
        "Protected components cross this supplied split.",
        "No protected-component overlap detected in this supplied split.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-004",
        "Requested held-out domain overlaps",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Only a separation violation for the corresponding unseen_site/unseen_phase objective.",
        "The requested held-out domain occurs on both sides of this split.",
        "No overlap detected for the requested held-out domain.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-005",
        "Training class missing",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Cannot fit the requested full-class baseline for that fold.",
        "Training lacks the requested class space; ordinary evaluation is blocked for this fold.",
        "Training represents all global classes.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-006",
        "Test class missing",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Class-complete metrics undefined for this fold; retain other meaningful results.",
        "Test class coverage is incomplete; class-complete metrics are undefined, not zero.",
        "Test represents all global classes.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-007",
        "Unknown or duplicate membership",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Structural membership diagnostic; reject invalid identity mapping.",
        "Unknown or duplicate membership prevents trustworthy identity mapping.",
        "All supplied observation keys are recognized.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-008",
        "Per-fold cohort coverage broken",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "No silent exclusions or automatic row intersection.",
        "Per-fold membership does not cover the complete supplied cohort.",
        "This fold covers the complete supplied cohort.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-009",
        "Inner rows escape outer train",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Outer test or unknown IDs appear in an inner partition.",
        "Inner membership escapes outer training or includes outer test.",
        "Inner membership stays within outer training and excludes outer test.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-010",
        "Inner partitions overlap or lack coverage",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Inner training/validation identities/components and completeness must hold.",
        "Inner partition separation or validation coverage is invalid.",
        "The scoped inner partition/coverage check passed.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
    RuleDefinition(
        "NCG-SPLIT-011",
        "Complete-CV coverage unavailable",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "A valid one-off holdout is auditable but outside complete-CV evaluation.",
        "Complete-CV coverage is unavailable; ordinary baseline eligibility is separate.",
        "The scoped complete-CV coverage check passed.",
        "Review explicit assignments and their objective; do not silently repair, drop "
        "or relabel rows.",
        stage="S04",
    ),
)


PLAN_RULES = (
    RuleDefinition(
        "NCG-PLAN-001",
        "Insufficient independent groups",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Requested fold count cannot be satisfied; do not downgrade automatically.",
        "Requested fold count cannot be satisfied; do not downgrade automatically.",
        "The scoped planning prerequisite passed; exact class balance is not promised.",
        "Review the explicit design and independent units; no rows, "
        "labels, seeds or fold counts are automatically changed.",
        stage="S05",
    ),
    RuleDefinition(
        "NCG-PLAN-002",
        "Protected component crosses held-out domain",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Strict domain plan rejected without removing or relabeling observations.",
        "Strict domain plan rejected without removing or relabeling observations.",
        "The scoped planning prerequisite passed; exact class balance is not promised.",
        "Review the explicit design and independent units; no rows, "
        "labels, seeds or fold counts are automatically changed.",
        stage="S05",
    ),
    RuleDefinition(
        "NCG-PLAN-003",
        "Stratification/class feasibility limitation",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Document absent test-class feasibility; invalid actual training folds block plan.",
        "Document absent test-class feasibility; invalid actual training folds block plan.",
        "The scoped planning prerequisite passed; exact class balance is not promised.",
        "Review the explicit design and independent units; no rows, "
        "labels, seeds or fold counts are automatically changed.",
        stage="S05",
    ),
)


ASSOCIATION_RULES = (
    RuleDefinition(
        "NCG-ASSOC-001",
        "Association review threshold crossed",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Descriptive review signal, not proof of causal confounding or shortcut use.",
        "Acquisition/target association warrants review under the stated generalization objective.",
        "The descriptive association is below the configured review threshold; "
        "this is not a validity verdict.",
        "Review acquisition/target distributions under the stated objective. "
        "For a claim about new sites or phases, consider the corresponding held-out-domain "
        "design; do not infer causal bias or model shortcut use.",
        stage="S06",
    ),
    RuleDefinition(
        "NCG-ASSOC-002",
        "Sparse contingency table",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Small observed/expected counts make interpretation unstable; no p-value.",
        "Small observed or expected cells can make the descriptive association estimate unstable.",
        "No observed or expected cells are below the configured sparse-count threshold.",
        "Review sample coverage and sparse cells before interpreting the descriptive estimate; "
        "do not infer significance or merge categories automatically.",
        stage="S06",
    ),
    RuleDefinition(
        "NCG-ASSOC-003",
        "Association not assessable",
        Severity.WARNING,
        EvidenceKind.UNASSESSABLE,
        "Missing, constant, unstable or excessive-category input prevents specified statistic.",
        "The participant-level association is not assessable for this pair; "
        "review the recorded reason.",
        "This rule is reserved for an unassessable association.",
        "Review missing values and within-person stability. For excessive categories, "
        "check whether the field is an identifier; do not choose a visit or merge levels "
        "automatically.",
        stage="S06",
    ),
)


PROVENANCE_RULES = (
    RuleDefinition(
        "NCG-PROV-001",
        "Upstream fitting history unknown",
        Severity.WARNING,
        EvidenceKind.UNASSESSABLE,
        "No automatic certification from a supplied feature matrix.",
        "Upstream preprocessing remains unassessable; declarations do not verify execution.",
        "Upstream preprocessing remains unassessable; declarations do not verify execution.",
        "Document the source, overlap and fitting scope of upstream transformations. "
        "A controlled Pipeline cannot repair earlier global fitting.",
        stage="S07",
    ),
    RuleDefinition(
        "NCG-PROV-002",
        "Declared global data-dependent fitting",
        Severity.WARNING,
        EvidenceKind.DECLARED,
        "User-declared information use outside training scope; not reconstructed history.",
        "The user declares data-dependent fitting on all cohort observations; "
        "this is a declared global-fit warning, not observed historical proof.",
        "No declared global-fit finding applies to this event.",
        "Review the declared global learning and repeat learned preprocessing within "
        "the relevant training subsets where feasible; later pipelines cannot undo it.",
        stage="S07",
    ),
    RuleDefinition(
        "NCG-PROV-003",
        "Declared fitting IDs violate scope",
        Severity.ERROR,
        EvidenceKind.DECLARED,
        "Qualified declaration-based boundary finding; does not prove historical execution.",
        "Declared fitting IDs extend outside the relevant training subset; "
        "this finding does not prove historical execution.",
        "Declared fitting IDs are within the supplied training subset; execution is not verified.",
        "Review the event and matching outer/inner plan. Supply explicit fit IDs and "
        "restrict data-dependent learning to that training subset.",
        stage="S07",
    ),
    RuleDefinition(
        "NCG-PROV-005",
        "Declared fixed non-learning transform",
        Severity.INFO,
        EvidenceKind.DECLARED,
        "No training-fit isolation requirement solely for a fixed row-local conversion.",
        "The operation is declared non-learning; this does not authenticate its behavior.",
        "No training-fit isolation requirement follows solely from a declared fixed "
        "row-local conversion; the non-learning declaration is not verified.",
        "Confirm that the declared operation is fixed and row-local and assess any "
        "target use separately; do not infer safety of other upstream operations.",
        stage="S07",
    ),
)


REPORT_RULES = (
    RuleDefinition(
        "NCG-REPORT-001",
        "Sensitive operational output",
        Severity.INFO,
        EvidenceKind.OBSERVED,
        "Identity-bearing split/private evaluation artifact; not a public report.",
        "Operational split/private evaluation records contain sensitive identities.",
        "This report does not export operational split or private evaluation records.",
        "Keep operational records separate from public reports and review "
        "authorization before sharing.",
        stage="S08",
    ),
)


EVALUATION_RULES = (
    RuleDefinition(
        "NCG-PROV-004",
        "Observed internal fit scope violation",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Controlled runner defect; block successful evaluation and investigate.",
        "An internal fitting boundary violation prevented successful evaluation.",
        "The controlled fit used the permitted training boundary.",
        "Stop using this run and investigate the runner's fit isolation.",
        stage="S10",
    ),
    RuleDefinition(
        "NCG-EVAL-001",
        "Fit failed or did not converge",
        Severity.ERROR,
        EvidenceKind.OBSERVED,
        "Incomplete run, no complete pooled score.",
        "A controlled fold failed or did not converge; no complete pooled score is available.",
        "The requested controlled fitting completed.",
        "Review feature scale, numeric inputs and iteration limits explicitly; "
        "do not omit failed folds.",
        stage="S10",
    ),
    RuleDefinition(
        "NCG-EVAL-002",
        "Metric undefined",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Null value plus specific reason; never substitute zero/NaN.",
        "A metric is undefined for this scored set; retain its null value and reason.",
        "The metric is defined for the supplied coverage.",
        "Inspect class support and the explicit positive class; do not substitute zero for null.",
        stage="S10",
    ),
    RuleDefinition(
        "NCG-EVAL-004",
        "Training feature entirely missing",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Document no training information and prescribed fold-local imputer handling.",
        "A feature has no training information in this fold; "
        "the imputer retains it with zero fill.",
        "Every feature has at least one observed training value.",
        "Review missingness upstream; never estimate a fill value from held-out observations.",
        stage="S10",
    ),
)


DIAGNOSTIC_RULES = (
    RuleDefinition(
        "NCG-EVAL-003",
        "Intentionally invalid diagnostic evaluation",
        Severity.WARNING,
        EvidenceKind.OBSERVED,
        "Do not use as evidence for unseen-participant generalization.",
        "Diagnostic only; valid_for_objective=false. Do not report as evidence for "
        "unseen-participant generalization. "
        "Participant aggregation does not repair training leakage.",
        "No intentional diagnostic evaluation was performed.",
        "Use an explicitly justified participant-disjoint design for an unseen-participant claim.",
        stage="S12",
    ),
)


def get_rule(rule_id: str) -> RuleDefinition:
    """Return fixed rule metadata.

    Parameters
    ----------
    rule_id : str
        An implemented NCG-COHORT, NCG-SPLIT, NCG-PLAN NCG-ASSOC or NCG-PROV rule ID.

    Returns
    -------
    RuleDefinition
        Immutable metadata in catalog order.

    Raises
    ------
    KeyError
        The requested rule is not implemented here.

    Examples
    --------
    >>> get_rule("NCG-COHORT-001").stage
    'S03'
    """
    for rule in (
        *COHORT_RULES,
        *SPLIT_RULES,
        *PLAN_RULES,
        *ASSOCIATION_RULES,
        *PROVENANCE_RULES,
        *REPORT_RULES,
        *EVALUATION_RULES,
        *DIAGNOSTIC_RULES,
    ):
        if rule.id == rule_id:
            return rule
    raise KeyError(rule_id)


def _public_message(rule_id: str, status: CheckStatus) -> str:
    rule = get_rule(rule_id)
    if status == CheckStatus.NOT_ASSESSABLE:
        if rule_id in {"NCG-COHORT-005", "NCG-COHORT-006"}:
            return rule.trigger_message
        return "This cohort check has incomplete input coverage and remains unassessable."
    if status == CheckStatus.NOT_APPLICABLE:
        return "This cohort check was not requested or does not apply to the supplied inputs."
    if rule_id in {"NCG-COHORT-001", "NCG-COHORT-003"} or status == CheckStatus.FAIL:
        return rule.trigger_message
    return rule.clear_message
