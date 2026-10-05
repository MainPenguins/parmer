from ui.backends.layer_shell import LayerShellBackend


def test_suggestion_click_calls_apply_callback():
    backend = LayerShellBackend(application=None)

    clicked = []

    def callback(index):
        clicked.append(index)

    backend.on_apply_requested(callback)

    backend._on_suggestion_clicked(None, 2)

    assert clicked == [2]
