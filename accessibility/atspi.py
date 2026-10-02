import threading

import gi

gi.require_version("Atspi", "2.0")
from core.session import ActiveSession
from gi.repository import Atspi, GLib
from core.checker import Checker
from engines.languagetool import LanguageToolEngine
from accessibility.focus import should_handle
from accessibility.text import is_text_field
from core.debouncer import Debouncer
from core.text_tracker import TextTracker
from ui.overlay import Overlay


tracker = TextTracker()
debouncer = Debouncer()
checker = Checker(engine=LanguageToolEngine())
overlay = Overlay()

session = ActiveSession()


def on_apply_requested(index):
    print(f"Apply requested: {index}")
    state = session.get_snapshot()
    context = state["context"]
    suggestions = state["suggestions"]

    if state["checked_generation"] != state["generation"]:
        print("Apply ignored: stale suggestion")
        return

    if state["obj"] is None:
        print("Apply ignored: no active field")

        return

    if context is None or tracker.text != context.text:
        print("Apply ignored: text changed")

        return

    if index < 0 or index >= len(suggestions):
        print("Apply ignored: bad index")

        return

    replacements = suggestions[index].replacements

    if not replacements:
        print("Apply ignored: no replacement")

        return

    replacement = replacements[0]

    try:
        Atspi.EditableText.delete_text(state["obj"], suggestions[index].start, suggestions[index].end)

        Atspi.EditableText.insert_text(
            state["obj"],
            suggestions[index].start,
            replacement,
            len(replacement),
        )

        print("Applied.")
    except Exception as error:
        print(f"Apply error: {error}")


def build_overlay_lines(context, suggestions):
    lines = []

    for suggestion in suggestions:
        original = context.text[suggestion.start:suggestion.end]

        if suggestion.replacements:
            lines.append(f"{original} -> {suggestion.replacements[0]}")
        else:
            lines.append(original)

    return lines


def on_text_checked(suggestions, checked, generation):
    # global active_state

    if generation != session.get_snapshot()["generation"]:
        print("Ignoring stale result")
        return False

    if tracker.text != checked.text:
        return False

    print("Suggestions:")

    for suggestion in suggestions:
        print(suggestion)

    session.update_suggestions(checked, suggestions, generation)

    if suggestions:
        overlay.show(
            checked.application or "",
            build_overlay_lines(checked, suggestions),
        )

    return False


def check_text(context, generation):
    try:
        suggestions = checker.check(context)
    except Exception as error:
        print(f"Grammar check error: {error}")
        return

    GLib.idle_add(on_text_checked, suggestions, context, generation)


def on_text_ready():
    context = tracker.get_context()
    generation = session.get_snapshot()["generation"]

    threading.Thread(target=check_text, args=(context, generation), daemon=True).start()


def on_event(event):
    # global active_object

    try:
        if not should_handle(event):
            return

        obj = event.source

        if obj is None:
            return

        if not is_text_field(obj):
            return

        session.set_object(obj)

        changed = tracker.update(obj)

        if tracker.context_changed:
            generation = session.increment_generation()
            print(f"Generation: {generation}")

        if changed:
            tracker.print(event.type)

            if tracker.text_changed:
                debouncer.call(on_text_ready)

    except Exception as error:
        print(f"AT-SPI error: {error}")


Atspi.init()

focus_listener = Atspi.EventListener.new(on_event)
caret_listener = Atspi.EventListener.new(on_event)
text_listener = Atspi.EventListener.new(on_event)

focus_listener.register(
    "object:state-changed:focused"
)

caret_listener.register(
    "object:text-caret-moved"
)

text_listener.register(
    "object:text-changed"
)

overlay.on_apply_requested(on_apply_requested)

print("Parmer AT-SPI listener started.")
print("Waiting for text input...")

Atspi.event_main()
