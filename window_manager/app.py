"""Entry point. Permission check, event tap, run loop."""

from __future__ import annotations

import argparse
import logging
import signal
import sys
from pathlib import Path

from Foundation import NSOperationQueue
from Quartz import CFRunLoopGetCurrent, CFRunLoopRun, CFRunLoopStop

from . import actions, bindings, permissions
from .bindings import Binding, ConfigError, Trigger
from .input import tap
from .watch import watch

log = logging.getLogger("window_manager")


def _load(path: Path) -> list[Binding]:
    found = bindings.load(path, known_actions=set(actions.names()))
    log.info("loaded %d bindings from %s", len(found), path)
    return found


def _later(fn, *args) -> None:
    """Queue work on the main run loop. The block must return None or pyobjc raises."""

    def block() -> None:
        fn(*args)

    NSOperationQueue.mainQueue().addOperationWithBlock_(block)


def _dispatch(lookup, trigger: Trigger) -> bool:
    """Match a trigger and queue its action. Returns True to swallow the event."""
    binding = lookup(trigger)
    if binding is None:
        return False
    log.debug("%s -> %s %s", trigger, binding.action, binding.args)
    # Run off the tap callback so a slow AX call cannot time the tap out.
    _later(actions.registry.run, binding.action, binding.args)
    return binding.swallow


def run(path: Path, debug: bool = False) -> int:
    missing = permissions.report(prompt=True)
    if missing:
        log.error("missing grants: %s — open %s", ", ".join(missing), permissions.SETTINGS_HINT)
        return 1

    try:
        found = _load(path)
        state = {"bindings": found, "lookup": bindings.matcher(found)}
    except ConfigError as exc:
        log.error("%s", exc)
        return 1

    def reload_config() -> None:
        try:
            found = _load(path)
            state["bindings"], state["lookup"] = found, bindings.matcher(found)
        except ConfigError as exc:
            log.error("reload failed, keeping the old bindings: %s", exc)

    handle = tap.install(lambda trigger: _dispatch(state["lookup"], trigger), debug=debug)
    timer = watch(path, reload_config)

    loop = CFRunLoopGetCurrent()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: CFRunLoopStop(loop))

    log.info("running — %d bindings, ctrl-c to stop", len(state["bindings"]))
    CFRunLoopRun()
    timer.invalidate()
    del handle
    log.info("stopped")
    return 0


def check(path: Path) -> int:
    missing = permissions.report(prompt=False)
    print("Accessibility:    ", "missing" if "Accessibility" in missing else "granted")
    print("Input Monitoring: ", "missing" if "Input Monitoring" in missing else "granted")
    try:
        found = _load(path)
    except ConfigError as exc:
        print(f"Config:            {exc}")
        return 1
    print(f"Config:            {path} ({len(found)} bindings)")
    for binding in found:
        print(f"  {str(binding.trigger):<24} {binding.action} {binding.args or ''}")
    return 1 if missing else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="window-manager", description=__doc__)
    parser.add_argument("--config", type=Path, default=bindings.DEFAULT_PATH)
    parser.add_argument("--verbose", "-v", action="store_true")
    sub = parser.add_subparsers(dest="command")
    run_cmd = sub.add_parser("run", help="start the background runner (default)")
    run_cmd.add_argument("--debug", action="store_true", help="log every tap event")
    sub.add_parser("check", help="report permissions and the loaded config")
    sub.add_parser("actions", help="list registered actions and their arguments")
    sub.add_parser("bind", help="capture a trigger and add a binding")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    if args.command == "check":
        return check(args.config)
    if args.command == "actions":
        from .cli import list_actions

        return list_actions()
    if args.command == "bind":
        from .cli import bind

        return bind(args.config)
    return run(args.config, debug=getattr(args, "debug", False))


if __name__ == "__main__":
    sys.exit(main())
