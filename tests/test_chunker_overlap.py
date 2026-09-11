import pytest

from chunking.chunker import (
    chunk_section,
    count_tokens,
    get_overlap_text,
)
from ingestion.models import Section


def make_section(text: str) -> Section:
    return Section(
        part="Часть первая",
        part_title="Part title",
        book="Книга первая",
        chapter="Глава первая",
        chapter_title="Chapter title",
        section="I",
        text=text,
    )


def test_overlap_zero_adds_no_duplicated_context():
    section = make_section(
        "First sentence. Second sentence.\n\n"
        "Third sentence. Fourth sentence."
    )

    chunks = chunk_section(
        section=section,
        book_id="test-book",
        max_tokens=8,
        overlap_tokens=0,
    )

    assert len(chunks) >= 2

    first_chunk_sentences = chunks[0].text.split()
    second_chunk_text = chunks[1].text

    assert chunks[0].text != chunks[1].text
    assert not second_chunk_text.startswith(chunks[0].text)



def test_normal_overlap_appears_at_start_of_next_chunk():
    section = make_section(
        "First sentence. Second sentence. Third sentence.\n\n"
        "Fourth sentence. Fifth sentence."
    )

    chunks = chunk_section(
        section=section,
        book_id="test-book",
        max_tokens=14,
        overlap_tokens=4,
    )

    assert len(chunks) == 2

    assert chunks[1].text.startswith(
        "Third sentence."
    )

    assert "Fourth sentence." in chunks[1].text
    assert "Fifth sentence." in chunks[1].text

def test_normal_overlap_appears_at_start_of_next_chunk():
    first_paragraph = (
        "First sentence. "
        "Second sentence. "
        "Third sentence."
    )

    second_paragraph = (
        "Fourth sentence. "
        "Fifth sentence."
    )

    overlap_sentence = "Third sentence."

    second_paragraph_tokens = count_tokens(
        second_paragraph
    )

    overlap_tokens = count_tokens(
        overlap_sentence
    )

    max_tokens = count_tokens(
        f"{overlap_sentence}\n\n{second_paragraph}"
    )

    section = make_section(
        f"{first_paragraph}\n\n{second_paragraph}"
    )

    chunks = chunk_section(
        section=section,
        book_id="test-book",
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
    )

    assert len(chunks) == 2

    assert chunks[1].text.startswith(
        overlap_sentence
    )

    assert count_tokens(chunks[1].text) <= max_tokens

def test_overlap_respects_overlap_token_limit():
    previous_text = (
        "First sentence. "
        "Second sentence. "
        "Third sentence. "
        "Fourth sentence."
    )

    overlap = get_overlap_text(
        text=previous_text,
        next_text="Next chunk text.",
        overlap_tokens=75,
        max_tokens=600,
    )

    assert count_tokens(overlap) <= 75


