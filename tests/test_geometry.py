from window_manager.geometry import (
    Frame, clamped, fraction, overlap_area, relative, scaled_into,
)

SCREEN = Frame(0, 0, 1600, 1000)


def test_fraction_splits_the_frame():
    assert fraction(SCREEN, 0.5, 0, 0.5, 1) == Frame(800, 0, 800, 1000)


def test_fraction_respects_the_origin():
    assert fraction(Frame(100, 50, 800, 600), 0, 0, 0.5, 1) == Frame(100, 50, 400, 600)


def test_relative_and_scaled_into_round_trip():
    inner = Frame(400, 250, 800, 500)
    other = Frame(1600, 0, 800, 500)
    assert scaled_into(relative(inner, SCREEN), SCREEN) == inner
    assert scaled_into(relative(inner, SCREEN), other) == Frame(1800, 125, 400, 250)


def test_clamped_shrinks_and_shifts():
    assert clamped(Frame(1500, -50, 400, 1200), SCREEN) == Frame(1200, 0, 400, 1000)


def test_overlap_area_is_zero_when_apart():
    assert overlap_area(SCREEN, Frame(1600, 0, 800, 600)) == 0
    assert overlap_area(SCREEN, Frame(1200, 0, 800, 1000)) == 400 * 1000
