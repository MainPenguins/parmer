from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell


def on_activate(app):
    window = Gtk.Window(application=app)

    window.set_default_size(320, 100)

    LayerShell.init_for_window(window)
    LayerShell.set_layer(window, LayerShell.Layer.TOP)

    LayerShell.set_anchor(
        window,
        LayerShell.Edge.TOP,
        True,
    )

    LayerShell.set_anchor(
        window,
        LayerShell.Edge.RIGHT,
        True,
    )

    LayerShell.set_margin(
        window,
        LayerShell.Edge.TOP,
        40,
    )

    LayerShell.set_margin(window, LayerShell.Edge.RIGHT, 40)

    label = Gtk.Label(label="Kire Amir")
    label.set_margin_top(20)
    label.set_margin_bottom(20)
    label.set_margin_start(20)
    label.set_margin_end(20)

    window.set_child(label)
    window.present()


app = Gtk.Application(application_id="dev.parmer.LayerShellDemo")

app.connect("activate", on_activate)
app.run(None)