def test_all_final_chunks_respect_max_token_limit_including_overlap():
    text = "\n\n".join(
        [
            "Sentence one. Sentence two. Sentence three."
            for _ in range(20)
        ]
    )

    section = make_section(text)

    chunks = chunk_section(
        section=section,
        book_id="test-book",
        max_tokens=30,
        overlap_tokens=8,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert count_tokens(chunk.text) <= 30


def test_sentence_too_large_for_overlap_is_not_cut():
    long_sentence = "word " * 100

    overlap = get_overlap_text(
        text=long_sentence,
        next_text="Next text.",
        overlap_tokens=10,
        max_tokens=100,
    )

    assert overlap == ""


def test_negative_overlap_tokens_raises_value_error():
    section = make_section(
        "Some text."
    )

    with pytest.raises(
        ValueError,
        match="overlap_tokens cannot be negative",
    ):
        chunk_section(
            section=section,
            book_id="test-book",
            max_tokens=600,
            overlap_tokens=-1,
        )


def test_overlap_equal_to_max_tokens_raises_value_error():
    section = make_section(
        "Some text."
    )

    with pytest.raises(
        ValueError,
        match="overlap_tokens must be smaller than max_tokens",
    ):
        chunk_section(
            section=section,
            book_id="test-book",
            max_tokens=100,
            overlap_tokens=100,
        )


def test_overlap_greater_than_max_tokens_raises_value_error():
    section = make_section(
        "Some text."
    )

    with pytest.raises(
        ValueError,
        match="overlap_tokens must be smaller than max_tokens",
    ):
        chunk_section(
            section=section,
            book_id="test-book",
            max_tokens=100,
            overlap_tokens=101,
        )


def test_overlap_does_not_change_metadata():
    section = make_section(
        "First sentence. Second sentence.\n\n"
        "Third sentence. Fourth sentence.\n\n"
        "Fifth sentence. Sixth sentence."
    )

    chunks = chunk_section(
        section=section,
        book_id="crime_and_punishment",
        max_tokens=12,
        overlap_tokens=4,
    )

    assert len(chunks) >= 2

    for chunk in chunks:
        assert chunk.book_id == "crime_and_punishment"
        assert chunk.part == "Часть первая"
        assert chunk.part_title == "Part title"
        assert chunk.book == "Книга первая"
        assert chunk.chapter == "Глава первая"
        assert chunk.chapter_title == "Chapter title"
        assert chunk.section == "I"
        assert chunk.content_type == "main_text"


def test_first_chunk_has_no_overlap_before_it():
    section = make_section(
        "First sentence. Second sentence.\n\n"
        "Third sentence. Fourth sentence."
    )

    chunks = chunk_section(
        section=section,
        book_id="test-book",
        max_tokens=12,
        overlap_tokens=4,
    )

    assert chunks[0].text.startswith("First sentence.")


def test_chunk_indexes_remain_sequential_with_overlap():
    section = make_section(
        "\n\n".join(
            [
                "First sentence. Second sentence.",
                "Third sentence. Fourth sentence.",
                "Fifth sentence. Sixth sentence.",
                "Seventh sentence. Eighth sentence.",
            ]
        )
    )

    chunks = chunk_section(
        section=section,
        book_id="test-book",
        max_tokens=12,
        overlap_tokens=4,
    )

    assert [
        chunk.chunk_index
        for chunk in chunks
    ] == list(range(len(chunks)))


def test_empty_section_returns_no_chunks_with_overlap_enabled():
    section = make_section("")

    chunks = chunk_section(
        section=section,
        book_id="test-book",
        max_tokens=600,
        overlap_tokens=75,
    )

    assert chunks == []


def test_overlap_uses_tail_of_previous_chunk_not_beginning():
    previous_text = (
        "Beginning sentence. "
        "Middle sentence. "
        "Final sentence."
    )

    overlap = get_overlap_text(
        text=previous_text,
        next_text="Next chunk.",
        overlap_tokens=5,
        max_tokens=50,
    )

    assert "Beginning sentence." not in overlap
    assert overlap.endswith("Final sentence.")


def test_overlap_is_not_added_when_it_would_make_next_chunk_too_large():
    previous_text = (
        "Previous ending sentence."
    )

    next_text = "word " * 19

    overlap = get_overlap_text(
        text=previous_text,
        next_text=next_text,
        overlap_tokens=10,
        max_tokens=20,
    )

    combined = (
        f"{overlap}\n\n{next_text}"
        if overlap
        else next_text
    )

    assert count_tokens(combined) <= 20


def test_overlap_preserves_sentence_order():
    previous_text = (
        "Sentence A. "
        "Sentence B. "
        "Sentence C."
    )

    overlap = get_overlap_text(
        text=previous_text,
        next_text="Next.",
        overlap_tokens=10,
        max_tokens=50,
    )

    if "Sentence B." in overlap:
        assert overlap.index("Sentence B.") < overlap.index("Sentence C.")