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

        for line in lines:
            label = Gtk.Label(label=line)
            label.set_xalign(0)
            box.append(label)

        window.set_child(box)
        window.present()

        self.window = window

    def hide(self):
        if self.window is not None:
            self.window.close()
            self.window = None
