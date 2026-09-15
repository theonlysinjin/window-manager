"""Draws the app icon and the status bar glyph with Quartz.

    python packaging/icon.py

Writes packaging/WindowManager.icns and window_manager/resources/statusbar.pdf.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import Quartz
from Foundation import NSURL
from Quartz import CGPointMake, CGRectMake

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ICONSET = HERE / "WindowManager.iconset"
ICNS = HERE / "WindowManager.icns"
GLYPH = ROOT / "window_manager" / "resources" / "statusbar.pdf"

ICNS_SIZES = (16, 32, 128, 256, 512)
GLYPH_SIZE = 18.0

TOP = (0.33, 0.58, 1.00)
BOTTOM = (0.16, 0.26, 0.80)

# Unit-square layout, shared by both drawings. Origin bottom-left.
PLATE = (0.085, 0.085, 0.830, 0.830)
PANES = (
    (0.215, 0.215, 0.245, 0.570),  # left, full height
    (0.495, 0.505, 0.290, 0.280),  # right top
    (0.495, 0.215, 0.290, 0.280),  # right bottom
)
PLATE_RADIUS = 0.225
PANE_RADIUS = 0.048

# The glyph is stroked, not filled. Filled panes turn into a black block at 18pt.
GLYPH_FRAME = (0.085, 0.085, 0.830, 0.830)
GLYPH_RADIUS = 0.16
GLYPH_SPLIT = 0.40  # vertical divider, as a fraction of the frame width
GLYPH_LINE = 0.075


def _scaled(rect, size: float):
    x, y, w, h = rect
    return CGRectMake(x * size, y * size, w * size, h * size)


def _rounded(rect, size: float, radius: float):
    corner = radius * size
    return Quartz.CGPathCreateWithRoundedRect(_scaled(rect, size), corner, corner, None)


def _fill(ctx, path, colour, alpha: float = 1.0) -> None:
    Quartz.CGContextSetRGBFillColor(ctx, *colour, alpha)
    Quartz.CGContextAddPath(ctx, path)
    Quartz.CGContextFillPath(ctx)


def _gradient_plate(ctx, size: float) -> None:
    space = Quartz.CGColorSpaceCreateDeviceRGB()
    gradient = Quartz.CGGradientCreateWithColorComponents(
        space, (*TOP, 1.0, *BOTTOM, 1.0), (0.0, 1.0), 2
    )
    Quartz.CGContextSaveGState(ctx)
    Quartz.CGContextAddPath(ctx, _rounded(PLATE, size, PLATE_RADIUS))
    Quartz.CGContextClip(ctx)
    Quartz.CGContextDrawLinearGradient(
        ctx, gradient, CGPointMake(0, size), CGPointMake(0, 0), 0
    )
    Quartz.CGContextRestoreGState(ctx)


def draw_icon(ctx, size: float) -> None:
    """App icon: a gradient plate carrying three white panes."""
    _gradient_plate(ctx, size)
    for index, pane in enumerate(PANES):
        _fill(ctx, _rounded(pane, size, PANE_RADIUS), (1, 1, 1), 1.0 if index == 0 else 0.88)


def draw_glyph(ctx, size: float) -> None:
    """Status bar glyph: a stroked frame with two dividers, which macOS recolours."""
    x, y, w, h = (value * size for value in GLYPH_FRAME)
    split = x + w * GLYPH_SPLIT
    Quartz.CGContextSetRGBStrokeColor(ctx, 0, 0, 0, 1)
    Quartz.CGContextSetLineWidth(ctx, GLYPH_LINE * size)
    Quartz.CGContextAddPath(ctx, _rounded(GLYPH_FRAME, size, GLYPH_RADIUS))
    Quartz.CGContextStrokePath(ctx)
    for start, end in (
        ((split, y), (split, y + h)),
        ((split, y + h / 2), (x + w, y + h / 2)),
    ):
        Quartz.CGContextMoveToPoint(ctx, *start)
        Quartz.CGContextAddLineToPoint(ctx, *end)
    Quartz.CGContextStrokePath(ctx)


def write_png(path: Path, size: int) -> None:
    space = Quartz.CGColorSpaceCreateDeviceRGB()
    ctx = Quartz.CGBitmapContextCreate(
        None, size, size, 8, 0, space, Quartz.kCGImageAlphaPremultipliedLast
    )
    draw_icon(ctx, float(size))
    url = NSURL.fileURLWithPath_(str(path))
    dest = Quartz.CGImageDestinationCreateWithURL(url, "public.png", 1, None)
    Quartz.CGImageDestinationAddImage(dest, Quartz.CGBitmapContextCreateImage(ctx), None)
    Quartz.CGImageDestinationFinalize(dest)


def write_pdf(path: Path, size: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    box = CGRectMake(0, 0, size, size)
    url = NSURL.fileURLWithPath_(str(path))
    ctx = Quartz.CGPDFContextCreateWithURL(url, box, None)
    Quartz.CGContextBeginPage(ctx, box)
    draw_glyph(ctx, size)
    Quartz.CGContextEndPage(ctx)
    Quartz.CGPDFContextClose(ctx)


def build() -> None:
    shutil.rmtree(ICONSET, ignore_errors=True)
    ICONSET.mkdir(parents=True)
    for size in ICNS_SIZES:
        write_png(ICONSET / f"icon_{size}x{size}.png", size)
        write_png(ICONSET / f"icon_{size}x{size}@2x.png", size * 2)
    subprocess.run(["iconutil", "-c", "icns", str(ICONSET), "-o", str(ICNS)], check=True)
    shutil.rmtree(ICONSET, ignore_errors=True)
    write_pdf(GLYPH, GLYPH_SIZE)
    print(f"wrote {ICNS.relative_to(ROOT)} and {GLYPH.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
