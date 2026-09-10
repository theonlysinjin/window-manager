"""Read and write the frame of the focused window. The only AX side effects live here."""

from __future__ import annotations

import logging

from AppKit import NSWorkspace
from ApplicationServices import (
    AXUIElementCopyAttributeValue,
    AXUIElementCreateApplication,
    AXUIElementSetAttributeValue,
    AXValueCreate,
    AXValueGetValue,
    kAXValueTypeCGPoint,
    kAXValueTypeCGSize,
)
from Quartz import CGPoint, CGSize

from .geometry import Frame

log = logging.getLogger(__name__)

_FOCUSED_WINDOW = "AXFocusedWindow"
_POSITION = "AXPosition"
_SIZE = "AXSize"
_FULLSCREEN = "AXFullScreen"


def _attribute(element, name):
    err, value = AXUIElementCopyAttributeValue(element, name, None)
    return value if err == 0 else None


def focused_window():
    """AX element of the focused window of the frontmost app, or None."""
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    if app is None:
        return None
    return _attribute(AXUIElementCreateApplication(app.processIdentifier()), _FOCUSED_WINDOW)


def frame_of(window) -> Frame | None:
    pos, size = _attribute(window, _POSITION), _attribute(window, _SIZE)
    if pos is None or size is None:
        return None
    ok_p, point = AXValueGetValue(pos, kAXValueTypeCGPoint, None)
    ok_s, extent = AXValueGetValue(size, kAXValueTypeCGSize, None)
    if not (ok_p and ok_s):
        return None
    return Frame(point.x, point.y, extent.width, extent.height)


def set_frame(window, frame: Frame) -> bool:
    """Set position then size, then position again.

    Some apps clamp a move against the old size, so the second write settles it.
    """
    leave_fullscreen(window)
    point = AXValueCreate(kAXValueTypeCGPoint, CGPoint(frame.x, frame.y))
    extent = AXValueCreate(kAXValueTypeCGSize, CGSize(frame.w, frame.h))
    errors = (
        AXUIElementSetAttributeValue(window, _POSITION, point),
        AXUIElementSetAttributeValue(window, _SIZE, extent),
        AXUIElementSetAttributeValue(window, _POSITION, point),
    )
    if any(errors):
        log.warning("set_frame failed: %s", errors)
        return False
    return True


def leave_fullscreen(window) -> None:
    """Native fullscreen ignores position writes, so drop out of it first."""
    if _attribute(window, _FULLSCREEN):
        AXUIElementSetAttributeValue(window, _FULLSCREEN, False)
