import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")

from gi.repository import Gdk, Gtk


class PopupDemo(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.parmer.GdkPopupDemo",
        )

    def do_activate(self):
        display = Gdk.Display.get_default()

        if display is None:
            print("Display unavailable")
            return

        print(f"Display: {display.get_name()}")

        surfaces = display.get_default_seat()

        print(f"Seat: {surfaces}")

        window = Gtk.Window(application=self)
        window.set_default_size(400, 100)

        label = Gtk.Label(label="GDK Popup test 🐧")
        window.set_child(label)

        window.present()


app = PopupDemo()
app.run([])
