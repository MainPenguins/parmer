import gi

gi.require_version("Atspi", "2.0")

from gi.repository import Atspi

from core.context import Context
def changed_span(old_text, new_text):
    if old_text == new_text:
        return None

    start = 0

    while start < len(old_text) and start < len(new_text):
        if old_text[start] != new_text[start]:
            break

        start += 1

    end_old = len(old_text)
    end_new = len(new_text)

    while end_old > start and end_new > start:
        if old_text[end_old - 1] != new_text[end_new - 1]:
            break

        end_old -= 1
        end_new -= 1

    return (start, end_old, end_new)


class TextTracker:
    def __init__(self):
        self.application = None
        self.field = None
        self.role = None
        self.text = ""
        self.cursor = 0
        self.selection_start = 0
        self.selection_end = 0

        self.field_changed = False
        self.context_changed = False
        self.text_changed = False
        self.cursor_moved = False
        self.selection_changed = False
        self.span = None

    def update(self, obj):
        try:
            application = obj.get_application()

            application_name = (
                application.get_name()
                if application
                else "Unknown"
            )

            character_count = Atspi.Text.get_character_count(obj)

            text = Atspi.Text.get_text(obj, 0, character_count)

            cursor = Atspi.Text.get_caret_offset(obj)

            selection_start = cursor
            selection_end = cursor

            if Atspi.Text.get_n_selections(obj) > 0:
                selection = Atspi.Text.get_selection(obj, 0)

                selection_start = selection.start_text
                selection_end = selection.end_text

        except Exception:
            return False

        same_field = (
            application_name == self.application
            and self.field == obj.get_name()
            and self.role == obj.get_role_name()
        )

        self.field_changed = not same_field

        self.text_changed = (
            self.field_changed or text != self.text
        )
        self.context_changed = (
            self.field_changed
            or self.text_changed
        )
        self.cursor_moved = (
            self.field_changed or cursor != self.cursor
        )

        self.selection_changed = (
            self.field_changed
            or selection_start != self.selection_start
            or selection_end != self.selection_end
        )

        if self.text_changed and not self.field_changed:
            self.span = changed_span(self.text, text)
        else:
            self.span = None

        if (
            not self.field_changed
            and not self.text_changed
            and not self.cursor_moved
            and not self.selection_changed
        ):
            return False

        self.application = application_name
        self.field = obj.get_name()
        self.role = obj.get_role_name()
        self.text = text
        self.cursor = cursor
        self.selection_start = selection_start
        self.selection_end = selection_end

        return True

    def get_context(self):
        return Context(
            text=self.text,
            cursor=self.cursor,
            selection_start=self.selection_start,
            selection_end=self.selection_end,
            application=self.application,
            field=self.field,
        )

    def print(self, event_type):
        print("\033[2J\033[H", end="")

        print(f"Event       : {event_type}")
        print(f"Application : {self.application}")
        print(f"Field       : {self.field}")
        print(f"Role        : {self.role}")
        print(f"Cursor      : {self.cursor}")
        print(f"Selection   : {self.selection_start} .. {self.selection_end}")

        if self.span is not None:
            print(f"Span        : {self.span[0]} .. {self.span[1]} -> {self.span[0]} .. {self.span[2]}")

        print("-" * 60)
        print(self.text)
