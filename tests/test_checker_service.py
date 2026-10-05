import threading

from core.checker_service import CheckerService
from core.check_request import CheckRequest
from core.context import Context
from gi.repository import GLib

class FakeChecker:
    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()

    def check(self, context):
        self.started.set()
        self.release.wait()
        return ["result"]


def test_old_request_is_ignored():
    checker = FakeChecker()
    service = CheckerService(checker)

    callback_called = threading.Event()
    callback_results = []

    def callback(suggestions, request):
        callback_results.append(suggestions)
        callback_called.set()
        return False

    context = Context(
        text="hello",
        cursor=5,
        selection_start=5,
        selection_end=5,
    )

    request1 = CheckRequest(context=context, generation=1)
    request2 = CheckRequest(context=context, generation=2)

    service.check_async(request1, callback)

    assert checker.started.wait(timeout=1)

    service.check_async(request2, callback)

    checker.release.set()

    assert not callback_called.wait(timeout=0.5)
    assert callback_results == []


def test_current_request_calls_callback():
    checker = FakeChecker()
    service = CheckerService(checker)

    callback_called = threading.Event()
    callback_results = []

    def callback(suggestions, request):
        callback_results.append((suggestions, request))
        callback_called.set()
        return False

    context = Context(
        text="hello",
        cursor=5,
        selection_start=5,
        selection_end=5,
    )

    request = CheckRequest(context=context, generation=1)

    service.check_async(request, callback)

    assert checker.started.wait(timeout=1)

    checker.release.set()

    main_loop = GLib.MainLoop()

    def stop_loop():
        if callback_called.is_set():
            main_loop.quit()
            return False

        return True

    GLib.timeout_add(10, stop_loop)
    main_loop.run()

    assert len(callback_results) == 1
    assert callback_results[0][0] == ["result"]
    assert callback_results[0][1] == request
