"""S02.C limits, local-source boundaries and deterministic integrity hashes."""

from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
from test_feature_inputs import CONFIG, frames

from neurocvguard import load_cohort
from neurocvguard.errors import InputValidationError
from neurocvguard.io import cohort_digest, feature_digest


@pytest.mark.parametrize(
    "source",
    [
        "https://invalid.example/cohort.csv",
        "ftp://invalid.example/a.tsv",
        "a.xlsx",
        "a.pkl",
        "a.joblib",
        "a.csv.gz",
        "//host/share/a.tsv",
    ],
)
def test_at_s02_15_unsupported_sources(source, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unsupported input must fail before filesystem access")

    monkeypatch.setattr(Path, "is_file", forbidden)
    with pytest.raises(InputValidationError, match="local uncompressed"):
        load_cohort(source, config=CONFIG)


@pytest.mark.parametrize("guard", ["rows", "features", "dense"])
def test_at_s02_16_allocation_guard(guard, monkeypatch):
    import neurocvguard._tables as tables

    metadata, features = frames()
    if guard == "rows":
        config = replace(CONFIG, limits=replace(CONFIG.limits, max_rows=1))
    elif guard == "features":
        features["extra"] = 0
        config = replace(
            CONFIG,
            limits=replace(CONFIG.limits, max_features=1),
            evaluation=replace(CONFIG.evaluation, feature_columns=("value", "extra")),
        )
    else:
        names = tuple(f"f{i}" for i in range(1000))
        metadata = pd.DataFrame(
            {
                "observation_id": [f"o{i}" for i in range(200)],
                "subject_id": [f"p{i}" for i in range(200)],
            }
        )
        features = pd.DataFrame({"observation_id": list(metadata.observation_id)})
        config = replace(
            CONFIG,
            limits=replace(CONFIG.limits, max_dense_mb=1),
            evaluation=replace(CONFIG.evaluation, feature_columns=names),
        )
    original = pd.DataFrame.copy

    def guarded_copy(frame, *args, **kwargs):
        if frame is features or (guard == "rows" and frame is metadata):
            raise AssertionError("Oversized frame copied before guard")
        return original(frame, *args, **kwargs)

    monkeypatch.setattr(tables.pd.DataFrame, "copy", guarded_copy)
    with pytest.raises(InputValidationError, match="limits"):
        load_cohort(metadata, config=config, features=features)


def test_at_s02_17_digest_invariance():
    metadata, features = frames()
    first = load_cohort(metadata, config=CONFIG, features=features)
    reordered = load_cohort(metadata.iloc[::-1], config=CONFIG, features=features.iloc[::-1])
    assert cohort_digest(first) == cohort_digest(reordered)
    assert feature_digest(first) == feature_digest(reordered)
    metadata["unrelated"] = ["X", "Y"]
    assert cohort_digest(first) == cohort_digest(load_cohort(metadata, config=CONFIG))
    metadata.loc[8, "subject_id"] = "different"
    assert cohort_digest(first) != cohort_digest(load_cohort(metadata, config=CONFIG))


def test_at_s02_18_paths_with_spaces(tmp_path):
    directory = tmp_path / "فایل synthetic tables"
    directory.mkdir()
    metadata, features = frames()
    metadata.to_csv(directory / "cohort input.tsv", sep="\t", index=False, encoding="utf-8-sig")
    features.to_csv(directory / "features input.csv", index=False)
    result = load_cohort(
        directory / "cohort input.tsv", config=CONFIG, features=directory / "features input.csv"
    )
    assert result.observation_order == ("001", "1")
    assert list(result.features.value) == [10.0, 20.0]


def test_file_limit_before_read(tmp_path, monkeypatch):
    path = tmp_path / "large.tsv"
    path.write_bytes(b"x" * (1024 * 1024 + 1))
    config = replace(CONFIG, limits=replace(CONFIG.limits, max_input_mb=1))

    def forbidden(*args, **kwargs):
        raise AssertionError("File read before size check")

    monkeypatch.setattr(Path, "open", forbidden)
    with pytest.raises(InputValidationError, match="max_input_mb"):
        load_cohort(path, config=config)


def test_fixture_key_alignment_and_no_global_fill():
    from neurocvguard.config import load_config

    root = Path(__file__).parents[1] / "fixtures"
    config = load_config(root / "config.json")
    result = load_cohort(
        root / "cohort_clean.tsv", config=config, features=root / "features_shuffled.tsv"
    )
    original = pd.read_csv(root / "features_shuffled.tsv", sep="\t").set_index("observation_id")
    for name in config.evaluation.feature_columns:
        assert list(result.features[name]) == list(
            original.loc[list(result.observation_order), name]
        )


def test_nested_dataframe_cells_are_refused_without_mutation():
    metadata, _ = frames()
    metadata["unused"] = [[1], [2]]
    with pytest.raises(InputValidationError, match="scalars"):
        load_cohort(metadata, config=CONFIG)
    assert metadata.unused.iloc[0] == [1]
