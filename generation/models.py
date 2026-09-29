from dataclasses import dataclass


@dataclass
class Citation:
    number: int
    book_id: str
    chapter: str | None
    section: str | None
    chunk_index: int
    text: str


@dataclass
class GeneratedAnswer:
    answer: str
    citations: list[Citation]