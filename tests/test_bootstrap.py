"""S00 installed-package acceptance checks using fresh Python processes."""

import json
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest


def test_import_has_no_side_effects(tmp_path: Path) -> None:
    """AT-S00-01: block non-code reads, writes, sockets, and worker creation."""
    probe = r"""
import os
import pathlib
import sys
import _thread

def reject_worker(*args, **kwargs):
    raise AssertionError("worker creation during import")

_thread.start_new_thread = reject_worker

def guard(event, args):
    if event == "open":
        path, mode, flags = args
        if not isinstance(path, (str, bytes)):
            raise AssertionError("unexpected file descriptor access")
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            raise AssertionError("filesystem write during import")
        if pathlib.Path(path).suffix not in {".py", ".pyc", ".pyd", ".dll"}:
            raise AssertionError("non-code file access during import")
    if event.startswith(("socket.", "subprocess.", "os.spawn", "os.exec")):
        raise AssertionError("network/process activity during import")
    if event in {
        "os.mkdir", "os.remove", "os.rename", "os.rmdir", "os.system",
        "os.fork", "os.link", "os.symlink", "os.truncate", "os.chmod",
        "os.utime", "_thread.start_new_thread",
    }:
        raise AssertionError("filesystem/process mutation during import")

sys.addaudithook(guard)
import neurocvguard
assert neurocvguard.__version__ == "0.1.0"
"""
    # -B prevents interpreter bytecode caching; the package itself must stay inert.
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == result.stderr == ""
    assert list(tmp_path.iterdir()) == []


def test_installed_version_matches_metadata(tmp_path: Path) -> None:
    """AT-S00-02: resolve the installed distribution outside the source tree."""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "import importlib.metadata as m, neurocvguard; "
            "assert m.version('neurocvguard') == neurocvguard.__version__ == '0.1.0'",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("entry", ["module", "console"])
@pytest.mark.parametrize(
    ("arguments", "code", "expected"),
    [
        (["--version"], 0, "neurocvguard 0.1.0"),
        (["--help"], 0, "Only help and version are available"),
        ([], 0, "Only help and version are available"),
        (["audit"], 2, "unrecognized arguments: audit"),
    ],
)
def test_entry_points(
    tmp_path: Path, entry: str, arguments: list[str], code: int, expected: str
) -> None:
    """AT-S00-02/04: expose working version/help, reject future commands."""
    executable = Path(sysconfig.get_path("scripts")) / (
        "neurocvguard.exe" if sys.platform == "win32" else "neurocvguard"
    )
    command = (
        [sys.executable, "-I", "-m", "neurocvguard"] if entry == "module" else [str(executable)]
    )
    result = subprocess.run([*command, *arguments], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == code, result.stderr
    assert expected in (result.stdout if code == 0 else result.stderr)
    if arguments == ["--version"]:
        assert result.stdout == expected + "\n"
        assert result.stderr == ""


def test_editable_install_points_to_source() -> None:
    """AT-S00-02: the development test run must exercise an editable install."""
    import importlib.metadata

    import neurocvguard

    root = Path(__file__).resolve().parents[1]
    assert Path(neurocvguard.__file__).resolve() == root / "src/neurocvguard/__init__.py"
    record = importlib.metadata.distribution("neurocvguard").read_text("direct_url.json")
    assert record is not None
    assert json.loads(record)["dir_info"]["editable"] is True
