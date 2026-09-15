"""Status bar item. A view-only shortcut list and a quit command."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import AppKit

from .bindings import Binding

TITLE = "Window Manager"
GLYPH = Path(__file__).parent / "resources" / "statusbar.pdf"
GLYPH_POINTS = 18.0
SYMBOL = "macwindow"
FALLBACK = "▣"


class _Handler(AppKit.NSObject):
    """pyobjc routes menu clicks to an NSObject, so the quit target needs one."""

    def quit_(self, sender) -> None:
        self.on_quit()


def _label(binding: Binding) -> str:
    args = " ".join(f"{k}={v}" for k, v in binding.args.items())
    return f"{binding.trigger}    {binding.action} {args}".rstrip()


def _disabled(menu, title: str) -> None:
    item = menu.addItemWithTitle_action_keyEquivalent_(title, None, "")
    item.setEnabled_(False)


def _shortcuts(bindings: list[Binding]):
    menu = AppKit.NSMenu.alloc().init()
    menu.setAutoenablesItems_(False)
    if not bindings:
        _disabled(menu, "no bindings")
    for binding in bindings:
        _disabled(menu, _label(binding))
    return menu


def _menu(bindings: list[Binding], handler):
    menu = AppKit.NSMenu.alloc().init()
    menu.setAutoenablesItems_(False)
    _disabled(menu, f"{TITLE} — {len(bindings)} bindings")
    menu.addItem_(AppKit.NSMenuItem.separatorItem())
    parent = menu.addItemWithTitle_action_keyEquivalent_("Shortcuts", None, "")
    menu.setSubmenu_forItem_(_shortcuts(bindings), parent)
    menu.addItem_(AppKit.NSMenuItem.separatorItem())
    quit_item = menu.addItemWithTitle_action_keyEquivalent_("Quit", "quit:", "q")
    quit_item.setTarget_(handler)
    return menu


def _image():
    """The bundled glyph, an SF Symbol as a fallback, or None."""
    if GLYPH.exists():
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(str(GLYPH))
        if image is not None:
            image.setSize_(AppKit.NSMakeSize(GLYPH_POINTS, GLYPH_POINTS))
            return image
    if hasattr(AppKit.NSImage, "imageWithSystemSymbolName_accessibilityDescription_"):
        return AppKit.NSImage.imageWithSystemSymbolName_accessibilityDescription_(SYMBOL, TITLE)
    return None


def _icon(button) -> None:
    image = _image()
    if image is None:
        button.setTitle_(FALLBACK)
        return
    image.setTemplate_(True)
    image.setAccessibilityDescription_(TITLE)
    button.setImage_(image)


def install(bindings: list[Binding], on_quit: Callable[[], None]):
    """Add the status item. Returns a refresh(bindings) function.

    Keep the returned function alive — it holds the only reference to the
    status item, and the icon vanishes when that is released.
    """
    item = AppKit.NSStatusBar.systemStatusBar().statusItemWithLength_(
        AppKit.NSVariableStatusItemLength
    )
    _icon(item.button())
    handler = _Handler.alloc().init()
    handler.on_quit = on_quit
    item.setMenu_(_menu(bindings, handler))

    def refresh(updated: list[Binding]) -> None:
        item.setMenu_(_menu(updated, handler))

    refresh.item = item
    refresh.handler = handler
    return refresh
