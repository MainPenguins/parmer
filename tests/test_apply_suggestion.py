import accessibility.atspi as atspi

from core.suggestions import Suggestion


def test_apply_suggestion(monkeypatch):
    applied = []

    class FakeEditableText:
        @staticmethod
        def delete_text(obj, start, end):
            applied.append(
                ("delete", obj, start, end)
            )

        @staticmethod
        def insert_text(obj, offset, text, length):
            applied.append(
                ("insert", obj, offset, text, length)
            )

    monkeypatch.setattr(
        atspi.Atspi,
        "EditableText",
        FakeEditableText,
    )

    obj = object()

    suggestion = Suggestion(
        message="Use these instead.",
        start=0,
        end=4,
        replacements=["these"],
    )

    atspi.session.set_object(obj)

    atspi.tracker.text = "this are amir"

    context = atspi.tracker.get_context()

    generation = atspi.session.get_snapshot()["generation"]

    atspi.session.update_suggestions(
        context,
        [suggestion],
        generation,
    )

    atspi.on_apply_requested(0)

    assert applied == [
        ("delete", obj, 0, 4),
        ("insert", obj, 0, "these", 5),
    ]


def test_apply_ignores_stale_suggestion(monkeypatch):
    applied = []

    class FakeEditableText:
        @staticmethod
        def delete_text(obj, start, end):
            applied.append(("delete", obj, start, end))

        @staticmethod
        def insert_text(obj, offset, text, length):
            applied.append(("insert", obj, offset, text, length))

    monkeypatch.setattr(
        atspi.Atspi,
        "EditableText",
        FakeEditableText,
    )

    obj = object()

    suggestion = Suggestion(
        message="Use these instead.",
        start=0,
        end=4,
        replacements=["these"],
    )

    atspi.session.set_object(obj)
    atspi.tracker.text = "this are amir"

    context = atspi.tracker.get_context()

    generation = atspi.session.get_snapshot()["generation"]

    atspi.session.update_suggestions(
        context,
        [suggestion],
        generation,
    )

    # Simulate text changing after the suggestion was generated.
    atspi.tracker.text = "these are amir"

    atspi.on_apply_requested(0)

    assert applied == []


def test_apply_ignores_invalid_index(monkeypatch):
    applied = []

    class FakeEditableText:
        @staticmethod
        def delete_text(*args):
            applied.append("delete")

        @staticmethod
        def insert_text(*args):
            applied.append("insert")

    monkeypatch.setattr(
        atspi.Atspi,
        "EditableText",
        FakeEditableText,
    )

    obj = object()

    suggestion = Suggestion(
        message="Use these instead.",
        start=0,
        end=4,
        replacements=["these"],
    )

    atspi.session.set_object(obj)
    atspi.tracker.text = "this are amir"

    context = atspi.tracker.get_context()
    generation = atspi.session.get_snapshot()["generation"]

    atspi.session.update_suggestions(
        context,
        [suggestion],
        generation,
    )

    atspi.on_apply_requested(99)

    assert applied == []


def test_apply_ignores_suggestion_without_replacement(monkeypatch):
    applied = []

    class FakeEditableText:
        @staticmethod
        def delete_text(*args):
            applied.append("delete")

        @staticmethod
        def insert_text(*args):
            applied.append("insert")

    monkeypatch.setattr(
        atspi.Atspi,
        "EditableText",
        FakeEditableText,
    )

    obj = object()

    suggestion = Suggestion(
        message="Something is wrong.",
        start=0,
        end=4,
        replacements=[],
    )

    atspi.session.set_object(obj)
    atspi.tracker.text = "this are amir"

    context = atspi.tracker.get_context()
    generation = atspi.session.get_snapshot()["generation"]

    atspi.session.update_suggestions(
        context,
        [suggestion],
        generation,
    )

    atspi.on_apply_requested(0)

    assert applied == []
