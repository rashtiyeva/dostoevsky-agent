from generation.prompt_builder import build_rag_prompt
from retrieval.models import RetrievedChunk


def make_chunk(text: str, section: str) -> RetrievedChunk:
    return RetrievedChunk(
        text=text,
        score=1.0,
        book_id="crime_and_punishment",
        part=None,
        part_title=None,
        book=None,
        chapter=None,
        chapter_title=None,
        section=section,
        section_title=None,
        chunk_index=1,
        content_type="text",
    )


def test_build_rag_prompt_contains_query_and_chunks():
    chunks = [
        make_chunk("First passage", "I"),
        make_chunk("Second passage", "II"),
    ]

    prompt = build_rag_prompt(
        query="Почему Раскольников совершил убийство?",
        chunks=chunks,
    )

    assert "Почему Раскольников совершил убийство?" in prompt
    assert "First passage" in prompt
    assert "Second passage" in prompt
    assert "[1]" in prompt
    assert "[2]" in prompt


def test_build_rag_prompt_contains_grounding_instructions():
    prompt = build_rag_prompt(
        query="Test question",
        chunks=[],
    )

    assert "using only the provided excerpts" in prompt
    assert "provided sources are insufficient" in prompt
    assert "Do not invent information" in prompt
    assert "same language as the user's question" in prompt