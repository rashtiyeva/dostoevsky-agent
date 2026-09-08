from fastapi import FastAPI

from app.llm.openai_client import generate_response
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = generate_response(request.message)

    return ChatResponse(
        answer=answer
    )