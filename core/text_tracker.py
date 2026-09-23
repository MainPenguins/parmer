from gi.repository import Atspi


class TextTracker:
    def __init__(self):
        self.application = None
        self.field = None
        self.text = ""
        self.cursor = 0

    def update(self, obj):
        application = obj.get_application()

        self.application = (
            application.get_name()
            if application
            else "Unknown"
        )

        self.field = obj.get_name()

        self.cursor = Atspi.Text.get_caret_offset(obj)

        character_count = Atspi.Text.get_character_count(obj)

        self.text = Atspi.Text.get_text(
            obj,
            0,
            character_count
        )

    def print(self, event_type):
        print("\033[2J\033[H", end="")

        print(f"Event       : {event_type}")
        print(f"Application : {self.application}")
        print(f"Field       : {self.field}")
        print(f"Cursor      : {self.cursor}")
        print("-" * 60)
        print(self.text)
