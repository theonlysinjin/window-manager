"""Tiling actions.

Each layout is a pure `(Frame, Screen) -> Frame` function. The registered action
is a thin wrapper that reads the focused window, applies the layout and writes back.
"""

from __future__ import annotations

import logging

from ..geometry import Frame, clamped, fraction, relative, scaled_into
from ..screens import Screen, neighbour, screen_of, screens
from ..window import focused_window, frame_of, set_frame
from .registry import action

log = logging.getLogger(__name__)

SIDES = {
    "left": (0.0, 0.0, 0.5, 1.0),
    "right": (0.5, 0.0, 0.5, 1.0),
    "top": (0.0, 0.0, 1.0, 0.5),
    "bottom": (0.0, 0.5, 1.0, 0.5),
}


def layout_maximise(frame: Frame, screen: Screen) -> Frame:
    return screen.visible


def layout_half(frame: Frame, screen: Screen, side: str) -> Frame:
    if side not in SIDES:
        raise ValueError(f"side must be one of {sorted(SIDES)}, got {side!r}")
    return fraction(screen.visible, *SIDES[side])


def layout_move_display(frame: Frame, source: Screen, target: Screen, keep: str) -> Frame:
    """Move a frame between screens.

    `keep: relative` holds the same proportions of the visible area.
    `keep: size` holds the pixel size and clamps it into the target.
    """
    if keep == "size":
        offset = Frame(
            target.visible.x + (frame.x - source.visible.x),
            target.visible.y + (frame.y - source.visible.y),
            frame.w,
            frame.h,
        )
        return clamped(offset, target.visible)
    if keep == "maximise":
        return target.visible
    return scaled_into(relative(frame, source.visible), target.visible)


def _apply(layout) -> bool:
    """Read the focused window, run a layout, write the result."""
    window = focused_window()
    if window is None:
        log.warning("no focused window")
        return False
    frame = frame_of(window)
    if frame is None:
        log.warning("focused window has no frame")
        return False
    screen = screen_of(frame)
    return set_frame(window, layout(frame, screen))


@action("maximise")
def maximise() -> bool:
    return _apply(layout_maximise)


@action("half")
def half(side: str = "left") -> bool:
    return _apply(lambda frame, screen: layout_half(frame, screen, side))


@action("move_display")
def move_display(direction: str = "right", keep: str = "relative") -> bool:
    known = screens()

    def layout(frame: Frame, source: Screen) -> Frame:
        return layout_move_display(frame, source, neighbour(source, direction, known), keep)

    return _apply(layout)
