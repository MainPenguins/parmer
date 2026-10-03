from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class PopupPosition:
    x: int
    y: int


def position_popup(
    caret: Rect,
    popup_width: int,
    popup_height: int,
    screen_width: int,
    screen_height: int,
    gap: int = 8,
) -> PopupPosition:
    x = caret.x
    y = caret.y + caret.height + gap

    if x + popup_width > screen_width:
        x = screen_width - popup_width - gap

    if x < gap:
        x = gap

    if y + popup_height > screen_height:
        y = caret.y - popup_height - gap

    if y < gap:
        y = gap

    return PopupPosition(x=x, y=y)


def relative_to_monitor(rect, monitor_x, monitor_y):
    return Rect(
        x=rect.x - monitor_x,
        y=rect.y - monitor_y,
        width=rect.width,
        height=rect.height,
    )
