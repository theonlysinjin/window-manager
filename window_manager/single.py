"""Single-instance lock. A second copy finds the lock held and exits."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path
from typing import IO

LOCK_PATH = Path("~/Library/Application Support/window-manager/run.lock").expanduser()


def acquire(path: Path | None = None) -> IO[str] | None:
    """Take the lock, or return None when another process holds it.

    The caller keeps the handle for the life of the process. macOS releases
    the flock when the file closes, so a crash frees it too.
    """
    path = Path(path or LOCK_PATH).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(path, "a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def holder_pid(path: Path | None = None) -> int | None:
    """Pid of the running instance, or None when the lock is free."""
    path = Path(path or LOCK_PATH).expanduser()
    if not path.exists():
        return None
    probe = acquire(path)
    if probe is not None:
        probe.close()
        return None
    try:
        return int(path.read_text().strip())
    except ValueError:
        return -1
