from ui.popup_controller import PopupController
from core.position import Rect

class FakeGeometry:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class FakeMonitor:
    def __init__(self, geometry):
        self.geometry = geometry

    def get_geometry(self):
        return self.geometry


class FakeMonitors:
    def __init__(self, monitors):
        self.monitors = monitors

    def get_n_items(self):
        return len(self.monitors)

    def get_item(self, index):
        return self.monitors[index]


class FakeDisplay:
    def __init__(self, monitors):
        self.monitors = FakeMonitors(monitors)

    def get_monitors(self):
        return self.monitors


def test_get_monitor_at_point():
    monitor_1 = FakeMonitor(
        FakeGeometry(0, 0, 1920, 1080)
    )

    monitor_2 = FakeMonitor(
        FakeGeometry(1920, 0, 1920, 1080)
    )

    display = FakeDisplay([
        monitor_1,
        monitor_2,
    ])

    controller = PopupController(display)

    assert controller.get_monitor(100, 500) is monitor_1
    assert controller.get_monitor(2100, 500) is monitor_2


def test_get_position():
    monitor = FakeMonitor(
        FakeGeometry(1920, 0, 1920, 1080)
    )

    display = FakeDisplay([monitor])

    controller = PopupController(display)

    caret = Rect(
        x=2100,
        y=500,
        width=10,
        height=22,
    )

    result = controller.get_position(
        caret,
        popup_width=320,
        popup_height=100,
    )

    assert result is not None

    returned_monitor, position = result

    assert returned_monitor is monitor
    assert position.x == 180
    assert position.y == 530
