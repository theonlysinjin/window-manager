from pathlib import Path

import window_manager.actions as actions
from window_manager.bindings import load

EXAMPLE = Path(__file__).resolve().parent.parent / "config.example.yaml"


def test_the_shipped_example_config_loads():
    found = load(EXAMPLE, known_actions=set(actions.names()))
    assert len(found) == 5
