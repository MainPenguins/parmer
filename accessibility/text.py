import gi

gi.require_version("Atspi", "2.0")

from gi.repository import Atspi


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
