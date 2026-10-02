def is_focus_event(event):
    return event.type == "object:state-changed:focused"


def is_focus_gained(event):
    return is_focus_event(event) and event.detail1 == 1


def should_handle(event):
    if is_focus_event(event):
        return is_focus_gained(event)

    if event.type == "object:text-caret-moved":
        return True

    return event.type.startswith("object:text-changed")
