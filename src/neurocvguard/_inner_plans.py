"""Derive inner memberships from outer training only, without fitting anything."""

from dataclasses import replace

from neurocvguard.config import AuditConfig, Objective, SplitConfig, SplitScheme
from neurocvguard.io import load_cohort
from neurocvguard.models import Cohort, InnerFold, SplitPlan
from neurocvguard.serialization import json_digest
from neurocvguard.splitting import make_splits


def with_inner_plans(cohort: Cohort, plan: SplitPlan, config: AuditConfig) -> SplitPlan:
    """Retain supplied assignments; generate missing ones on explicit keyed subsets.

    The caller audits outer and supplied inner memberships before this function,
    and audits the complete derived plan afterward. No alternate seed is tried.
    """
    if all(fold.inner_folds for fold in plan.folds):
        return plan
    inner_config = replace(
        config,
        study=replace(config.study, objective=Objective.UNSEEN_PARTICIPANT),
        split=SplitConfig(
            SplitScheme.SUBJECT_KFOLD, config.evaluation.inner_splits, config.split.seed
        ),
        evaluation=replace(config.evaluation, tune=False),
    )
    metadata = cohort.metadata.set_index(config.columns.observation_id, drop=False)
    folds = []
    for fold in sorted(plan.folds, key=lambda item: (item.repeat_id, item.fold_id)):
        if fold.inner_folds:
            folds.append(fold)
            continue
        subset = load_cohort(
            metadata.loc[list(fold.train_ids)].reset_index(drop=True), config=inner_config
        )
        generated = make_splits(subset, config=inner_config)
        folds.append(
            replace(
                fold,
                inner_folds=tuple(
                    InnerFold(inner.fold_id, inner.train_ids, inner.test_ids)
                    for inner in generated.folds
                ),
            )
        )
    payload = plan.to_operational_dict()
    payload.pop("plan_id")
    payload["folds"] = [fold._as_dict() for fold in folds]
    return SplitPlan.from_dict({**payload, "plan_id": json_digest(payload)})
