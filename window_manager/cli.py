"""CLI config builder. Captures a trigger, picks an action, writes config.yaml."""

from __future__ import annotations

import inspect
from pathlib import Path

import yaml
from Quartz import CFRunLoopGetCurrent, CFRunLoopRun, CFRunLoopStop

from . import actions, bindings, permissions
from .bindings import KEY, MOUSE, ConfigError, Trigger
from .input import tap
from .input.keys import key_name, modifier_names


def list_actions() -> int:
    for name in actions.names():
        params = actions.registry.signature(name).parameters.values()
        args = " ".join(
            p.name if p.default is inspect.Parameter.empty else f"{p.name}={p.default!r}"
            for p in params
        )
        print(f"{name:<14} {args}")
    return 0


def capture() -> Trigger | None:
    """Run the tap until one trigger arrives, then stop."""
    caught: list[Trigger] = []
    loop = CFRunLoopGetCurrent()

    def take(trigger: Trigger) -> bool:
        caught.append(trigger)
        CFRunLoopStop(loop)
        return True  # swallow, so the capture press does not reach other apps

    handle = tap.install(take)
    print("Press the mouse button or key combination to bind…")
    CFRunLoopRun()
    del handle
    return caught[0] if caught else None


def _trigger_document(trigger: Trigger) -> dict:
    spec: dict = {"type": trigger.kind}
    if trigger.kind == MOUSE:
        spec["button"] = trigger.code
    else:
        spec["key"] = key_name(trigger.code)
    mods = modifier_names(trigger.mods)
    if mods:
        spec["mods"] = mods
    return spec


def _ask_action() -> str:
    available = actions.names()
    print("\nActions: " + ", ".join(available))
    while True:
        name = input("Action: ").strip()
        if name in available:
            return name
        print(f"  unknown action {name!r}")


def _ask_args(name: str) -> dict:
    args = {}
    for param in actions.registry.signature(name).parameters.values():
        default = "" if param.default is inspect.Parameter.empty else str(param.default)
        prompt = f"  {param.name}" + (f" [{default}]" if default else "") + ": "
        value = input(prompt).strip()
        if value:
            # mods reads as a list; everything else stays a plain string.
            args[param.name] = (
                [m.strip() for m in value.replace("+", ",").split(",") if m.strip()]
                if param.name == "mods"
                else value
            )
        elif param.default is inspect.Parameter.empty:
            raise SystemExit(f"{param.name} is required")
    return args


def _read(path: Path) -> dict:
    if not path.exists():
        return {"bindings": []}
    document = yaml.safe_load(path.read_text()) or {}
    document.setdefault("bindings", [])
    return document


def bind(path: Path) -> int:
    """Interactive: capture a trigger, pick an action, append it to the config."""
    missing = permissions.report(prompt=True)
    if "Input Monitoring" in missing:
        print(f"Input Monitoring is missing — open {permissions.SETTINGS_HINT}")
        return 1

    trigger = capture()
    if trigger is None:
        print("nothing captured")
        return 1
    print(f"Captured: {trigger}")

    entry: dict = {"trigger": _trigger_document(trigger), "action": _ask_action()}
    args = _ask_args(entry["action"])
    if args:
        entry["args"] = args

    document = _read(path)
    document["bindings"] = [
        b for b in document["bindings"] if b.get("trigger") != entry["trigger"]
    ] + [entry]

    try:
        bindings.parse(document, known_actions=set(actions.names()))
    except ConfigError as exc:
        print(f"refusing to write: {exc}")
        return 1

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    print(f"wrote {path}")
    return 0
