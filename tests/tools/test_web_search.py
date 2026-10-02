from unittest.mock import AsyncMock, Mock

import pytest

from tools.web_search import WebSearchTool


@pytest.mark.anyio
async def test_web_search_returns_answer_and_sources():
    tool = WebSearchTool.__new__(WebSearchTool)
    tool.client = Mock()

    annotation = Mock()
    annotation.type = "url_citation"
    annotation.title = "Test Source"
    annotation.url = "https://example.com/article"

    content = Mock()
    content.type = "output_text"
    content.annotations = [annotation]

    output = Mock()
    output.type = "message"
    output.content = [content]

    response = Mock()
    response.output_text = "Test answer"
    response.output = [output]

    tool.client.responses.create = AsyncMock(
        return_value=response
    )

    result = await tool.search("test query")

    assert result.answer == "Test answer"
    assert len(result.sources) == 1
    assert result.sources[0].number == 1
    assert result.sources[0].title == "Test Source"
    assert result.sources[0].url == "https://example.com/article"