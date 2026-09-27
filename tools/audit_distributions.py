"""Inspect local wheel/sdist payloads against the exact selected source tree."""

import argparse
import ast
import hashlib
import json
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_payload(root):
    files = {}
    package = root / "src/neurocvguard"
    for path in package.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(package)
            allowed = (
                path.suffix == ".py"
                or relative.as_posix() == "py.typed"
                or relative.as_posix() in {"templates/report.html", "templates/report.css"}
                or (relative.parent.as_posix() == "schemas" and path.name.endswith(".schema.json"))
            )
            assert allowed, f"Unexpected runtime resource: {relative}"
            files["neurocvguard/" + relative.as_posix()] = path.read_bytes()
    for path in (root / "examples").glob("*.py"):
        files["neurocvguard/examples/" + path.name] = path.read_bytes()
    return files


def audit_wheel(path, expected, version):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), "Duplicate archive member"
        metadata_root = f"neurocvguard-{version}.dist-info/"
        allowed = set(expected) | {
            metadata_root + name
            for name in ("METADATA", "WHEEL", "RECORD", "entry_points.txt", "licenses/LICENSE")
        }
        assert set(names) == allowed, f"Unexpected/missing wheel files: {set(names) ^ allowed}"
        for name, content in expected.items():
            assert archive.read(name) == content, f"Source mismatch: {name}"
        metadata = BytesParser().parsebytes(archive.read(metadata_root + "METADATA"))
        assert metadata["Name"] == "neurocvguard" and metadata["Version"] == version
        assert metadata["Requires-Python"] == ">=3.11"
        assert (
            "neurocvguard = neurocvguard.__main__:main"
            in archive.read(metadata_root + "entry_points.txt").decode()
        )
        return {
            "members": sorted(names),
            "requires_dist": metadata.get_all("Requires-Dist"),
            "license_notice_sha256": digest(archive.read(metadata_root + "licenses/LICENSE")),
        }


def audit_sdist(path, root, expected, version):
    prefix = f"neurocvguard-{version}/"
    payload = {}
    for name, content in expected.items():
        key = name.replace("neurocvguard/examples/", "examples/", 1)
        if key.startswith("neurocvguard/"):
            key = "src/" + key
        payload[prefix + key] = content
    for name in ("pyproject.toml", "README.md", "LICENSE", ".gitignore"):
        payload[prefix + name] = (root / name).read_bytes()
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        assert len(names) == len(set(names)), "Duplicate sdist member"
        assert all(m.isfile() and not PurePosixPath(m.name).is_absolute() for m in members)
        assert set(names) == set(payload) | {prefix + "PKG-INFO"}, "Unexpected/missing sdist files"
        for name, content in payload.items():
            assert archive.extractfile(name).read() == content, f"Source mismatch: {name}"
        metadata = BytesParser().parsebytes(archive.extractfile(prefix + "PKG-INFO").read())
        assert metadata["Name"] == "neurocvguard" and metadata["Version"] == version
    return {"members": sorted(names)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), "Refuse to overwrite evidence"
    tree = ast.parse((args.root / "src/neurocvguard/__init__.py").read_text(encoding="utf-8"))
    version = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets)
    )
    expected = source_payload(args.root)
    files = sorted(args.dist.iterdir())
    assert {p.name for p in files} == {
        f"neurocvguard-{version}-py3-none-any.whl",
        f"neurocvguard-{version}.tar.gz",
    }
    artifacts = []
    for path in files:
        detail = (
            audit_wheel(path, expected, version)
            if path.suffix == ".whl"
            else audit_sdist(path, args.root, expected, version)
        )
        artifacts.append(
            {
                "file": path.name,
                "bytes": path.stat().st_size,
                "sha256": digest(path.read_bytes()),
                **detail,
            }
        )
    record = {
        "version": version,
        "artifacts": artifacts,
        "source_payload_hashes": {n: digest(b) for n, b in sorted(expected.items())},
        "scope": "Exact archive allowlist and byte equality; no application or license approval.",
    }
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(f"Verified {len(expected)} runtime payloads in both distributions; version {version}.")


if __name__ == "__main__":
    main()
