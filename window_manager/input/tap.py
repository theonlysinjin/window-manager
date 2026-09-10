"""Quartz event tap. Normalises mouse and key events into Trigger objects."""

from __future__ import annotations

import logging
from typing import Callable

from Quartz import (
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopGetCurrent,
    CGEventGetFlags,
    CGEventGetIntegerValueField,
    CGEventMaskBit,
    CGEventTapCreate,
    CGEventTapEnable,
    kCFAllocatorDefault,
    kCFRunLoopCommonModes,
    kCGEventKeyDown,
    kCGEventOtherMouseDown,
    kCGEventOtherMouseUp,
    kCGEventSourceUserData,
    kCGEventTapDisabledByTimeout,
    kCGEventTapDisabledByUserInput,
    kCGEventTapOptionDefault,
    kCGHeadInsertEventTap,
    kCGHIDEventTap,
    kCGKeyboardEventKeycode,
    kCGMouseEventButtonNumber,
)

from ..actions.keyboard import SYNTHETIC_MARKER
from ..bindings import KEY, MOUSE, Trigger
from .keys import MODIFIER_MASK

log = logging.getLogger(__name__)

EVENT_MASK = (
    CGEventMaskBit(kCGEventKeyDown)
    | CGEventMaskBit(kCGEventOtherMouseDown)
    | CGEventMaskBit(kCGEventOtherMouseUp)
)


class TapError(Exception):
    pass


def _trigger(event_type: int, event) -> Trigger | None:
    # The mask drops caps lock and numeric pad bits.
    mods = int(CGEventGetFlags(event)) & MODIFIER_MASK
    if event_type == kCGEventKeyDown:
        return Trigger(KEY, int(CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)), mods)
    if event_type == kCGEventOtherMouseDown:
        return Trigger(MOUSE, int(CGEventGetIntegerValueField(event, kCGMouseEventButtonNumber)), mods)
    return None


def install(dispatch: Callable[[Trigger], bool], debug: bool = False):
    """Create the tap and attach it to the current run loop.

    `dispatch` receives a Trigger and returns True to swallow the event.
    Returns the tap, which the caller keeps alive.
    """
    swallowed_buttons: set[int] = set()

    def callback(proxy, event_type, event, refcon):
        if event_type in (kCGEventTapDisabledByTimeout, kCGEventTapDisabledByUserInput):
            log.warning("event tap disabled (%s), re-enabling", event_type)
            CGEventTapEnable(tap, True)
            return event

        # Ignore events this app posted itself.
        if CGEventGetIntegerValueField(event, kCGEventSourceUserData) == SYNTHETIC_MARKER:
            return event

        if event_type == kCGEventOtherMouseUp:
            button = int(CGEventGetIntegerValueField(event, kCGMouseEventButtonNumber))
            # The press was swallowed, so hide the matching release too.
            if button in swallowed_buttons:
                swallowed_buttons.discard(button)
                return None
            return event

        trigger = _trigger(event_type, event)
        if trigger is None:
            return event
        if debug:
            log.info("event %s", trigger)
        try:
            swallow = bool(dispatch(trigger))
        except Exception:
            log.exception("dispatch failed for %s", trigger)
            return event
        if swallow and trigger.kind == MOUSE:
            swallowed_buttons.add(trigger.code)
        return None if swallow else event

    tap = CGEventTapCreate(
        kCGHIDEventTap,
        kCGHeadInsertEventTap,
        kCGEventTapOptionDefault,
        EVENT_MASK,
        callback,
        None,
    )
    if tap is None:
        raise TapError("could not create the event tap — grant Input Monitoring")

    source = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
    CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
    CGEventTapEnable(tap, True)
    return tap
