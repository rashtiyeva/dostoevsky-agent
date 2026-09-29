from dataclasses import dataclass


@dataclass
class CorpusSource:
    number: int
    book_id: str
    chapter: str | None
    section: str | None
    chunk_index: int
    text: str


@dataclass
class WebSource:
    number: int
    title: str
    url: str


@dataclass
class CorpusSearchResult:
    sources: list[CorpusSource]


@dataclass
class WebSearchResult:
    answer: str
    sources: list[WebSource]