"""Print actual interpreter and resolved dependency versions as JSON."""

import importlib
import importlib.metadata
import json
import platform
import sys

runtime = {
    "numpy": "numpy",
    "pandas": "pandas",
    "scipy": "scipy",
    "scikit-learn": "sklearn",
    "Jinja2": "jinja2",
    "jsonschema": "jsonschema",
}
for module in runtime.values():
    importlib.import_module(module)

print(
    json.dumps(
        {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "isolated_venv": sys.prefix != sys.base_prefix,
            "runtime_imports": list(runtime.values()),
            "packages": {
                distribution.metadata["Name"]: distribution.version
                for distribution in sorted(
                    importlib.metadata.distributions(),
                    key=lambda item: item.metadata["Name"].lower(),
                )
            },
        },
        indent=2,
    )
)
