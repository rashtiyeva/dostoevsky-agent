from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from agent.models import AgentResponse
from app.main import agent, app
from tools.models import CorpusSource, WebSource

client = TestClient(app)


def test_chat_returns_agent_response():
    original_run = agent.run

    agent.run = AsyncMock(
        return_value=AgentResponse(
            answer="Test answer",
            corpus_sources=[
                CorpusSource(
                    number=1,
                    book_id="crime_and_punishment",
                    chapter=None,
                    section="I",
                    chunk_index=3,
                    text="Test passage",
                )
            ],
            web_sources=[
                WebSource(
                    number=1,
                    title="Test Source",
                    url="https://example.com",
                )
            ],
        )
    )

    try:
        response = client.post(
            "/chat",
            json={"message": "Test question"},
        )
    finally:
        agent.run = original_run

    assert response.status_code == 200

    body = response.json()

    assert body["answer"] == "Test answer"

    assert len(body["corpus_sources"]) == 1
    assert body["corpus_sources"][0]["book_id"] == "crime_and_punishment"
    assert body["corpus_sources"][0]["text"] == "Test passage"

    assert len(body["web_sources"]) == 1
    assert body["web_sources"][0]["title"] == "Test Source"
    assert body["web_sources"][0]["url"] == "https://example.com"