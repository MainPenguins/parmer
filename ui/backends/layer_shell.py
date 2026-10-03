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

    def show(self, monitor, position):
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

        label = Gtk.Label(label="Parmer Popup 🐧")

        label.set_margin_top(20)
        label.set_margin_bottom(20)
        label.set_margin_start(20)
        label.set_margin_end(20)

        window.set_child(label)
        window.present()

        self.window = window

    def hide(self):
        if self.window is not None:
            self.window.close()
            self.window = None
