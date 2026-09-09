from ingestion.chunker import (
    chunk_chapter,
    split_into_paragraphs,
    split_large_paragraph,
)
from ingestion.models import Chapter


def test_split_into_paragraphs():
    chapter = Chapter(
        part=1,
        chapter=1,
        text="First paragraph.\n\nSecond paragraph.\n\nThird paragraph.",
    )

    paragraphs = split_into_paragraphs(chapter)

    assert paragraphs == [
        "First paragraph.",
        "Second paragraph.",
        "Third paragraph.",
    ]


def test_split_into_paragraphs_removes_empty_paragraphs():
    chapter = Chapter(
        part=1,
        chapter=1,
        text="First paragraph.\n\n\n\nSecond paragraph.",
    )

    paragraphs = split_into_paragraphs(chapter)

    assert paragraphs == [
        "First paragraph.",
        "Second paragraph.",
    ]


def test_chunk_chapter_creates_single_chunk_when_text_fits():
    chapter = Chapter(
        part=1,
        chapter=1,
        text="First paragraph.\n\nSecond paragraph.",
    )

    chunks = chunk_chapter(
        chapter=chapter,
        book_id="crime-and-punishment",
        max_chars=1000,
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.book_id == "crime-and-punishment"
    assert chunk.part == 1
    assert chunk.chapter == 1
    assert chunk.chunk_index == 0
    assert chunk.text == "First paragraph.\n\nSecond paragraph."


def test_chunk_chapter_creates_multiple_chunks_when_limit_exceeded():
    chapter = Chapter(
        part=1,
        chapter=1,
        text="AAAAA\n\nBBBBB\n\nCCCCC",
    )

    chunks = chunk_chapter(
        chapter=chapter,
        book_id="crime-and-punishment",
        max_chars=10,
    )

    assert len(chunks) == 2

    assert chunks[0].text == "AAAAA\n\nBBBBB"
    assert chunks[0].chunk_index == 0

    assert chunks[1].text == "CCCCC"
    assert chunks[1].chunk_index == 1


def test_chunk_indexes_are_sequential():
    chapter = Chapter(
        part=1,
        chapter=2,
        text="AAAAA\n\nBBBBB\n\nCCCCC",
    )

    chunks = chunk_chapter(
        chapter=chapter,
        book_id="crime-and-punishment",
        max_chars=5,
    )

    assert len(chunks) == 3

    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2


def test_chunk_chapter_preserves_metadata():
    chapter = Chapter(
        part=2,
        chapter=4,
        text="Some paragraph.",
    )

    chunks = chunk_chapter(
        chapter=chapter,
        book_id="the-idiot",
    )

    chunk = chunks[0]

    assert chunk.book_id == "the-idiot"
    assert chunk.part == 2
    assert chunk.chapter == 4


def test_chunk_chapter_returns_empty_list_for_empty_text():
    chapter = Chapter(
        part=1,
        chapter=1,
        text="",
    )

    chunks = chunk_chapter(
        chapter=chapter,
        book_id="crime-and-punishment",
    )

    assert chunks == []

def test_split_large_paragraph():
    paragraph = "a" * 6000

    parts = split_large_paragraph(
        paragraph,
        max_chars=2500,
    )

    assert len(parts) == 3
    assert len(parts[0]) == 2500
    assert len(parts[1]) == 2500
    assert len(parts[2]) == 1000