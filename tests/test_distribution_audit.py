"""AT-S16-01/02/06: reject missing, altered and unexpected distribution payloads."""

import importlib.util
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "distribution_audit", ROOT / "tools/audit_distributions.py"
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def wheel(tmp_path, change=None):
    expected = {
        "neurocvguard/schemas/config.schema.json": b"{}",
        "neurocvguard/templates/report.css": b"body {}",
    }
    files = dict(expected)
    prefix = "neurocvguard-0.1.0.dist-info/"
    files.update({prefix + name: b"" for name in ("WHEEL", "RECORD", "licenses/LICENSE")})
    files[prefix + "METADATA"] = b"Name: neurocvguard\nVersion: 0.1.0\nRequires-Python: >=3.11\n"
    files[prefix + "entry_points.txt"] = (
        b"[console_scripts]\nneurocvguard = neurocvguard.__main__:main\n"
    )
    if change:
        change(files)
    path = tmp_path / "sample.whl"
    with zipfile.ZipFile(path, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)
    return path, expected


def test_at_s16_valid_payload_and_version(tmp_path):
    path, expected = wheel(tmp_path)
    assert len(AUDIT.audit_wheel(path, expected, "0.1.0")["members"]) == 7


@pytest.mark.parametrize(
    "name", ["neurocvguard/schemas/config.schema.json", "neurocvguard/templates/report.css"]
)
def test_at_s16_missing_runtime_asset_rejected(tmp_path, name):
    path, expected = wheel(tmp_path, lambda files: files.pop(name))
    with pytest.raises(AssertionError, match="Unexpected/missing"):
        AUDIT.audit_wheel(path, expected, "0.1.0")


@pytest.mark.parametrize(
    "name", ["private_data/cohort.csv", "../../outside", "neurocvguard/__pycache__/x.pyc"]
)
def test_at_s16_unexpected_private_or_unsafe_member_rejected(tmp_path, name):
    path, expected = wheel(tmp_path, lambda files: files.update({name: b"not allowed"}))
    with pytest.raises(AssertionError, match="Unexpected/missing"):
        AUDIT.audit_wheel(path, expected, "0.1.0")


def test_at_s16_payload_drift_rejected(tmp_path):
    path, expected = wheel(
        tmp_path, lambda files: files.update({"neurocvguard/templates/report.css": b"changed"})
    )
    with pytest.raises(AssertionError, match="Source mismatch"):
        AUDIT.audit_wheel(path, expected, "0.1.0")


def test_at_s16_metadata_version_drift_rejected(tmp_path):
    path, expected = wheel(
        tmp_path,
        lambda files: files.update(
            {
                "neurocvguard-0.1.0.dist-info/METADATA": (
                    b"Name: neurocvguard\nVersion: 9.9.9\nRequires-Python: >=3.11\n"
                )
            }
        ),
    )
    with pytest.raises(AssertionError):
        AUDIT.audit_wheel(path, expected, "0.1.0")


def test_at_s16_source_private_file_is_not_allowlisted(tmp_path):
    package = tmp_path / "src/neurocvguard"
    package.mkdir(parents=True)
    (package / "evaluation.private.json").write_text("{}")
    with pytest.raises(AssertionError, match="Unexpected runtime resource"):
        AUDIT.source_payload(tmp_path)
