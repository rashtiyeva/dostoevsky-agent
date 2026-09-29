from unittest.mock import Mock

from retrieval.models import RetrievedChunk
from tools.corpus_search import CorpusSearchTool


def test_corpus_search_returns_structured_sources():
    tool = CorpusSearchTool.__new__(CorpusSearchTool)
    tool.retriever = Mock()

    tool.retriever.retrieve.return_value = [
        RetrievedChunk(
            text="Test passage",
            score=0.9,
            book_id="crime_and_punishment",
            part=None,
            part_title=None,
            book=None,
            chapter=None,
            chapter_title=None,
            section="I",
            section_title=None,
            chunk_index=3,
            content_type="text",
        )
    ]

    result = tool.search("test query")

    assert len(result.sources) == 1
    assert result.sources[0].number == 1
    assert result.sources[0].book_id == "crime_and_punishment"
    assert result.sources[0].text == "Test passage"