from fastapi import FastAPI

from agent.agent import DostoevskyAgent
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import (
    ChatResponse,
    CorpusSourceResponse,
    WebSourceResponse,
)


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