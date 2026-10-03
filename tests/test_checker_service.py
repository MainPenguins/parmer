import threading

from core.checker_service import CheckerService
from core.check_request import CheckRequest
from core.context import Context


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
