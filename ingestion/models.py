from dataclasses import dataclass


@dataclass
class Document:
    book_id: str
    title: str
    author: str
    language: str
    text: str

@dataclass
class Chapter:
    part: str
    chapter: str
    text: str

@dataclass
class Chunk:
    book_id: str
    part: str
    chapter: str
    text: str
    chunk_index: int