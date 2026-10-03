from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")

from gi.repository import Gdk, Gtk

import threading

from accessibility.atspi import set_popup_ui, start_atspi

from ui.backends.layer_shell import LayerShellBackend
from ui.popup_controller import PopupController


class ParmerApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.parmer.Parmer",
        )
        self.hold()

        self.display = None
        self.popup = None
        self.popup_controller = None

    def do_activate(self):
        display = Gdk.Display.get_default()

        if display is None:
            print("Display: unavailable")
            return

        self.display = display

        self.popup_controller = PopupController(display)
        self.popup = LayerShellBackend(self)

        set_popup_ui(
            self.popup_controller,
            self.popup,
        )
        threading.Thread(
            target=start_atspi,
            daemon=True,
        ).start()
        print("GTK activate reached")
