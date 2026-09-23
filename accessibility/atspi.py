import gi

gi.require_version("Atspi", "2.0")

from gi.repository import Atspi

from core.text_tracker import TextTracker


tracker = TextTracker()


def on_event(event):
    try:
        obj = event.source

        if not obj.is_text():
            return

        tracker.update(obj)
        tracker.print(event.type)

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

print("Parmer AT-SPI listener started.")
print("Waiting for text input...")

Atspi.event_main()
