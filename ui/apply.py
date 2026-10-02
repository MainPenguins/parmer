import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gio", "2.0")

from gi.repository import GLib, Gio

OBJECT_PATH = "/dev/parmer/Overlay"

INTERFACE = "dev.parmer.Overlay"

APPLY_SIGNAL_NAME = "ApplyRequested"


def main():
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    bus.emit_signal(
        None,
        OBJECT_PATH,
        INTERFACE,
        APPLY_SIGNAL_NAME,
        GLib.Variant("(i)", (0,)),
    )


main()
