"""Key names, virtual keycodes and modifier flags."""

from __future__ import annotations

from Quartz import (
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
)

MODIFIERS: dict[str, int] = {
    "shift": kCGEventFlagMaskShift,
    "ctrl": kCGEventFlagMaskControl,
    "control": kCGEventFlagMaskControl,
    "alt": kCGEventFlagMaskAlternate,
    "opt": kCGEventFlagMaskAlternate,
    "option": kCGEventFlagMaskAlternate,
    "cmd": kCGEventFlagMaskCommand,
    "command": kCGEventFlagMaskCommand,
}

# Bits the matcher looks at. Everything else is noise: caps lock, the numeric pad,
# and the fn bit that macOS stamps on every function key press.
MODIFIER_MASK = (
    kCGEventFlagMaskShift
    | kCGEventFlagMaskControl
    | kCGEventFlagMaskAlternate
    | kCGEventFlagMaskCommand
)

CANONICAL_MODIFIER = {
    kCGEventFlagMaskShift: "shift",
    kCGEventFlagMaskControl: "ctrl",
    kCGEventFlagMaskAlternate: "alt",
    kCGEventFlagMaskCommand: "cmd",
}

KEYCODES: dict[str, int] = {
    "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7, "c": 8,
    "v": 9, "b": 11, "q": 12, "w": 13, "e": 14, "r": 15, "y": 16, "t": 17,
    "1": 18, "2": 19, "3": 20, "4": 21, "6": 22, "5": 23, "=": 24, "9": 25,
    "7": 26, "-": 27, "8": 28, "0": 29, "]": 30, "o": 31, "u": 32, "[": 33,
    "i": 34, "p": 35, "l": 37, "j": 38, "'": 39, "k": 40, ";": 41, "\\": 42,
    ",": 43, "/": 44, "n": 45, "m": 46, ".": 47, "`": 50,
    "return": 36, "tab": 48, "space": 49, "delete": 51, "escape": 53,
    "capslock": 57, "home": 115, "pageup": 116, "forwarddelete": 117,
    "end": 119, "pagedown": 121,
    "left": 123, "right": 124, "down": 125, "up": 126,
    "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97, "f7": 98,
    "f8": 100, "f9": 101, "f10": 109, "f11": 103, "f12": 111,
    "f13": 105, "f14": 107, "f15": 113, "f16": 106, "f17": 64, "f18": 79,
    "f19": 80, "f20": 90,
}

NAMES: dict[int, str] = {code: name for name, code in reversed(KEYCODES.items())}


def keycode(name: str) -> int:
    key = name.strip().lower()
    if key not in KEYCODES:
        raise KeyError(f"unknown key {name!r}")
    return KEYCODES[key]


def key_name(code: int) -> str:
    return NAMES.get(code, f"keycode:{code}")


def modifier_mask(names) -> int:
    mask = 0
    for name in names or ():
        key = str(name).strip().lower()
        if key not in MODIFIERS:
            raise KeyError(f"unknown modifier {name!r}")
        mask |= MODIFIERS[key]
    return mask


def modifier_names(mask: int) -> list[str]:
    return [name for bit, name in CANONICAL_MODIFIER.items() if mask & bit]
