from collections.abc import Iterable

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

from agent.agent import DostoevskyAgent
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import (
    ChatResponse,
    CorpusSourceResponse,
    WebSourceResponse,
)
from app.streaming import to_sse_events

app = FastAPI()

agent = DostoevskyAgent()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = agent.run(request.message)

    return ChatResponse(
        answer=result.answer,
        corpus_sources=[
            CorpusSourceResponse(
                number=source.number,
                book_id=source.book_id,
                chapter=source.chapter,
                section=source.section,
                chunk_index=source.chunk_index,
                text=source.text,
            )
            for source in result.corpus_sources
        ],
        web_sources=[
            WebSourceResponse(
                number=source.number,
                title=source.title,
                url=source.url,
            )
            for source in result.web_sources
        ],
    )


@app.post(
    "/chat/stream",
    response_class=EventSourceResponse,
)
def chat_stream(
    request: ChatRequest,
) -> Iterable[ServerSentEvent]:
    return to_sse_events(
        agent.stream(request.message)
    )