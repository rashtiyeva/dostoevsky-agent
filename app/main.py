from fastapi import FastAPI

from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model= ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        answer = f"You asked: {request.message}"
    )