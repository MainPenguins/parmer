import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from core.suggestions import Suggestion


class SuggestionRow(Gtk.Button):
    def __init__(self, suggestion: Suggestion, index, callback):
        super().__init__()

        self.index = index
        self.suggestion = suggestion

        self.add_css_class("suggestion")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
        )

        original = Gtk.Label(
            label=suggestion.replacements[0]
            if suggestion.replacements
            else "",
        )
        original.set_xalign(0)
        original.add_css_class("suggestion-replacement")

        message = Gtk.Label(
            label=suggestion.message,
        )
        message.set_xalign(0)
        message.set_wrap(True)
        message.add_css_class("suggestion-message")

        box.append(original)
        box.append(message)

        self.set_child(box)

        self.connect(
            "clicked",
            self._on_clicked,
            callback,
        )

    def _on_clicked(self, button, callback):
        callback(self.index)
