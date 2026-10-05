import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class PopoverDemo(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.parmer.PopoverDemo",
        )

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_default_size(800, 500)

        button = Gtk.Button(label="Click me")
        window.set_child(button)

        popover = Gtk.Popover()
        popover.set_parent(button)

        label = Gtk.Label(label="Parmer suggestion 🐧")
        label.set_margin_top(20)
        label.set_margin_bottom(20)
        label.set_margin_start(20)
        label.set_margin_end(20)

        popover.set_child(label)

        button.connect(
            "clicked",
            lambda *_: popover.popup(),
        )

        window.present()


app = PopoverDemo()
app.run([])
