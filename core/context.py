from dataclasses import dataclass


@dataclass
class Context:
    text: str
    cursor: int
    selection_start: int
    selection_end: int
    application: str | None = None
    field: str | None = None
    language: str = "en-US"
