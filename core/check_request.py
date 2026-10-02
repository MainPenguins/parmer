from dataclasses import dataclass

from core.context import Context


@dataclass(frozen=True)
class CheckRequest:
    context: Context
    generation: int
