"""S17 local checkpoint must retain missing consent and candidate drift."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release_preflight", ROOT / "tools/release_preflight.py"
)
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


@pytest.fixture
def candidate(tmp_path):
    """Tiny synthetic release metadata, never an actual owner approval."""
    for directory in ("state", "qa/evidence/S16", "dist", "src/neurocvguard"):
        (tmp_path / directory).mkdir(parents=True)
    files = {
        "src/neurocvguard/__init__.py": b"__version__ = '0.1.0'\n",
        "LICENSE": b"PROPOSED LICENSE - NOT FINALIZED\n",
    }
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
    metadata = '[tool.neurocvguard.release]\nmaintainer = "PENDING_MAINTAINER_CONFIRMATION"\n'
    (tmp_path / "pyproject.toml").write_text(metadata)
    (tmp_path / "state/PROJECT_STATUS.json").write_text(
        json.dumps(
            {
                "target_release": "0.1.0",
                "public_release_authorized": False,
                "stages": [{"id": "S16", "human_accepted": False}],
            }
        )
    )
    wheel = b"synthetic bytes, not an installable wheel"
    (tmp_path / "dist/example.whl").write_bytes(wheel)
    (tmp_path / "qa/evidence/S16/distributions.json").write_text(
        json.dumps(
            {
                "version": "0.1.0",
                "artifacts": [
                    {
                        "file": "example.whl",
                        "bytes": len(wheel),
                        "sha256": hashlib.sha256(wheel).hexdigest(),
                    }
                ],
                "source_payload_hashes": {
                    "neurocvguard/__init__.py": hashlib.sha256(
                        files["src/neurocvguard/__init__.py"]
                    ).hexdigest()
                },
            }
        )
    )
    (tmp_path / "qa/evidence/S16/preservation.json").write_text(
        json.dumps(
            {
                "candidate_metadata_hashes": {
                    "LICENSE": hashlib.sha256(files["LICENSE"]).hexdigest()
                },
            }
        )
    )
    return tmp_path


def test_missing_real_owner_and_approval_stays_blocked(candidate):
    record = PREFLIGHT.inspect_candidate(candidate, candidate / "dist")
    assert record["status"] == "BLOCKED" and not record["publication_performed"]
    assert "Owner confirmation missing: maintainer" in record["blockers"]
    assert "Human stage acceptance pending: S16" in record["blockers"]
    assert "Project public-release authorization is absent" in record["blockers"]
    assert record["artifacts"][0]["matches_candidate"] and not record["source_drift"]


@pytest.mark.parametrize("change", ["changed", "missing"])
def test_artifact_tamper_or_absence_retained(candidate, change):
    path = candidate / "dist/example.whl"
    if change == "changed":
        path.write_bytes(b"not the reviewed bytes")
    else:
        path.unlink()
    record = PREFLIGHT.inspect_candidate(candidate, candidate / "dist")
    assert not record["artifacts"][0]["matches_candidate"]
    assert "Retained artifact missing or changed: example.whl" in record["blockers"]


@pytest.mark.parametrize("name", ["src/neurocvguard/__init__.py", "LICENSE"])
def test_new_source_or_owner_metadata_requires_new_candidate(candidate, name):
    (candidate / name).write_text("changed")
    record = PREFLIGHT.inspect_candidate(candidate, candidate / "dist")
    assert record["source_drift"] == [name]
    assert "Source/metadata changed: rebuild and review new candidate hashes" in record["blockers"]


def test_target_version_must_match_reviewed_artifact(candidate):
    path = candidate / "state/PROJECT_STATUS.json"
    data = json.loads(path.read_text())
    data["target_release"] = "9.9.9"
    path.write_text(json.dumps(data))
    record = PREFLIGHT.inspect_candidate(candidate, candidate / "dist")
    assert "Target version differs from retained candidate" in record["blockers"]


def test_local_flags_never_grant_publication(candidate):
    path = candidate / "state/PROJECT_STATUS.json"
    data = json.loads(path.read_text())
    data["public_release_authorized"] = True
    data["stages"][0]["human_accepted"] = True
    path.write_text(json.dumps(data))
    (candidate / "pyproject.toml").write_text(
        "[tool.neurocvguard.release]\npublic-release-authorized = true\n"
        + "\n".join(
            f'{key} = "synthetic test value"'
            for key in (
                "license-status",
                "copyright-owner",
                "maintainer",
                "security-contact",
                "repository-url",
                "package-namespace",
            )
        )
    )
    (candidate / "LICENSE").write_text("synthetic license fixture")
    path = candidate / "qa/evidence/S16/preservation.json"
    path.write_text(json.dumps({"candidate_metadata_hashes": {}}))
    record = PREFLIGHT.inspect_candidate(candidate, candidate / "dist")
    assert record["status"] == "LOCAL_CHECKS_PASS_REQUIRES_HUMAN_DECISION"
    assert not record["publication_performed"] and record["still_requires"]


def test_explicit_new_candidate_does_not_rewrite_historical_evidence(candidate):
    original = candidate / "qa/evidence/S16/distributions.json"
    before = original.read_bytes()
    (candidate / "LICENSE").write_text("new approved license fixture")
    (candidate / "README.md").write_text("new metadata")
    (candidate / ".gitignore").write_text("dist/\n")
    data = json.loads(before)
    data["candidate_metadata_hashes"] = {
        name: hashlib.sha256((candidate / name).read_bytes()).hexdigest()
        for name in ("pyproject.toml", "README.md", "LICENSE", ".gitignore")
    }
    manifest = candidate / "new-candidate.json"
    manifest.write_text(json.dumps(data))
    result = PREFLIGHT.inspect_candidate(candidate, candidate / "dist", manifest)
    assert not result["source_drift"]
    assert original.read_bytes() == before
    data["candidate_metadata_hashes"].pop("LICENSE")
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="all four metadata hashes"):
        PREFLIGHT.inspect_candidate(candidate, candidate / "dist", manifest)
