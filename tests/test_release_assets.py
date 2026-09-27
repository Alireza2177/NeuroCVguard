"""Release publishing must reject different bytes or an absent owner decision."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release_assets", ROOT / "tools/verify_release_assets.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


@pytest.fixture
def release(tmp_path):
    directory = tmp_path / "dist"
    directory.mkdir()
    entries = []
    for suffix in ("-py3-none-any.whl", ".tar.gz"):
        name = "neurocvguard-0.1.0" + suffix
        content = b"synthetic test artifact " + suffix.encode()
        (directory / name).write_bytes(content)
        entries.append(
            {"file": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"version": "0.1.0", "artifacts": entries, "pypi_upload_authorized": False})
    )
    return manifest, directory


def test_approved_byte_identity_does_not_imply_permission(release):
    manifest, directory = release
    CHECK.verify(manifest, directory)
    with pytest.raises(ValueError, match="owner publication decision"):
        CHECK.verify(manifest, directory, require_authorization=True)


@pytest.mark.parametrize("change", ["same_size_bytes", "extra", "missing"])
def test_reject_changed_or_unreviewed_assets(release, change):
    manifest, directory = release
    path = directory / "neurocvguard-0.1.0.tar.gz"
    if change == "same_size_bytes":
        path.write_bytes(b"X" * path.stat().st_size)
    elif change == "extra":
        (directory / "private.json").write_text("{}")
    else:
        path.unlink()
    with pytest.raises(ValueError, match="SHA256 mismatch|exactly the two"):
        CHECK.verify(manifest, directory)
