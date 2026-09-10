"""Synthetic key presses. Not window management — it proves the registry is open."""

from __future__ import annotations

import logging

from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    CGEventSetIntegerValueField,
    kCGEventSourceUserData,
    kCGHIDEventTap,
)

from ..input.keys import keycode, modifier_mask
from .registry import action

log = logging.getLogger(__name__)

# Stamped on every event this app posts, so the tap can ignore its own output.
SYNTHETIC_MARKER = 0x574D4752  # "WMGR"


def _post(code: int, flags: int, down: bool) -> None:
    event = CGEventCreateKeyboardEvent(None, code, down)
    CGEventSetFlags(event, flags)
    CGEventSetIntegerValueField(event, kCGEventSourceUserData, SYNTHETIC_MARKER)
    CGEventPost(kCGHIDEventTap, event)


@action("send_key")
def send_key(key: str, mods=()) -> bool:
    code = keycode(key)
    flags = modifier_mask(mods)
    _post(code, flags, True)
    _post(code, flags, False)
    return True
