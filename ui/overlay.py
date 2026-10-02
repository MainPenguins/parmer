import gi

gi.require_version("Gio", "2.0")

gi.require_version("GLib", "2.0")

from gi.repository import Gio, GLib


OBJECT_PATH = "/dev/parmer/Overlay"

INTERFACE = "dev.parmer.Overlay"

SIGNAL_NAME = "ShowRequested"

APPLY_SIGNAL_NAME = "ApplyRequested"


class Overlay:
    def __init__(self):
        self._bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def on_apply_requested(self, callback):
        def handle(bus, sender, path, interface, signal, params, user_data):
            callback(params.unpack()[0])

        self._bus.signal_subscribe(
            None,
            INTERFACE,
            APPLY_SIGNAL_NAME,
            OBJECT_PATH,
            None,
            Gio.DBusSignalFlags.NONE,
            handle,
            None,
        )

    def show(self, application, lines):
        params = GLib.Variant(
            "(sas)",
            (application, lines),
        )

        try:
            self._bus.emit_signal(
                None,
                OBJECT_PATH,
                INTERFACE,
                SIGNAL_NAME,
                params,
            )
        except Exception:
            pass
