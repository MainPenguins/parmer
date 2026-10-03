import gi

gi.require_version("Gdk", "4.0")
from gi.repository import Gdk


def get_monitor_at_point(display, x, y):
    if display is None:
        return None

    monitors = display.get_monitors()

    for i in range(monitors.get_n_items()):
        monitor = monitors.get_item(i)
        geometry = monitor.get_geometry()

        if (
            geometry.x <= x < geometry.x + geometry.width
            and geometry.y <= y < geometry.y + geometry.height
        ):
            return monitor

    return None
