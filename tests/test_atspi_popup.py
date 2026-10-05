import accessibility.atspi as atspi


def test_set_popup_ui_registers_apply_callback():
    class FakePopupController:
        def __init__(self):
            self.callback = None

        def on_apply_requested(self, callback):
            self.callback = callback

    controller = FakePopupController()
    popup = object()

    atspi.set_popup_ui(controller, popup)

    assert atspi.popup_controller is controller
    assert atspi.popup is popup
    assert atspi.popup_controller.callback is atspi.on_apply_requested

def test_on_text_checked_shows_popup(monkeypatch):
    shown = []

    class FakePopupController:
        def show_at_caret(self, popup, caret, suggestions):
            shown.append((popup, caret, suggestions))

    popup = object()
    controller = FakePopupController()

    monkeypatch.setattr(atspi, "popup_controller", controller)
    monkeypatch.setattr(atspi, "popup", popup)

    obj = object()
    atspi.session.set_object(obj)

    atspi.tracker.text = "this are amir"
    context = atspi.tracker.get_context()

    generation = atspi.session.get_snapshot()["generation"]

    from core.suggestions import Suggestion

    suggestions = [
        Suggestion(
            message="Use these instead.",
            start=0,
            end=4,
            replacements=["these"],
        )
    ]

    request = atspi.CheckRequest(
        context=context,
        generation=generation,
    )

    from core.position import Rect

    monkeypatch.setattr(
        atspi,
        "get_caret_rect",
        lambda obj: Rect(
            x=100,
            y=200,
            width=7,
            height=22,
        ),
    )

    atspi.on_text_checked(suggestions, request)

    assert len(shown) == 1

    shown_popup, caret, shown_suggestions = shown[0]

    assert shown_popup is popup

    assert caret.x == 100
    assert caret.y == 200
    assert caret.width == 7
    assert caret.height == 22

    assert shown_suggestions == suggestions
