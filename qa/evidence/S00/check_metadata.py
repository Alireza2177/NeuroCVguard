"""Check S00 source and installed metadata without asserting release approval."""

import importlib.metadata
import json
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parents[3]
configuration = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
project = configuration["project"]
assert project["name"] == "neurocvguard"
assert project["requires-python"] == ">=3.11"
assert set(project["dependencies"]) == {
    "numpy",
    "pandas",
    "scipy",
    "scikit-learn",
    "Jinja2",
    "jsonschema",
}
assert not {"authors", "maintainers", "urls", "license", "classifiers"} & project.keys()
release = configuration["tool"]["neurocvguard"]["release"]
assert release["proposed-license"] == "BSD-3-Clause"
assert release["license-status"] == "PENDING_MAINTAINER_CONFIRMATION"
assert release["public-release-authorized"] is False
metadata = importlib.metadata.metadata("neurocvguard")
assert metadata["Name"] == "neurocvguard"
assert metadata["Version"] == "0.1.0"
assert metadata.get_payload().strip() == (root / "README.md").read_text().strip()
for field in (
    "Author",
    "Author-email",
    "Maintainer",
    "Home-page",
    "Project-URL",
    "License-Expression",
):
    assert metadata.get(field) is None, field
assert metadata["Summary"] == "Research-only NeuroCVguard development bootstrap"
print(json.dumps({"source_and_installed_metadata": "PASS", "publication_metadata": "PENDING"}))
