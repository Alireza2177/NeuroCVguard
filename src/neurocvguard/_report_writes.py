"""Local named-artifact staging with overwrite refusal and ordinary failure rollback."""

import os
import shutil
import tempfile
from pathlib import Path

from neurocvguard._paths import is_remote_path
from neurocvguard.errors import InputValidationError


def write_bundle(
    output_dir: str | Path, contents: dict[str, str], *, overwrite: bool
) -> dict[str, Path]:
    if type(overwrite) is not bool:
        raise InputValidationError("overwrite must be an explicit boolean.")
    destination = Path(output_dir)
    if is_remote_path(output_dir):
        raise InputValidationError("Choose a local report directory.")
    if destination.is_symlink() or any(Path(name).name != name for name in contents):
        raise InputValidationError("Report destinations must use local regular files.")
    paths = {name: destination / name for name in contents}
    lock = destination / ".neurocvguard-report.lock"
    acquired = False
    staging: Path | None = None
    keep_recovery = False
    reserved: list[Path] = []
    replaced: list[str] = []
    backups: dict[str, Path] = {}
    try:
        destination.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        acquired = True
        if any(
            p.is_symlink() or (p.exists() and (not overwrite or not p.is_file()))
            for p in paths.values()
        ):
            raise InputValidationError(
                "Report output exists or is not a regular file. Choose a new directory "
                "or explicitly set overwrite=True."
            )
        staging = Path(tempfile.mkdtemp(prefix=".neurocvguard-report-", dir=destination))
        for index, (name, text) in enumerate(contents.items()):
            staged = staging / name
            with staged.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            staged.chmod(0o600)
            if paths[name].exists():
                backup = staging / f"backup-{index}"
                shutil.copy2(paths[name], backup)
                backups[name] = backup
        try:
            if not overwrite:
                for path in paths.values():
                    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                    os.close(descriptor)
                    reserved.append(path)
            for name, path in paths.items():
                os.replace(staging / name, path)
                replaced.append(name)
        except BaseException:
            # Roll back only names owned by this invocation; retain backups if recovery fails.
            for name in reversed(replaced):
                try:
                    if name in backups:
                        os.replace(backups[name], paths[name])
                    else:
                        paths[name].unlink(missing_ok=True)
                except OSError:
                    keep_recovery = True
            for path in reserved:
                if path.name not in replaced:
                    try:
                        path.unlink(missing_ok=True)
                    except OSError:
                        keep_recovery = True
            if keep_recovery:
                raise InputValidationError(
                    "Report write and rollback failed; recovery copies remain in the output "
                    "directory under .neurocvguard-report-*."
                ) from None
            raise
    except OSError:
        raise InputValidationError(
            "Could not write reports. Check permissions, output conflicts or an active "
            "report lock; prior files were not intentionally discarded."
        ) from None
    finally:
        if staging is not None and not keep_recovery:
            # Only delete this invocation's resolved staging directory inside the destination.
            if staging.resolve().parent == destination.resolve() and staging.name.startswith(
                ".neurocvguard-report-"
            ):
                shutil.rmtree(staging)
        if acquired:
            lock.unlink(missing_ok=True)
    return paths
