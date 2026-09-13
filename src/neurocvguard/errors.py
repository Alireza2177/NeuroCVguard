"""Actionable domain errors; messages must not disclose research-row values."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neurocvguard.models import AuditReport


class NeuroCVguardError(ValueError):
    """Base error for invalid research-tool inputs or unsupported operations."""


class ConfigurationError(NeuroCVguardError):
    """Invalid configuration; correct the named field before retrying."""


class InputValidationError(NeuroCVguardError):
    """Malformed input or record; supply a compatible local contract document."""


class SplitValidationError(NeuroCVguardError):
    """Invalid split representation or membership; review the supplied plan."""


class UnsupportedDesignError(NeuroCVguardError):
    """A well-formed research design lies outside the supported scope."""


class PlanningError(UnsupportedDesignError):
    """Infeasible plan with a separate, sensitive diagnostic report; no usable plan."""

    def __init__(self, message: str, *, report: "AuditReport") -> None:
        super().__init__(message)
        self.report = report


class EvaluationError(NeuroCVguardError):
    """Invalid evaluation record or failed controlled evaluation."""
