from generation.citation_mapper import map_citations
from retrieval.models import RetrievedChunk


def make_chunk(chunk_index: int) -> RetrievedChunk:
    return RetrievedChunk(
        text=f"Text {chunk_index}",
        score=1.0,
        book_id="crime_and_punishment",
        part=None,
        part_title=None,
        book=None,
        chapter=None,
        chapter_title=None,
        section="I",
        section_title=None,
        chunk_index=chunk_index,
        content_type="text",
    )


def test_map_citations_maps_used_numbers_to_chunks():
    chunks = [
        make_chunk(1),
        make_chunk(2),
        make_chunk(3),
    ]

    citations = map_citations(
        answer="First claim [1]. Another claim [3].",
        chunks=chunks,
    )

    assert len(citations) == 2

    assert citations[0].number == 1
    assert citations[0].chunk_index == 1
    assert citations[0].text == "Text 1"

    assert citations[1].number == 3
    assert citations[1].chunk_index == 3
    assert citations[1].text == "Text 3"


def test_map_citations_ignores_invalid_numbers():
    chunks = [make_chunk(1)]

    citations = map_citations(
        answer="Valid [1]. Invalid [99].",
        chunks=chunks,
    )

    assert len(citations) == 1
    assert citations[0].number == 1


def test_map_citations_removes_duplicates():
    chunks = [make_chunk(1)]

    citations = map_citations(
        answer="First [1]. Again [1].",
        chunks=chunks,
    )

    assert len(citations) == 1