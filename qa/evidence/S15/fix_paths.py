"""Apply the reviewed early-locality guard consistently across input/output boundaries."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for filename, value in (
    ("config.py", "path"),
    ("_tables.py", "source"),
    ("cli.py", "path"),
    ("comparison.py", "source"),
    ("provenance.py", "source"),
    ("demo.py", "output_dir"),
    ("_report_writes.py", "output_dir"),
):
    path = ROOT / "src/neurocvguard" / filename
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "from neurocvguard.errors import",
        "from neurocvguard._paths import is_remote_path\nfrom neurocvguard.errors import",
        1,
    )
    old = f'"://" in str({value})'
    # Remove the old prefix clause while retaining the remaining format checks.
    import re

    pattern = re.escape(old) + r"\s+or str\(" + value + r'\)\.startswith\(\("\\\\\\\\", "//"\)\)'
    text, count = re.subn(pattern, f"is_remote_path({value})", text)
    if count != 1:
        raise ValueError((filename, count))
    path.write_text(text, encoding="utf-8")
path = ROOT / "src/neurocvguard/io.py"
text = path.read_text(encoding="utf-8")
text = text.replace(
    "from neurocvguard.errors import",
    "from neurocvguard._paths import is_remote_path\nfrom neurocvguard.errors import",
    1,
)
text = text.replace(
    '"://" in str(path)\n        or str(path).startswith("\\\\\\\\")', "is_remote_path(path)"
)
text = text.replace(
    '"://" in str(output_dir) or str(destination).startswith("\\\\\\\\")',
    "is_remote_path(output_dir)",
)
text = text.replace(
    "    if any(\n        (Path(output_dir) / name).exists()",
    "    if is_remote_path(output_dir):\n"
    '        raise InputValidationError("Choose a local directory for split artifacts.")\n'
    "    if any(\n        (Path(output_dir) / name).exists()",
)
path.write_text(text, encoding="utf-8")
