"""Screen list in accessibility coordinates.

NSScreen reports a bottom-left origin. The accessibility API uses a top-left
origin on the primary display. Every frame leaving this module is converted.
"""

from __future__ import annotations

from typing import NamedTuple

from AppKit import NSScreen

from .geometry import Frame, overlap_area


class Screen(NamedTuple):
    index: int
    frame: Frame
    visible: Frame  # menu bar and Dock removed


def _global_height() -> float:
    screens = NSScreen.screens()
    return screens[0].frame().size.height if screens else 0.0


def _to_ax(ns_rect, global_height: float) -> Frame:
    o, s = ns_rect.origin, ns_rect.size
    return Frame(o.x, global_height - (o.y + s.height), s.width, s.height)


def screens() -> list[Screen]:
    """Screens ordered left to right, then top to bottom."""
    height = _global_height()
    found = [
        Screen(0, _to_ax(s.frame(), height), _to_ax(s.visibleFrame(), height))
        for s in NSScreen.screens()
    ]
    found.sort(key=lambda s: (s.frame.x, s.frame.y))
    return [s._replace(index=i) for i, s in enumerate(found)]


def screen_of(frame: Frame, known: list[Screen] | None = None) -> Screen:
    """Screen holding the largest part of `frame`. Falls back to the first screen."""
    known = known or screens()
    return max(known, key=lambda s: (overlap_area(frame, s.frame), -s.index))


def neighbour(current: Screen, direction: str, known: list[Screen] | None = None) -> Screen:
    """Next screen in the sorted list. Wraps around."""
    known = known or screens()
    if len(known) < 2:
        return current
    step = 1 if direction in ("right", "next", "down") else -1
    return known[(current.index + step) % len(known)]
