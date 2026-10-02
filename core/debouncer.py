import gi

gi.require_version("GLib", "2.0")

from gi.repository import GLib


class Debouncer:
    def __init__(self, delay=500):
        self.delay = delay
        self._source_id = None

    def call(self, callback):
        self.cancel()

        self._source_id = GLib.timeout_add(self.delay, self._run, callback)

    def _run(self, callback):
        self._source_id = None

        callback()

        return GLib.SOURCE_REMOVE

    def cancel(self):
        if self._source_id is not None:
            GLib.source_remove(self._source_id)
            self._source_id = None
