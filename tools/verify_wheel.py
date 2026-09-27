"""Run from an isolated wheel environment; refuse networking and source-tree reads."""

import argparse
import hashlib
import importlib.metadata as metadata
import importlib.resources as resources
import json
import os
import platform
import sys
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forbid-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    args = parser.parse_args()
    forbidden = os.path.normcase(str(args.forbid_root.resolve()))

    def guard(event, values):
        # gethostname reads the local machine name; it does not send a packet.
        if event.startswith("socket.") and event != "socket.gethostname":
            raise AssertionError("Network access during wheel verification")
        if event in {"open", "os.listdir", "os.scandir"}:
            path = values[0]
            if isinstance(path, (str, bytes, os.PathLike)):
                resolved = os.path.normcase(os.path.abspath(os.fsdecode(path)))
                if resolved == forbidden or resolved.startswith(forbidden + os.sep):
                    raise AssertionError("Source-tree access during wheel verification")

    sys.addaudithook(guard)
    import neurocvguard
    from neurocvguard.cli import main as cli_main
    from neurocvguard.schema import load_schema

    installed = Path(neurocvguard.__file__).resolve()
    assert installed.is_relative_to(Path(sys.prefix).resolve())
    assert not any(Path(p).resolve().is_relative_to(args.forbid_root.resolve()) for p in sys.path)
    distribution = metadata.distribution("neurocvguard")
    direct = json.loads(distribution.read_text("direct_url.json"))
    assert "archive_info" in direct and not direct.get("dir_info", {}).get("editable", False)
    assert neurocvguard.__version__ == distribution.version == "0.1.0"
    package = resources.files("neurocvguard")
    with zipfile.ZipFile(args.wheel) as archive:
        payloads = [name for name in archive.namelist() if name.startswith("neurocvguard/")]
        for name in payloads:
            assert package.joinpath(
                name.removeprefix("neurocvguard/")
            ).read_bytes() == archive.read(name)
    schemas = sorted(p.name for p in package.joinpath("schemas").iterdir())
    assert len(schemas) == 6
    for name in schemas:
        load_schema(name.removesuffix(".schema.json"))
    for name in ("templates/report.html", "templates/report.css", "py.typed"):
        assert package.joinpath(name).is_file()
    scripts = sorted(p.name for p in package.joinpath("examples").iterdir() if p.suffix == ".py")
    assert len(scripts) == 5
    assert cli_main(["--debug", "demo", "--out", str(args.out)]) == 0
    assert (args.out / "report.html").is_file()
    report = json.loads((args.out / "report.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.out / "demo.private.json").read_text(encoding="utf-8"))
    assert manifest["execution_status"] == "completed"
    assert report["execution_status"] == "partial"
    assert any(
        c["rule_id"] == "NCG-PROV-001" and c["status"] == "not_assessable" for c in report["checks"]
    )
    record = {
        "version": distribution.version,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "installed_under_environment": True,
        "editable": False,
        "source_tree_reads": "blocked by audit hook",
        "network": "blocked by audit hook",
        "schemas": schemas,
        "examples": scripts,
        "demo": "completed",
        "audit_report": "partial; upstream preprocessing remains unassessable",
        "wheel_sha256": hashlib.sha256(args.wheel.read_bytes()).hexdigest(),
        "installed_payloads_match_wheel": len(payloads),
        "versions": {
            name: metadata.version(name)
            for name in ("numpy", "pandas", "scipy", "scikit-learn", "Jinja2", "jsonschema")
        },
    }
    with (args.out / "wheel-verification.json").open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
