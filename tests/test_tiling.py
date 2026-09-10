import pytest

from window_manager.actions.tiling import layout_half, layout_maximise, layout_move_display
from window_manager.geometry import Frame
from window_manager.screens import Screen

LEFT = Screen(0, Frame(0, 0, 1600, 1000), Frame(0, 25, 1600, 975))
RIGHT = Screen(1, Frame(1600, 0, 800, 600), Frame(1600, 25, 800, 575))


def test_maximise_fills_the_visible_frame():
    assert layout_maximise(Frame(10, 10, 100, 100), LEFT) == LEFT.visible


def test_half_left_and_right_tile_without_a_gap():
    left = layout_half(Frame(0, 0, 1, 1), LEFT, "left")
    right = layout_half(Frame(0, 0, 1, 1), LEFT, "right")
    assert left == Frame(0, 25, 800, 975)
    assert left.x + left.w == right.x
    assert right.x + right.w == LEFT.visible.x + LEFT.visible.w


def test_half_rejects_an_unknown_side():
    with pytest.raises(ValueError):
        layout_half(Frame(0, 0, 1, 1), LEFT, "sideways")


def test_move_display_keeps_the_relative_frame():
    half = Frame(0, 25, 800, 975)
    assert layout_move_display(half, LEFT, RIGHT, "relative") == Frame(1600, 25, 400, 575)


def test_move_display_keeps_the_size_and_clamps():
    wide = Frame(0, 25, 1200, 900)
    assert layout_move_display(wide, LEFT, RIGHT, "size") == Frame(1600, 25, 800, 575)


def test_move_display_can_maximise_on_arrival():
    assert layout_move_display(Frame(0, 25, 10, 10), LEFT, RIGHT, "maximise") == RIGHT.visible
