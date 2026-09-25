"""Qualified declaration-based preprocessing findings; never reconstructed history."""

from neurocvguard.config import AuditConfig
from neurocvguard.models import CheckResult, CheckStatus, Cohort, EvidenceKind, Severity, SplitPlan
from neurocvguard.provenance import _training_ids, _validate_context, load_preprocessing_ledger
from neurocvguard.rules import get_rule
from neurocvguard.serialization import FrozenJSONValue


def _check(
    number: int,
    index: int,
    status: CheckStatus,
    scope: dict[str, str | int | None],
    evidence: dict[str, FrozenJSONValue],
) -> CheckResult:
    rule = get_rule(f"NCG-PROV-{number:03}")
    unknown = status == CheckStatus.NOT_ASSESSABLE
    message = (
        rule.clear_message
        if status in {CheckStatus.PASS, CheckStatus.NOT_APPLICABLE}
        else "The declared fitting boundary is unassessable from the supplied context."
        if unknown and number == 3
        else rule.trigger_message
    )
    return CheckResult(
        f"provenance-{number:03}-{index:04}",
        rule.id,
        status,
        Severity.WARNING
        if unknown
        else rule.trigger_severity
        if status == CheckStatus.FAIL
        else Severity.INFO,
        EvidenceKind.UNASSESSABLE if unknown else EvidenceKind.DECLARED,
        scope,
        message,
        rule.recommendation,
        evidence,
    )


def check_preprocessing(
    cohort: Cohort,
    *,
    config: AuditConfig,
    ledger: dict[str, object] | None = None,
    plan: SplitPlan | None = None,
) -> tuple[CheckResult, ...]:
    """Audit declarations against supplied training context without executing operations.

    Parameters
    ----------
    cohort : Cohort
        Known observation identities; feature values cannot establish fit history.
    config : AuditConfig
        Matching roles, objective and input limits.
    ledger : dict or None, optional
        Strict imported declaration contract. Absence and empty events remain unknown.
    plan : SplitPlan or None, optional
        Valid memberships for outer/inner training boundary comparison.

    Returns
    -------
    tuple of CheckResult
        Deterministic scoped declared/unassessable findings. An upstream limitation
        always remains, including when all explicit fit IDs lie inside training.

    Examples
    --------
    ``check_preprocessing(cohort, config=config, ledger=data, plan=plan)``
    """
    _validate_context(cohort, config, plan)
    parsed = (
        None
        if ledger is None
        else load_preprocessing_ledger(ledger, cohort=cohort, config=config, plan=plan)
    )
    checks = [
        _check(
            1,
            0,
            CheckStatus.NOT_ASSESSABLE,
            {"component": "upstream_preprocessing"},
            {
                "reason": "upstream_execution_unverified",
                "ledger_supplied": parsed is not None,
                "upstream_preprocessing_verified": False,
            },
        )
    ]
    for index, event in enumerate(
        sorted(parsed.events if parsed else (), key=lambda e: e.event_id), 1
    ):
        scope: dict[str, str | int | None] = {"component": "upstream_preprocessing"}
        for name in ("repeat_id", "fold_id", "inner_fold_id"):
            value = getattr(event, name)
            if value is not None:
                scope[name] = value
        evidence: dict[str, FrozenJSONValue] = {
            "source": "user_declaration",
            "event_id": event.event_id,
            "transform": event.transform,
            "data_dependent": event.data_dependent,
            "uses_target": event.uses_target,
            "fit_scope": event.fit_scope,
            "fit_ids": event.fit_ids,
            "execution_verified": False,
        }
        if not event.data_dependent:
            checks.append(_check(5, index, CheckStatus.NOT_APPLICABLE, scope, evidence))
            continue
        if event.fit_scope in {"external", "unknown"}:
            evidence["reason"] = (
                "external_provenance_unverified"
                if event.fit_scope == "external"
                else "unknown_fit_scope"
            )
            checks.append(_check(1, index, CheckStatus.NOT_ASSESSABLE, scope, evidence))
            continue
        if event.fit_scope == "all_cohort":
            checks.append(_check(2, index, CheckStatus.FAIL, scope, evidence))
            if event.fold_id is None:
                continue
        if plan is None or event.fit_ids is None:
            evidence = dict(
                evidence, reason="split_context_missing" if plan is None else "fit_ids_missing"
            )
            checks.append(_check(1, index, CheckStatus.NOT_ASSESSABLE, scope, evidence))
            continue
        assert event.repeat_id is not None and event.fold_id is not None
        allowed = set(_training_ids(plan, event.repeat_id, event.fold_id, event.inner_fold_id))
        outside = tuple(sorted(set(event.fit_ids) - allowed))
        evidence = dict(
            evidence,
            outside_training_ids=outside,
            outside_training_count=len(outside),
            declared_fit_count=len(event.fit_ids),
            permitted_training_count=len(allowed),
        )
        checks.append(
            _check(3, index, CheckStatus.FAIL if outside else CheckStatus.PASS, scope, evidence)
        )
    return tuple(sorted(checks, key=lambda c: (c.rule_id, c.instance_id)))
