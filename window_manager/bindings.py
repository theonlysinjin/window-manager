"""Config loading. Maps a trigger to an action name plus arguments."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, NamedTuple

import yaml

from .input.keys import key_name, keycode, modifier_mask, modifier_names

DEFAULT_PATH = Path(
    os.environ.get("WINDOW_MANAGER_CONFIG", "~/.config/window-manager/config.yaml")
).expanduser()

MOUSE = "mouse"
KEY = "key"


class Trigger(NamedTuple):
    kind: str  # MOUSE or KEY
    code: int  # button number or keycode
    mods: int  # modifier bit mask

    def __str__(self) -> str:
        parts = modifier_names(self.mods)
        parts.append(
            f"button{self.code}" if self.kind == MOUSE else key_name(self.code)
        )
        return "+".join(parts)


class Binding(NamedTuple):
    trigger: Trigger
    action: str
    args: dict[str, Any]
    swallow: bool


class ConfigError(Exception):
    pass


def _parse_trigger(spec: Any) -> Trigger:
    if not isinstance(spec, dict):
        raise ConfigError(f"trigger must be a mapping, got {spec!r}")
    kind = str(spec.get("type", "")).lower()
    mods = modifier_mask(spec.get("mods", []))
    if kind == MOUSE:
        button = spec.get("button")
        if not isinstance(button, int):
            raise ConfigError(f"mouse trigger needs an integer button: {spec!r}")
        return Trigger(MOUSE, button, mods)
    if kind == KEY:
        name = spec.get("key")
        if not isinstance(name, str):
            raise ConfigError(f"key trigger needs a key name: {spec!r}")
        return Trigger(KEY, keycode(name), mods)
    raise ConfigError(f"trigger type must be 'mouse' or 'key': {spec!r}")


def parse(document: Any, known_actions=None) -> list[Binding]:
    """Validate a loaded document into bindings. Raises ConfigError."""
    if document is None:
        document = {}
    if not isinstance(document, dict):
        raise ConfigError("config root must be a mapping")

    entries = document.get("bindings") or []
    if not isinstance(entries, list):
        raise ConfigError("'bindings' must be a list")

    bindings: list[Binding] = []
    seen: dict[Trigger, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ConfigError(f"binding must be a mapping, got {entry!r}")
        trigger = _parse_trigger(entry.get("trigger"))
        action = entry.get("action")
        if not isinstance(action, str):
            raise ConfigError(f"binding needs an action name: {entry!r}")
        if known_actions is not None and action not in known_actions:
            raise ConfigError(f"unknown action {action!r}")
        args = entry.get("args") or {}
        if not isinstance(args, dict):
            raise ConfigError(f"'args' must be a mapping: {entry!r}")
        if trigger in seen:
            raise ConfigError(f"duplicate trigger {trigger} ({seen[trigger]} and {action})")
        seen[trigger] = action
        bindings.append(Binding(trigger, action, args, bool(entry.get("swallow", True))))
    return bindings


def load(path: Path | None = None, known_actions=None) -> list[Binding]:
    path = Path(path or DEFAULT_PATH).expanduser()
    if not path.exists():
        raise ConfigError(f"no config at {path}")
    try:
        document = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path}: {exc}") from exc
    return parse(document, known_actions)


def matcher(bindings: list[Binding]):
    """Return a lookup function from Trigger to Binding, or None."""
    table = {b.trigger: b for b in bindings}
    return table.get
