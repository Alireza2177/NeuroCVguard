"""Explicit JSON configuration and immutable role mappings; no column inference."""

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from neurocvguard._paths import is_remote_path
from neurocvguard._records import Record
from neurocvguard.errors import ConfigurationError
from neurocvguard.serialization import JSONObject


class Objective(StrEnum):
    """The population/generalization claim, not a universal validity label."""

    UNSEEN_PARTICIPANT = "unseen_participant"
    UNSEEN_SITE = "unseen_site"
    UNSEEN_PHASE = "unseen_phase"
    AUDIT_ONLY = "audit_only"


class SplitScheme(StrEnum):
    """Supported declared partition schemes for imports and explicit plan generation."""

    SUBJECT_KFOLD = "subject_kfold"
    LEAVE_ONE_SITE_OUT = "leave_one_site_out"
    LEAVE_ONE_PHASE_OUT = "leave_one_phase_out"
    IMPORTED = "imported"


@dataclass(frozen=True)
class ConfigRecord(Record):
    """Structural configuration component with an explicit detached dictionary view."""

    _schema_name: ClassVar[str] = "config"
    _error_type = ConfigurationError

    def to_dict(self) -> JSONObject:
        """Return a mutable copy; configuration may contain sensitive column names.

        Returns
        -------
        JSONObject
            All configured fields and defaults; changing this copy cannot change the record.

        Examples
        --------
        >>> AuditConfig().to_dict()["schema_version"]
        '1.0'
        """
        return self._as_dict()


@dataclass(frozen=True)
class ColumnMap(ConfigRecord):
    """Explicit source columns; None means absent, never an inferred role.

    Parameters are the eight `columns` fields in config.schema.json. Scalar
    roles must be distinct. Independence/covariate lists are copied to tuples.
    The constructor defaults form the documented example, not a file-key fallback.
    """

    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "columns")
    observation_id: str = "observation_id"
    subject_id: str = "subject_id"
    target: str | None = "diagnosis"
    session: str | None = "session_id"
    site: str | None = "site"
    phase: str | None = None
    independence: tuple[str, ...] = ()
    categorical_covariates: tuple[str, ...] = ()

    def _validate_semantics(self) -> None:
        scalar = [
            self.observation_id,
            self.subject_id,
            self.target,
            self.session,
            self.site,
            self.phase,
        ]
        selected = [name for name in scalar if name is not None]
        if len(selected) != len(set(selected)):
            raise ConfigurationError(
                "columns: scalar role mappings collide; assign distinct columns."
            )
        if any(
            not name.strip()
            for name in (*selected, *self.independence, *self.categorical_covariates)
        ):
            raise ConfigurationError("columns: mapped names must be non-empty.")


@dataclass(frozen=True)
class StudyConfig(ConfigRecord):
    """Declared generalization objective (`study`)."""

    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "study")
    objective: Objective = Objective.UNSEEN_PARTICIPANT


@dataclass(frozen=True)
class SplitConfig(ConfigRecord):
    """Partition scheme, fold count and explicit deterministic seed (`split`)."""

    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "split")
    scheme: SplitScheme = SplitScheme.SUBJECT_KFOLD
    n_splits: int | None = 3
    seed: int = 2026

    def _validate_semantics(self) -> None:
        if (self.scheme == SplitScheme.SUBJECT_KFOLD) != (self.n_splits is not None):
            raise ConfigurationError(
                "split.n_splits must be an integer only for subject_kfold; null otherwise."
            )


@dataclass(frozen=True)
class AssociationConfig(ConfigRecord):
    """Descriptive review guardrails, not causal thresholds (`association`)."""

    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "association")
    review_threshold: float = 0.3
    min_cell_count: int = 5


@dataclass(frozen=True)
class EvaluationConfig(ConfigRecord):
    """Explicit feature and baseline settings (`evaluation`); no estimator is run."""

    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "evaluation")
    feature_columns: tuple[str, ...] = ("feature_1", "feature_2")
    tune: bool = False
    C: float = 1.0
    C_grid: tuple[float, ...] = (0.1, 1.0, 10.0)
    inner_splits: int = 3
    max_iter: int = 2000
    diagnostic_allow_subject_overlap: bool = False
    positive_class: str | None = None


