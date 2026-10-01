import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from agent.models import AgentStreamEvent, AgentStreamEventType
from app.main import agent, app

client = TestClient(app)


def test_root_serves_research_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'id="research-form"' in response.text
    assert 'src="/static/app.js"' in response.text
    assert 'href="/static/styles.css"' in response.text


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("/static/app.js", "javascript"),
        ("/static/styles.css", "text/css"),
        ("/docs", "text/html"),
        ("/openapi.json", "application/json"),
    ],
)
def test_assets_and_api_documentation_remain_available(path, content_type):
    response = client.get(path)
    assert response.status_code == 200
    assert content_type in response.headers["content-type"]


def test_static_mount_does_not_shadow_api():
    assert client.get("/health").json() == {"status": "ok"}
    paths = client.get("/openapi.json").json()["paths"]
    assert "post" in paths["/chat"]
    assert "post" in paths["/chat/stream"]
    assert client.get("/static/missing.css").status_code == 404
    assert client.get("/static/../app/main.py").status_code == 404


def test_stream_keeps_contract_and_full_passages():
    events = [
        AgentStreamEvent(AgentStreamEventType.STATUS, {"message": "Analyzing your question..."}),
        AgentStreamEvent(AgentStreamEventType.TOKEN, {"text": "Раскольников"}),
        AgentStreamEvent(AgentStreamEventType.SOURCES, {
            "corpus_sources": [{
                "number": 1, "book_id": "crime_and_punishment",
                "chapter": None, "section": "IV", "chunk_index": 28,
                "text": "Full passage retained.",
            }],
            "web_sources": [],
        }),
        AgentStreamEvent(AgentStreamEventType.DONE, {}),
    ]
    with patch.object(agent, "stream", return_value=iter(events)) as stream:
        response = client.post("/chat/stream", json={"message": "Guilt?"})
    stream.assert_called_once_with("Guilt?")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    records = response.text.replace("\r\n", "\n").strip().split("\n\n")
    parsed = []
    for record in records:
        lines = record.splitlines()
        name = next(line[7:] for line in lines if line.startswith("event: "))
        data = json.loads("\n".join(line[6:] for line in lines if line.startswith("data: ")))
        parsed.append((name, data))
    assert [name for name, _ in parsed] == ["status", "token", "sources", "done"]
    assert parsed[1][1]["text"] == "Раскольников"
    assert parsed[2][1]["corpus_sources"][0]["text"] == "Full passage retained."


def test_stream_error_contract_is_unchanged():
    events = [AgentStreamEvent(AgentStreamEventType.ERROR, {
        "message": "Failed to process the request.", "detail": "Internal test detail",
    })]
    with patch.object(agent, "stream", return_value=iter(events)):
        response = client.post("/chat/stream", json={"message": "Question"})
    assert response.status_code == 200
    assert "event: error" in response.text
