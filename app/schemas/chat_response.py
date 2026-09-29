from pydantic import BaseModel


class CorpusSourceResponse(BaseModel):
    number: int
    book_id: str
    chapter: str | None
    section: str | None
    chunk_index: int
    text: str


class WebSourceResponse(BaseModel):
    number: int
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str
    corpus_sources: list[CorpusSourceResponse]
    web_sources: list[WebSourceResponse]