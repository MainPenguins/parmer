import threading
from gi.repository import GLib


class CheckerService:
    def __init__(self, checker):
        self.checker = checker
        self._lock = threading.Lock()
        self._request_id = 0

    def check_async(self, request, callback):
        with self._lock:
            self._request_id += 1
            request_id = self._request_id

        thread = threading.Thread(target=self._run, args=(request, callback, request_id), daemon=True)

        thread.start()

    def _run(self, request, callback, request_id):
        with self._lock:
            if request_id != self._request_id:
                return
        try:
            suggestions = self.checker.check(request.context)



        except Exception as error:
            print(f"Grammar check error: {error}")
            return

        with self._lock:
            if request_id != self._request_id:
                return

        GLib.idle_add(
            callback,
            suggestions,
            request,
        )
