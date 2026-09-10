"""Frame arithmetic. Pure functions, no framework calls.

All frames use the accessibility coordinate space: origin at the top left of the
primary display, y grows downward.
"""

from __future__ import annotations

from typing import NamedTuple


class Frame(NamedTuple):
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


def rounded(f: Frame) -> Frame:
    return Frame(round(f.x), round(f.y), round(f.w), round(f.h))


def fraction(f: Frame, left: float, top: float, width: float, height: float) -> Frame:
    """Sub-frame of `f`, given as fractions of its width and height."""
    return rounded(
        Frame(f.x + f.w * left, f.y + f.h * top, f.w * width, f.h * height)
    )


def contains_point(f: Frame, x: float, y: float) -> bool:
    return f.x <= x < f.x + f.w and f.y <= y < f.y + f.h


def overlap_area(a: Frame, b: Frame) -> float:
    w = min(a.x + a.w, b.x + b.w) - max(a.x, b.x)
    h = min(a.y + a.h, b.y + b.h) - max(a.y, b.y)
    return max(0.0, w) * max(0.0, h)


def relative(inner: Frame, outer: Frame) -> Frame:
    """Position and size of `inner` as fractions of `outer`."""
    return Frame(
        (inner.x - outer.x) / outer.w,
        (inner.y - outer.y) / outer.h,
        inner.w / outer.w,
        inner.h / outer.h,
    )


def scaled_into(rel: Frame, outer: Frame) -> Frame:
    """Inverse of `relative`. Places a fractional frame inside `outer`."""
    return rounded(
        Frame(
            outer.x + rel.x * outer.w,
            outer.y + rel.y * outer.h,
            rel.w * outer.w,
            rel.h * outer.h,
        )
    )


def clamped(inner: Frame, outer: Frame) -> Frame:
    """Shrink and shift `inner` so it fits inside `outer`."""
    w = min(inner.w, outer.w)
    h = min(inner.h, outer.h)
    x = min(max(inner.x, outer.x), outer.x + outer.w - w)
    y = min(max(inner.y, outer.y), outer.y + outer.h - h)
    return rounded(Frame(x, y, w, h))
