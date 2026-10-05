from ui.backends.layer_shell import LayerShellBackend


def test_suggestion_click_calls_apply_callback():
    backend = LayerShellBackend(application=None)

    clicked = []

    def callback(index):
        clicked.append(index)

    backend.on_apply_requested(callback)

    backend._on_suggestion_clicked(None, 2)

    assert clicked == [2]

def test_apply_callback_can_be_registered_and_replaced():
    backend = LayerShellBackend(application=None)

    first = []
    second = []

    backend.on_apply_requested(
        lambda index: first.append(index)
    )

    backend._on_suggestion_clicked(None, 1)

    backend.on_apply_requested(
        lambda index: second.append(index)
    )

    backend._on_suggestion_clicked(None, 2)

    assert first == [1]
    assert second == [2]
