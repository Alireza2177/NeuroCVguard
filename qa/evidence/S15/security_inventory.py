"""Retain installed dependency/license evidence and an auditable source/workflow inventory."""

import ast
import hashlib
import json
from importlib.metadata import distribution
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    dependencies = {}
    for name in (
        "numpy",
        "pandas",
        "scipy",
        "scikit-learn",
        "Jinja2",
        "jsonschema",
        "sphinx",
        "myst-parser",
        "pytest",
        "hypothesis",
    ):
        dist = distribution(name)
        licenses = []
        for path in dist.files or ():
            if "dist-info" in str(path) and any(
                word in path.name.lower() for word in ("license", "copying", "notice")
            ):
                full = Path(dist.locate_file(path))
                data = full.read_bytes()
                licenses.append(
                    {
                        "file": str(path),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "text": data.decode("utf-8", errors="replace"),
                    }
                )
        dependencies[name] = {
            "version": dist.version,
            "license_expression": dist.metadata.get("License-Expression"),
            "license_metadata": dist.metadata.get("License"),
            "license_files": licenses,
        }
    imports, risky_calls = [], []
    prohibited = {
        "eval",
        "exec",
        "__import__",
        "pickle.load",
        "pickle.loads",
        "joblib.load",
        "yaml.load",
        "os.system",
        "subprocess.run",
        "subprocess.Popen",
        "requests.get",
        "urlopen",
        "urllib.request.urlopen",
        "socket.connect",
    }
    for source in sorted((ROOT / "src/neurocvguard").rglob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(
                    {
                        "file": source.relative_to(ROOT).as_posix(),
                        "line": node.lineno,
                        "module": alias.name,
                    }
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                imports.append(
                    {
                        "file": source.relative_to(ROOT).as_posix(),
                        "line": node.lineno,
                        "module": node.module,
                    }
                )
            elif isinstance(node, ast.Call):
                name = ast.unparse(node.func)
                if name in prohibited:
                    risky_calls.append(
                        {
                            "file": source.relative_to(ROOT).as_posix(),
                            "line": node.lineno,
                            "call": name,
                        }
                    )
    record = {
        "dependencies": dependencies,
        "runtime_imports": imports,
        "prohibited_call_hits": risky_calls,
        "workflows": [
            p.relative_to(ROOT).as_posix() for p in (ROOT / ".github/workflows").glob("*")
        ],
        "scope": "Installed metadata/license texts and source AST review inputs only; "
        "not a vulnerability database scan or a complete proof of absence of networking.",
    }
    destination = Path(__file__).with_name("security-inventory.json")
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    assert not risky_calls
    print(
        f"Reviewed {len(imports)} runtime import statements; no listed unsafe calls; "
        f"{len(record['workflows'])} executable workflows; {len(dependencies)} dependency records."
    )


if __name__ == "__main__":
    main()
