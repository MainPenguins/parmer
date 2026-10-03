import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from core.position import Rect


def get_caret_rect(obj):
    caret = Atspi.Text.get_caret_offset(obj)

    if caret < 0:
        return None

    character_count = Atspi.Text.get_character_count(obj)

    if character_count == 0:
        return None

    offset = min(caret, character_count - 1)

    rect = Atspi.Text.get_character_extents(
        obj,
        offset,
        Atspi.CoordType.SCREEN,
    )

    if rect.x < 0 or rect.y < 0:
        return None

    return Rect(x=rect.x, y=rect.y, width=rect.width, height=rect.height)
