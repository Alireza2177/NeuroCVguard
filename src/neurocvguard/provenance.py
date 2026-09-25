"""Strict declarations and fit-boundary preparation; no fitting or authentication."""

from pathlib import Path

from neurocvguard.config import AuditConfig
from neurocvguard.errors import ConfigurationError, InputValidationError
from neurocvguard.identity import _valid_label, _validated_metadata
from neurocvguard.io import _plan_context
from neurocvguard.models import Cohort, LedgerEvent, PreprocessingLedger, SplitPlan


def _training_ids(plan: SplitPlan, repeat: str, fold: str, inner: str | None) -> tuple[str, ...]:
    outer = next((f for f in plan.folds if (f.repeat_id, f.fold_id) == (repeat, fold)), None)
    if outer is None:
        raise InputValidationError("Unknown repeat/fold reference; supply its matching split plan.")
    if inner is None:
        return outer.train_ids
    selected = next((f for f in outer.inner_folds or () if f.inner_fold_id == inner), None)
    if selected is None:
        raise InputValidationError("Unknown inner-fold reference within the named outer fold.")
    return selected.train_ids


def _validate_context(cohort: Cohort, config: AuditConfig, plan: SplitPlan | None) -> set[str]:
    if cohort.columns != config.columns:
        raise ConfigurationError("Cohort roles differ from config.columns; use matching roles.")
    data = _validated_metadata(cohort)
    ids = set(data[cohort.columns.observation_id])
    if plan is not None:
        _plan_context(cohort, plan, config)
        for outer in plan.folds:
            train, test = set(outer.train_ids), set(outer.test_ids)
            if train & test or train | test != ids:
                raise InputValidationError(
                    "Provenance context requires a disjoint complete outer partition."
                )
            for inner in outer.inner_folds or ():
                left, right = set(inner.train_ids), set(inner.validation_ids)
                if left & right or left | right != train:
                    raise InputValidationError(
                        "Provenance context requires inner partitions of outer train only."
                    )
    return ids


def _validate_event(event: LedgerEvent, known: set[str], plan: SplitPlan | None) -> None:
    labels = [event.event_id, event.repeat_id, event.fold_id, event.inner_fold_id]
    labels.extend(event.fit_ids or ())
    if any(value is not None and not _valid_label(value) for value in labels):
        raise InputValidationError(
            "Ledger identities require nonempty unpadded strings without controls."
        )
    if (event.repeat_id is None) != (event.fold_id is None):
        raise InputValidationError("Ledger repeat_id and fold_id must be supplied together.")
    if event.inner_fold_id is not None and event.fold_id is None:
        raise InputValidationError("An inner-fold reference requires its repeat and outer fold.")
    if event.fit_scope == "outer_train" and (
        event.fold_id is None or event.inner_fold_id is not None
    ):
        raise InputValidationError(
            "outer_train requires an outer fold and no inner-fold reference."
        )
    if event.fit_scope == "inner_train" and event.inner_fold_id is None:
        raise InputValidationError("inner_train requires a named inner fold.")
    if event.fit_ids is not None and not set(event.fit_ids) <= known:
        raise InputValidationError(
            "Ledger fit_ids include unknown observations; review the cohort mapping."
        )
    if plan is not None and event.repeat_id is not None and event.fold_id is not None:
        _training_ids(plan, event.repeat_id, event.fold_id, event.inner_fold_id)


def load_preprocessing_ledger(
    source: str | Path | dict[str, object],
    *,
    cohort: Cohort,
    config: AuditConfig,
    plan: SplitPlan | None = None,
) -> PreprocessingLedger:
    """Load local strict JSON declarations and validate identities and available context.

    Parameters
    ----------
    source : str, Path or dict
        Local .json path or strict schema-shaped dictionary. Never executable code.
    cohort : Cohort
        Constructed cohort defining known observation identities.
    config : AuditConfig
        Matching roles and maximum file size.
    plan : SplitPlan or None, optional
        Context for fold references. Without it, fold references remain unresolved
        and the corresponding boundary checks must be unassessable.

    Returns
    -------
    PreprocessingLedger
        Detached declarations with source=user_declaration, never runtime evidence.

    Raises
    ------
    InputValidationError, ConfigurationError, SplitValidationError
        Invalid JSON/source, IDs, scope/reference structure or supplied plan context.

    Examples
    --------
    ``load_preprocessing_ledger("ledger.json", cohort=cohort, config=config)``
    """
    known = _validate_context(cohort, config, plan)
    if isinstance(source, dict):
        ledger = PreprocessingLedger.from_dict(source)
    else:
        path = Path(source)
        if (
            "://" in str(source)
            or str(source).startswith(("\\\\", "//"))
            or path.suffix.lower() != ".json"
        ):
            raise InputValidationError("Use a local uncompressed .json preprocessing ledger.")
        limit = config.limits.max_input_mb * 1024 * 1024
        try:
            if not path.is_file() or path.stat().st_size > limit:
                raise InputValidationError("Ledger file is missing or exceeds limits.max_input_mb.")
            with path.open("rb") as handle:
                content = handle.read(limit + 1)
            if len(content) > limit:
                raise InputValidationError("Ledger exceeds limits.max_input_mb.")
            text = content.decode("utf-8-sig")
        except (OSError, UnicodeError):
            raise InputValidationError("Cannot read ledger as a local UTF-8 file.") from None
        ledger = PreprocessingLedger.from_json(text)
    if len({event.event_id for event in ledger.events}) != len(ledger.events):
        raise InputValidationError("Ledger event_id values must be unique.")
    for event in ledger.events:
        _validate_event(event, known, plan)
    return ledger
