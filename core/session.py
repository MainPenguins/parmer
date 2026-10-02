import threading
from dataclasses import dataclass, field


@dataclass
class ActiveSession:
    obj: object | None = None
    context: object | None = None
    suggestions: list = field(default_factory=list)
    generation: int = 0
    checked_generation: int = 0

    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def reset(self):
        with self._lock:
            self.obj = None
            self.context = None
            self.suggestions.clear()
            self.generation += 1

    def set_object(self, obj):
        with self._lock:
            self.obj = obj

    def update_suggestions(self, context, suggestions, generation):
        with self._lock:
            self.context = context
            self.suggestions = suggestions.copy()
            self.checked_generation = generation

    def get_snapshot(self):
        with self._lock:
            return {"obj": self.obj, "context": self.context, "suggestions": self.suggestions.copy(), "generation": self.generation, "checked_generation": self.checked_generation}

    def increment_generation(self):
        with self._lock:
            self.generation += 1
            return self.generation

    def invalidate(self):
        with self._lock:
            self.context = None
            self.suggestions.clear()
            self.checked_generation = -1


    def get_generation(self):
        with self._lock:
            return self.generation
