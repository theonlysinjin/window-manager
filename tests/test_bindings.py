import pytest

from window_manager.bindings import KEY, MOUSE, ConfigError, matcher, parse
from window_manager.input.keys import keycode, modifier_mask

ACTIONS = {"maximise", "half"}


def test_parses_a_mouse_and_a_key_trigger():
    found = parse(
        {
            "bindings": [
                {"trigger": {"type": "mouse", "button": 3}, "action": "maximise"},
                {
                    "trigger": {"type": "key", "key": "f13", "mods": ["ctrl", "alt"]},
                    "action": "half",
                    "args": {"side": "right"},
                },
            ]
        },
        ACTIONS,
    )
    assert found[0].trigger == (MOUSE, 3, 0)
    assert found[1].trigger == (KEY, keycode("f13"), modifier_mask(["ctrl", "alt"]))
    assert found[1].args == {"side": "right"}
    assert found[0].swallow is True


def test_matcher_ignores_a_different_modifier_set():
    found = parse(
        {"bindings": [{"trigger": {"type": "key", "key": "f13", "mods": ["ctrl"]}, "action": "maximise"}]},
        ACTIONS,
    )
    lookup = matcher(found)
    assert lookup((KEY, keycode("f13"), modifier_mask(["ctrl"]))) is not None
    assert lookup((KEY, keycode("f13"), 0)) is None


@pytest.mark.parametrize(
    "document",
    [
        {"bindings": [{"trigger": {"type": "mouse", "button": 3}, "action": "nope"}]},
        {"bindings": [{"trigger": {"type": "wheel", "button": 3}, "action": "maximise"}]},
        {"bindings": [{"trigger": {"type": "mouse"}, "action": "maximise"}]},
        {"bindings": [{"trigger": {"type": "key", "key": "f99"}, "action": "maximise"}]},
        {"bindings": [{"trigger": {"type": "key", "key": "f13", "mods": ["hyper"]}, "action": "maximise"}]},
        {"bindings": "not-a-list"},
    ],
)
def test_rejects_bad_config(document):
    with pytest.raises((ConfigError, KeyError)):
        parse(document, ACTIONS)


def test_rejects_a_duplicate_trigger():
    document = {
        "bindings": [
            {"trigger": {"type": "mouse", "button": 3}, "action": "maximise"},
            {"trigger": {"type": "mouse", "button": 3}, "action": "half"},
        ]
    }
    with pytest.raises(ConfigError):
        parse(document, ACTIONS)


def test_empty_config_is_valid():
    assert parse(None) == []


def test_the_fn_bit_is_ignored():
    """macOS stamps fn on every function key press. A bare f13 binding must still match."""
    from Quartz import kCGEventFlagMaskSecondaryFn

    from window_manager.input.keys import MODIFIER_MASK

    found = parse(
        {"bindings": [{"trigger": {"type": "key", "key": "f13"}, "action": "maximise"}]},
        ACTIONS,
    )
    as_reported = int(kCGEventFlagMaskSecondaryFn) & MODIFIER_MASK
    assert matcher(found)((KEY, keycode("f13"), as_reported)) is not None


def test_dispatch_queues_the_action_and_returns_the_swallow_flag():
    """The queued block must return None; pyobjc raises on any other value."""
    from window_manager import app

    found = parse(
        {"bindings": [{"trigger": {"type": "mouse", "button": 3}, "action": "maximise"}]},
        ACTIONS,
    )
    queued = []
    app.NSOperationQueue = type(
        "Stub", (), {"mainQueue": staticmethod(lambda: type(
            "Q", (), {"addOperationWithBlock_": staticmethod(queued.append)})())}
    )
    try:
        assert app._dispatch(matcher(found), (MOUSE, 3, 0)) is True
        assert app._dispatch(matcher(found), (MOUSE, 9, 0)) is False
        assert len(queued) == 1
        assert queued[0]() is None
    finally:
        from Foundation import NSOperationQueue

        app.NSOperationQueue = NSOperationQueue
