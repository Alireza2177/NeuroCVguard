"""Compare downloaded release files to the owner's reviewed byte manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def verify(manifest: Path, directory: Path, *, require_authorization: bool = False) -> None:
    """Reject altered/extra files; local records never authenticate their author."""
    record = json.loads(manifest.read_text(encoding="utf-8"))
    if require_authorization and record.get("pypi_upload_authorized") is not True:
        raise ValueError("An explicit owner publication decision is required")
    version = record["version"]
    names = {f"neurocvguard-{version}-py3-none-any.whl", f"neurocvguard-{version}.tar.gz"}
    entries = record["artifacts"]
    if len(entries) != 2 or {entry["file"] for entry in entries} != names:
        raise ValueError("Manifest must identify exactly the wheel and sdist for this version")
    if {path.name for path in directory.iterdir()} != names:
        raise ValueError("Release directory must contain exactly the two approved artifacts")
    for entry in entries:
        path = directory / entry["file"]
        if path.is_symlink() or not path.is_file():
            raise ValueError("Release asset must be a regular file")
        if path.stat().st_size != entry["bytes"]:
            raise ValueError(f"Release size mismatch: {path.name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Release SHA256 mismatch: {path.name}")
    print(f"Verified exact wheel/sdist bytes for {version}; no rebuild performed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--require-authorization", action="store_true")
    args = parser.parse_args()
    verify(args.manifest, args.dist, require_authorization=args.require_authorization)


if __name__ == "__main__":
    main()
