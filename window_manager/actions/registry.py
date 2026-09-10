"""Decorator-based action registry. Adding an action needs no core change."""

from __future__ import annotations

import inspect
import logging
from typing import Any, Callable

log = logging.getLogger(__name__)

Action = Callable[..., Any]
_ACTIONS: dict[str, Action] = {}


def action(name: str) -> Callable[[Action], Action]:
    def register(fn: Action) -> Action:
        if name in _ACTIONS:
            raise ValueError(f"action {name!r} is already registered")
        _ACTIONS[name] = fn
        return fn

    return register


def get(name: str) -> Action | None:
    return _ACTIONS.get(name)


def names() -> list[str]:
    return sorted(_ACTIONS)


def signature(name: str) -> inspect.Signature:
    """Argument shape of an action. The config builder reads this."""
    return inspect.signature(_ACTIONS[name])


def run(name: str, args: dict[str, Any]) -> bool:
    fn = get(name)
    if fn is None:
        log.error("unknown action %r", name)
        return False
    try:
        return bool(fn(**args))
    except TypeError as exc:
        log.error("bad arguments for %r: %s", name, exc)
    except Exception:
        log.exception("action %r failed", name)
    return False
