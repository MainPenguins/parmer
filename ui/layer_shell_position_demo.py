from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell


class Demo(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.parmer.LayerShellPositionDemo",
        )

    def do_activate(self):
        window = Gtk.Window(application=self)
        window.set_default_size(320, 100)

        LayerShell.init_for_window(window)
        LayerShell.set_namespace(window, "parmer-position-demo")
        LayerShell.set_layer(window, LayerShell.Layer.TOP)

        # Test position
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
            690,
        )

        LayerShell.set_margin(
            window,
            LayerShell.Edge.LEFT,
            176,
        )

        label = Gtk.Label(
            label="Caret position 🐧",
        )

        label.set_margin_top(20)
        label.set_margin_bottom(20)
        label.set_margin_start(20)
        label.set_margin_end(20)

        window.set_child(label)
        window.present()


app = Demo()
app.run([])