@dataclass(frozen=True)
class ReportConfig(ConfigRecord):
    """Explicit sensitive-detail choice and public count suppression threshold."""

    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "report")
    sensitive_details: bool = False
    small_cell_threshold: int = 5


@dataclass(frozen=True)
class LimitsConfig(ConfigRecord):
    """Positive resource limits, including the optional 128 MB input-file default."""

    _schema_path: ClassVar[tuple[str | int, ...]] = ("properties", "limits")
    max_rows: int = 100000
    max_features: int = 10000
    max_dense_mb: int = 512
    max_input_mb: int = 128


@dataclass(frozen=True)
class AuditConfig(ConfigRecord):
    """Complete immutable configuration; JSON input must include all required fields.

    Calling AuditConfig() explicitly creates the specification's example defaults.
    from_dict/from_json never fill missing required fields. No table roles are
    guessed and no evaluation or splitting is performed during validation.
    """

    schema_version: str = "1.0"
    columns: ColumnMap = field(default_factory=ColumnMap)
    study: StudyConfig = field(default_factory=StudyConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    association: AssociationConfig = field(default_factory=AssociationConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)

    def _validate_semantics(self) -> None:
        expected = {
            SplitScheme.SUBJECT_KFOLD: Objective.UNSEEN_PARTICIPANT,
            SplitScheme.LEAVE_ONE_SITE_OUT: Objective.UNSEEN_SITE,
            SplitScheme.LEAVE_ONE_PHASE_OUT: Objective.UNSEEN_PHASE,
        }
        if self.study.objective != Objective.AUDIT_ONLY and self.split.scheme in expected:
            if self.study.objective != expected[self.split.scheme]:
                raise ConfigurationError(
                    "split.scheme does not match study.objective; "
                    "choose the intended design explicitly."
                )
        roles = self.columns.to_dict()
        forbidden = {value for value in roles.values() if isinstance(value, str)}
        forbidden.update(self.columns.independence)
        forbidden.update(self.columns.categorical_covariates)
        if forbidden.intersection(self.evaluation.feature_columns):
            raise ConfigurationError(
                "evaluation.feature_columns includes a mapped role, target "
                "or protected/covariate column."
            )
        # Empty features/absent targets are valid for inventory configuration.
        # The future evaluator must require them when evaluation is requested.


def load_config(path: str | Path, *, max_input_mb: int = 128) -> AuditConfig:
    """Read an explicitly named local JSON configuration with a pre-read size limit.

    Parameters
    ----------
    path : str or Path
        Local .json file; relative paths use the current working directory.
    max_input_mb : int, optional
        Positive file-size bound before parsing (default 128 MiB).

    Returns
    -------
    AuditConfig
        Detached immutable settings, with only documented optional defaults.

    Raises
    ------
    ConfigurationError
        Path, size, UTF-8, JSON, schema or cross-field validation failed.

    Examples
    --------
    ``config = load_config("fixtures/config.json")`` in the source workspace.
    """
    if type(max_input_mb) is not int or max_input_mb <= 0:
        raise ConfigurationError("max_input_mb must be a positive integer.")
    source = Path(path)
    if is_remote_path(path) or source.suffix.lower() != ".json":
        raise ConfigurationError("Use a local .json configuration file; URLs are unsupported.")
    try:
        if not source.is_file() or source.stat().st_size > max_input_mb * 1024 * 1024:
            raise ConfigurationError("Configuration file is missing or exceeds max_input_mb.")
        with source.open("rb") as handle:
            content = handle.read(max_input_mb * 1024 * 1024 + 1)
        if len(content) > max_input_mb * 1024 * 1024:
            raise ConfigurationError("Configuration file exceeds max_input_mb.")
        return AuditConfig.from_json(content.decode("utf-8-sig"))
    except (OSError, UnicodeError) as error:
        raise ConfigurationError("Cannot read configuration as a local UTF-8 JSON file.") from error
