"""Fictitious tabular mechanisms, not biologically realistic neuroimaging models."""

from dataclasses import asdict, dataclass, replace
from math import isfinite
from typing import cast

import numpy as np
import pandas as pd

from neurocvguard.config import AuditConfig, ColumnMap, EvaluationConfig, SplitConfig
from neurocvguard.errors import InputValidationError
from neurocvguard.serialization import JSONObject

SCENARIOS = ("clean", "repeated", "site_shift")
SYNTHETIC_NOTICE = (
    "Fully synthetic demonstration; no patient data. These are fictitious tabular "
    "mechanisms, not biologically realistic brain models or clinical results."
)


@dataclass(frozen=True)
class SyntheticParameters:
    """Explicit local RNG parameters; noise has fixed unit normal standard deviation.

    Signal, participant effect and site effect multiply independent standard
    normal vectors. site_target_association mixes independent site allocation
    with class-associated allocation (class modulo sites, or its next site with
    probability 0.25). Labels remain balanced and constant within participants.
    """

    seed: int = 2026
    n_participants: int = 60
    observations_per_participant: int = 2
    n_classes: int = 2
    n_sites: int = 3
    n_features: int = 8
    signal_strength: float = 1.0
    participant_effect: float = 0.5
    site_effect: float = 0.0
    site_target_association: float = 0.0

    def __post_init__(self) -> None:
        integers = (
            (self.seed, 0, 2**32 - 1),
            (self.n_participants, 2, 100_000),
            (self.observations_per_participant, 1, 100),
            (self.n_classes, 2, 100),
            (self.n_sites, 1, 100),
            (self.n_features, 1, 1000),
        )
        if any(type(v) is not int or not low <= v <= high for v, low, high in integers):
            raise InputValidationError(
                "Synthetic integer parameters are outside documented limits."
            )
        if max(self.n_classes, self.n_sites) > self.n_participants:
            raise InputValidationError("Class/site counts must not exceed participant count.")
        strengths = (self.signal_strength, self.participant_effect, self.site_effect)
        if any(
            type(v) not in (float, int) or not 0 <= v <= 100 or not isfinite(v) for v in strengths
        ):
            raise InputValidationError("Synthetic strengths must be finite numbers in [0, 100].")
        association = self.site_target_association
        if (
            type(association) not in (float, int)
            or not 0 <= association <= 1
            or not isfinite(association)
        ):
            raise InputValidationError("site_target_association must be in [0, 1].")
        # Bound allocations before constructing noise or long-form feature tables.
        if self.n_participants * self.observations_per_participant * self.n_features > 2_000_000:
            raise InputValidationError("Synthetic feature allocation exceeds 2,000,000 values.")

    def to_dict(self) -> JSONObject:
        return cast(JSONObject, asdict(self))


@dataclass(frozen=True)
class SyntheticData:
    """Owned mutable DataFrames with explicit fictitious keys and fixed parameters."""

    metadata: pd.DataFrame
    features: pd.DataFrame
    parameters: SyntheticParameters

    def config(self) -> AuditConfig:
        """Explicit mapping for these generated tables; no inference from filenames."""
        return AuditConfig(
            columns=ColumnMap(target="target", session="session"),
            split=SplitConfig(seed=self.parameters.seed),
            evaluation=EvaluationConfig(
                feature_columns=tuple(self.features.columns[1:]), positive_class="class-1"
            ),
        )


def scenario_parameters(scenario: str = "clean", **overrides: int | float) -> SyntheticParameters:
    """Documented presets with explicit overrides; no seed or score search.

    repeated changes only participant_effect to 3.0. site_shift changes only
    site_effect to 2.0 and site_target_association to 0.8. All other defaults
    match clean, including two visits per person and seed 2026.
    """
    if scenario not in SCENARIOS:
        raise InputValidationError("Choose clean, repeated or site_shift.")
    parameters = SyntheticParameters()
    if scenario == "repeated":
        parameters = replace(parameters, participant_effect=3.0)
    elif scenario == "site_shift":
        parameters = replace(parameters, site_effect=2.0, site_target_association=0.8)
    try:
        values = asdict(parameters)
        values.update(overrides)
        return SyntheticParameters(**values)
    except TypeError:
        raise InputValidationError("Unknown synthetic parameter; use documented fields.") from None


def generate_synthetic(parameters: SyntheticParameters | None = None) -> SyntheticData:
    """Generate keyed synthetic tables without touching global NumPy/Python RNG state.

    Six independent local streams draw label order, site allocation, class
    vectors, participant vectors, site vectors and observation noise. Changing
    an effect strength consumes no different draws or changes labels/identities.
    Site association changes allocation only; class labels are never relabeled.
    """
    p = SyntheticParameters() if parameters is None else parameters
    if not isinstance(p, SyntheticParameters):
        raise InputValidationError("Supply SyntheticParameters.")
    # Revalidate even a deliberately modified frozen instance before allocation.
    p = SyntheticParameters(**asdict(p))
    label_rng, site_rng, class_rng, person_rng, effect_rng, noise_rng = (
        np.random.default_rng(seed) for seed in np.random.SeedSequence(p.seed).spawn(6)
    )
    labels = label_rng.permutation(np.arange(p.n_participants) % p.n_classes)
    base_sites = site_rng.integers(p.n_sites, size=p.n_participants)
    favored_sites = (labels + (site_rng.random(p.n_participants) < 0.25)) % p.n_sites
    sites = np.where(
        site_rng.random(p.n_participants) < p.site_target_association, favored_sites, base_sites
    )
    class_vectors = class_rng.normal(size=(p.n_classes, p.n_features))
    person_vectors = person_rng.normal(size=(p.n_participants, p.n_features))
    site_vectors = effect_rng.normal(size=(p.n_sites, p.n_features))
    noise = noise_rng.normal(size=(p.n_participants, p.observations_per_participant, p.n_features))
    values = (
        noise
        + (
            p.signal_strength * class_vectors[labels]
            + p.participant_effect * person_vectors
            + p.site_effect * site_vectors[sites]
        )[:, None, :]
    )
    people = np.repeat(np.arange(p.n_participants), p.observations_per_participant)
    visits = np.tile(np.arange(p.observations_per_participant), p.n_participants)
    keys = [
        f"SYN-obs-{person:06d}-{visit:03d}" for person, visit in zip(people, visits, strict=True)
    ]
    metadata = pd.DataFrame(
        {
            "observation_id": keys,
            "subject_id": [f"SYN-person-{person:06d}" for person in people],
            "session": [f"visit-{visit:03d}" for visit in visits],
            "target": [f"class-{label}" for label in labels[people]],
            "site": [f"SYN-site-{site:03d}" for site in sites[people]],
            "data_kind": "fully_synthetic_no_patient_data",
        }
    )
    features = pd.DataFrame(
        values.reshape(-1, p.n_features),
        columns=[f"feature_{i:03d}" for i in range(p.n_features)],
    )
    features.insert(0, "observation_id", keys)
    return SyntheticData(metadata, features, p)
