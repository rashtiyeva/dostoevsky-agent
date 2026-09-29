from fastapi import FastAPI

from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse, CitationResponse
from app.services.rag_service import generate_rag_response

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = generate_rag_response(request.message)

    return ChatResponse(
        answer=result.answer,
        citations=[
            CitationResponse(
                number=citation.number,
                book_id=citation.book_id,
                chapter=citation.chapter,
                section=citation.section,
                chunk_index=citation.chunk_index,
                text=citation.text,
            )
            for citation in result.citations
        ],
    )