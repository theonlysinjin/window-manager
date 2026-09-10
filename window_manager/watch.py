"""Reload the config when its file changes. Polls the modification time."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from Foundation import NSTimer

log = logging.getLogger(__name__)

INTERVAL_SECONDS = 1.0


def _stamp(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def watch(path: Path, on_change: Callable[[], None], interval: float = INTERVAL_SECONDS):
    """Call `on_change` when `path` changes. Returns the timer, which the caller keeps."""
    state = {"stamp": _stamp(path)}

    def tick(_timer):
        stamp = _stamp(path)
        if stamp != state["stamp"]:
            state["stamp"] = stamp
            log.info("config changed, reloading")
            on_change()

    return NSTimer.scheduledTimerWithTimeInterval_repeats_block_(interval, True, tick)
