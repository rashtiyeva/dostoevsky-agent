from dataclasses import dataclass


@dataclass
class Chunk:
    book_id: str

    part: str | None
    part_title: str | None

    book: str | None

    chapter: str | None
    chapter_title: str | None

    section: str | None
    section_title: str | None

    text: str
    chunk_index: int
    content_type: str