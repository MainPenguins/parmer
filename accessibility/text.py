import gi

gi.require_version("Atspi", "2.0")

from gi.repository import Atspi


from core.position import Rect

editable_roles = (
    Atspi.Role.ENTRY,
    Atspi.Role.TEXT,
    Atspi.Role.COMBO_BOX,
)


def is_text_field(obj):
    try:
        role = obj.get_role()

        if role not in editable_roles:
            return False

        state = obj.get_state_set()

        return state.contains(Atspi.StateType.EDITABLE)

    except Exception:
        return False



def get_caret_rect(obj):
    offset = Atspi.Text.get_caret_offset(obj)

    if offset > 0:
        rect = Atspi.Text.get_range_extents(
            obj,
            offset - 1,
            offset,
            Atspi.CoordType.SCREEN,
        )
    else:
        rect = Atspi.Text.get_range_extents(
            obj,
            0,
            1,
            Atspi.CoordType.SCREEN,
        )

    return Rect(
        x=rect.x,
        y=rect.y,
        width=rect.width,
        height=rect.height,
    )
