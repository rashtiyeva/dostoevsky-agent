from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.sse import EventSourceResponse
from fastapi.staticfiles import StaticFiles

from agent.agent import DostoevskyAgent
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import (
    ChatResponse,
    CorpusSourceResponse,
    WebSourceResponse,
)
from app.streaming import to_sse_events

app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)

agent = DostoevskyAgent()


@app.get("/", include_in_schema=False)
def research_ui():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await agent.run(request.message)

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
async def chat_stream(request: ChatRequest):
    async for event in to_sse_events(
        agent.stream(request.message)
    ):
        yield event