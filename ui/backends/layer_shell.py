from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell


class LayerShellBackend:
    def __init__(self, application):
        self.application = application
        self.window = None
        self.apply_callback = None

    def on_apply_requested(self, callback):
        self.apply_callback = callback

    # Dafam naze charecter disney e
    def _on_suggestion_clicked(self, button, index):
        print(f"Suggestion clicked: {index}")

        if self.apply_callback is not None:
            self.apply_callback(index)


    def show(self, monitor, position, lines):
        if self.window is not None:
            self.window.close()

        window = Gtk.Window(application=self.application)
        window.set_default_size(320, 100)

        LayerShell.init_for_window(window)
        LayerShell.set_namespace(window, "parmer-popup")
        LayerShell.set_layer(window, LayerShell.Layer.TOP)
        LayerShell.set_monitor(window, monitor)

        LayerShell.set_anchor(
            window,
            LayerShell.Edge.TOP,
            True,
        )

        LayerShell.set_anchor(
            window,
            LayerShell.Edge.LEFT,
            True,
        )

        LayerShell.set_margin(
            window,
            LayerShell.Edge.TOP,
            position.y,
        )

        LayerShell.set_margin(
            window,
            LayerShell.Edge.LEFT,
            position.x,
        )

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )

        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        for index, line in enumerate(lines):
            button = Gtk.Button(label=line)
            button.set_halign(Gtk.Align.FILL)
            # Flick Shot mizanam tiram miss mire
            button.connect("clicked", self._on_suggestion_clicked, index)

            box.append(button)

        window.set_child(box)
        window.present()

        self.window = window

    def hide(self):
        if self.window is not None:
            self.window.close()
            self.window = None



# Tiram miss mire
