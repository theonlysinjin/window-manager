"""Permission checks for Accessibility and Input Monitoring."""

from __future__ import annotations

from ApplicationServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt
from Quartz import CGPreflightListenEventAccess, CGRequestListenEventAccess

SETTINGS_HINT = "System Settings → Privacy & Security"


def accessibility(prompt: bool = False) -> bool:
    """True when the process may drive other apps' windows."""
    return bool(AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: prompt}))


def input_monitoring(prompt: bool = False) -> bool:
    """True when the process may read the event tap."""
    if CGPreflightListenEventAccess():
        return True
    if prompt:
        CGRequestListenEventAccess()
    return bool(CGPreflightListenEventAccess())


def report(prompt: bool = False) -> list[str]:
    """Names of the grants that are still missing."""
    missing = []
    if not accessibility(prompt):
        missing.append("Accessibility")
    if not input_monitoring(prompt):
        missing.append("Input Monitoring")
    return missing
