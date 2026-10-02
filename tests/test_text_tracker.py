from unittest.mock import Mock, patch

from core.text_tracker import TextTracker


def make_text_object(
    text="",
    cursor=0,
    name="Input",
    role="text",
    application="Test App",
    selection=None,
):
    obj = Mock()

    app = Mock()
    app.get_name.return_value = application

    obj.get_application.return_value = app
    obj.get_name.return_value = name
    obj.get_role_name.return_value = role

    if selection is None:
        selection_start = cursor
        selection_end = cursor
    else:
        selection_start, selection_end = selection

    return obj, {
        "text": text,
        "cursor": cursor,
        "selection_start": selection_start,
        "selection_end": selection_end,
    }


def update_atspi(atspi_mock, obj, state):
    atspi_mock.Text.get_character_count.return_value = len(
        state["text"]
    )

    atspi_mock.Text.get_text.return_value = state["text"]

    atspi_mock.Text.get_caret_offset.return_value = state["cursor"]

    if state["selection_start"] == state["selection_end"]:
        atspi_mock.Text.get_n_selections.return_value = 0
    else:
        selection = Mock()
        selection.start_text = state["selection_start"]
        selection.end_text = state["selection_end"]

        atspi_mock.Text.get_n_selections.return_value = 1
        atspi_mock.Text.get_selection.return_value = selection


@patch("core.text_tracker.Atspi")
def test_first_update(mock_atspi):
    tracker = TextTracker()

    obj, state = make_text_object(
        text="hello",
        cursor=5,
    )

    update_atspi(mock_atspi, obj, state)

    assert tracker.update(obj) is True

    assert tracker.text == "hello"
    assert tracker.cursor == 5
    assert tracker.field == "Input"
    assert tracker.application == "Test App"


@patch("core.text_tracker.Atspi")
def test_unchanged_text_is_ignored(mock_atspi):
    tracker = TextTracker()

    obj, state = make_text_object(
        text="hello",
        cursor=5,
    )

    update_atspi(mock_atspi, obj, state)
    assert tracker.update(obj) is True

    update_atspi(mock_atspi, obj, state)
    assert tracker.update(obj) is False


@patch("core.text_tracker.Atspi")
def test_text_change_is_detected(mock_atspi):
    tracker = TextTracker()

    obj, state = make_text_object(
        text="hello",
        cursor=5,
    )

    update_atspi(mock_atspi, obj, state)
    assert tracker.update(obj) is True

    state["text"] = "hello world"
    state["cursor"] = 11

    update_atspi(mock_atspi, obj, state)

    assert tracker.update(obj) is True
    assert tracker.text_changed is True
    assert tracker.span == (5, 5, 11)
    assert tracker.text == "hello world"


@patch("core.text_tracker.Atspi")
def test_cursor_movement_is_detected(mock_atspi):
    tracker = TextTracker()

    obj, state = make_text_object(
        text="hello",
        cursor=5,
    )

    update_atspi(mock_atspi, obj, state)
    tracker.update(obj)

    state["cursor"] = 2

    update_atspi(mock_atspi, obj, state)

    assert tracker.update(obj) is True
    assert tracker.cursor_moved is True
    assert tracker.text_changed is False


@patch("core.text_tracker.Atspi")
def test_selection_change_is_detected(mock_atspi):
    tracker = TextTracker()

    obj, state = make_text_object(
        text="hello",
        cursor=5,
        selection=(0, 5),
    )

    update_atspi(mock_atspi, obj, state)
    tracker.update(obj)

    state["selection_start"] = 0
    state["selection_end"] = 2

    update_atspi(mock_atspi, obj, state)

    assert tracker.update(obj) is True
    assert tracker.selection_changed is True
