
import gi

gi.require_version("Atspi", "2.0")

from core.checker_service import CheckerService
from core.session import ActiveSession
from gi.repository import Atspi, GLib
from core.checker import Checker
from engines.languagetool import LanguageToolEngine
from accessibility.focus import should_handle
from accessibility.text import is_text_field
from core.debouncer import Debouncer
from core.text_tracker import TextTracker
from ui.overlay import Overlay


from core.check_request import CheckRequest


tracker = TextTracker()
debouncer = Debouncer()
checker = Checker(engine=LanguageToolEngine())

checker_service = CheckerService(checker)
overlay = Overlay()

session = ActiveSession()


def create_check_request():
    context = tracker.get_context()
    generation = session.get_snapshot()["generation"]

    return CheckRequest(context=context, generation=generation)

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


def on_text_checked(suggestions, request):
    # global active_state

    if request.generation != session.get_snapshot()["generation"]:
        print("Ignoring stale result")
        return False

    if tracker.text != request.context.text:
        return False

    print("Suggestions:")

    for suggestion in suggestions:
        print(suggestion)

    session.update_suggestions(request.context, suggestions, request.generation)

    if suggestions:
        overlay.show(request.context.application or "", build_overlay_lines(request.context, suggestions))

    return False


# def check_text(request):
#
#     try:
#         suggestions = checker.check(request.context)
#     except Exception as error:
#         print(f"Grammar check error: {error}")
#         return
#
#     GLib.idle_add(on_text_checked, suggestions, request)


def on_text_ready():
    request = create_check_request()

    checker_service.check_async(request, on_text_checked)


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
            session.invalidate()
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
