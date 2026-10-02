from dataclasses import dataclass


@dataclass
class Suggestion:
    message: str
    start: int
    end: int
    replacements: list[str]
