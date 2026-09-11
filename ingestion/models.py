from dataclasses import dataclass


@dataclass
class Document:
    book_id: str
    title: str
    author: str
    language: str
    text: str
    start_marker: str | None
    end_marker: str | None


@dataclass
class DocumentSection:
    book_id: str
    content_type: str
    text: str


@dataclass
class Section:
    part: str | None
    part_title: str | None

    book: str | None

    chapter: str | None
    chapter_title: str | None

    section: str | None
    text: str


