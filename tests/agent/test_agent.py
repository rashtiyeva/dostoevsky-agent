from unittest.mock import Mock, patch

from agent.agent import DostoevskyAgent
from agent.models import AgentDecision, AgentToolCall, ToolName
from tools.models import (
    CorpusSearchResult,
    CorpusSource,
    WebSearchResult,
    WebSource,
)


def create_agent() -> DostoevskyAgent:
    agent = DostoevskyAgent.__new__(DostoevskyAgent)
    agent.executor = Mock()
    return agent


def test_run_returns_answer_when_no_tool_is_needed():
    agent = create_agent()

    agent.decide_tools = Mock(
        return_value=AgentDecision(
            tool_calls=[],
            answer="This question is outside my scope.",
        )
    )

    result = agent.run("What is the capital of France?")

    assert result.answer == "This question is outside my scope."
    assert result.corpus_sources == []
    assert result.web_sources == []
    agent.executor.execute.assert_not_called()


@patch("agent.agent.client")
def test_run_executes_corpus_search(mock_client):
    agent = create_agent()

    agent.decide_tools = Mock(
        return_value=AgentDecision(
            tool_calls=[
                AgentToolCall(
                    tool=ToolName.CORPUS_SEARCH,
                    query="Raskolnikov extraordinary people",
                )
            ]
        )
    )

    agent.executor.execute.return_value = CorpusSearchResult(
        sources=[
            CorpusSource(
                number=1,
                book_id="crime_and_punishment",
                chapter=None,
                section="I",
                chunk_index=3,
                text="Test passage",
            )
        ]
    )

    mock_client.responses.create.return_value.output_text = "Final answer"

    result = agent.run("What does Raskolnikov believe?")

    assert result.answer == "Final answer"

    assert len(result.corpus_sources) == 1
    assert result.corpus_sources[0].book_id == "crime_and_punishment"
    assert result.corpus_sources[0].text == "Test passage"

    assert result.web_sources == []

    agent.executor.execute.assert_called_once()


@patch("agent.agent.client")
def test_run_executes_web_search(mock_client):
    agent = create_agent()

    agent.decide_tools = Mock(
        return_value=AgentDecision(
            tool_calls=[
                AgentToolCall(
                    tool=ToolName.WEB_SEARCH,
                    query="recent Dostoevsky scholarship",
                )
            ]
        )
    )

    agent.executor.execute.return_value = WebSearchResult(
        answer="Recent research discusses Dostoevsky.",
        sources=[
            WebSource(
                number=1,
                title="Test Source",
                url="https://example.com",
            )
        ],
    )

    mock_client.responses.create.return_value.output_text = "Final answer"

    result = agent.run("What are recent discussions about Dostoevsky?")

    assert result.answer == "Final answer"

    assert result.corpus_sources == []

    assert len(result.web_sources) == 1
    assert result.web_sources[0].title == "Test Source"
    assert result.web_sources[0].url == "https://example.com"

    agent.executor.execute.assert_called_once()


@patch("agent.agent.client")
def test_run_executes_multiple_tools(mock_client):
    agent = create_agent()

    corpus_call = AgentToolCall(
        tool=ToolName.CORPUS_SEARCH,
        query="Raskolnikov extraordinary people",
    )

    web_call = AgentToolCall(
        tool=ToolName.WEB_SEARCH,
        query="modern scholarship Raskolnikov extraordinary people",
    )

    agent.decide_tools = Mock(
        return_value=AgentDecision(
            tool_calls=[corpus_call, web_call]
        )
    )

    agent.executor.execute.side_effect = [
        CorpusSearchResult(
            sources=[
                CorpusSource(
                    number=1,
                    book_id="crime_and_punishment",
                    chapter=None,
                    section="I",
                    chunk_index=3,
                    text="Test passage",
                )
            ]
        ),
        WebSearchResult(
            answer="Modern scholarly interpretation.",
            sources=[
                WebSource(
                    number=1,
                    title="Test Source",
                    url="https://example.com",
                )
            ],
        ),
    ]

    mock_client.responses.create.return_value.output_text = "Combined answer"

    result = agent.run(
        "What does Raskolnikov believe and how do modern scholars interpret it?"
    )

    assert result.answer == "Combined answer"

    assert len(result.corpus_sources) == 1
    assert result.corpus_sources[0].book_id == "crime_and_punishment"

    assert len(result.web_sources) == 1
    assert result.web_sources[0].title == "Test Source"

    assert agent.executor.execute.call_count == 2