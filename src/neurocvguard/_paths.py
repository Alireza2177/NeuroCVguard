"""Reject remote spellings before filesystem access, including Windows normalization."""

from pathlib import Path, PureWindowsPath


def is_remote_path(value: str | Path) -> bool:
    text = str(value)
    return (
        "://" in text
        or text.startswith(("\\\\", "//"))
        or PureWindowsPath(text).drive.startswith("\\\\")
    )
