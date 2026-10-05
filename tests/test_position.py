# from core.position import Rect, position_popup
from core.position import (Rect, position_popup, relative_to_monitor)

def test_popup_below_caret():
    caret = Rect(
        x=100,
        y=200,
        width=10,
        height=20,
    )

    position = position_popup(
        caret,
        popup_width=300,
        popup_height=100,
        screen_width=1920,
        screen_height=1080,
    )

    assert position.x == 100
    assert position.y == 228


def test_popup_flips_above_when_bottom_space_is_not_enough():
    caret = Rect(
        x=100,
        y=1000,
        width=10,
        height=20,
    )

    position = position_popup(
        caret,
        popup_width=300,
        popup_height=100,
        screen_width=1920,
        screen_height=1080,
    )

    assert position.x == 100
    assert position.y == 892


def test_popup_stays_inside_right_edge():
    caret = Rect(
        x=1800,
        y=200,
        width=10,
        height=20,
    )

    position = position_popup(
        caret,
        popup_width=300,
        popup_height=100,
        screen_width=1920,
        screen_height=1080,
    )

    assert position.x == 1612



def test_rect_relative_to_monitor():
    rect = Rect(
        x=2100,
        y=500,
        width=10,
        height=22,
    )

    relative = relative_to_monitor(
        rect,
        monitor_x=1920,
        monitor_y=0,
    )

    assert relative.x == 180
    assert relative.y == 500
    assert relative.width == 10
    assert relative.height == 22
