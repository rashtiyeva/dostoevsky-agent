from dataclasses import dataclass


@dataclass
class Document:
    book_id: str
    title: str
    author: str
    language: str
    text: str