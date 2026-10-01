from dataclasses import dataclass, field


@dataclass
class ActiveSession:
    obj: object | None = None
    context: object | None = None
    suggestions: list = field(default_factory=list)
    generation: int = 0
    checked_generation: int = 0

    def reset(self):
        self.obj = None
        self.context = None
        self.suggestions.clear()
        self.generation += 1
