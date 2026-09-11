from pathlib import Path

import pytest

from chunking.chunker import chunk_section
from ingestion.cleaner import clean_text
from ingestion.extractor import extract_book_text
from ingestion.loader import load_document
from ingestion.parser import parse_sections

BOOKS_DIR = Path("data/books")
MAX_CHARS = 2500


def get_book_directories() -> list[Path]:
    return [
        path
        for path in BOOKS_DIR.iterdir()
        if path.is_dir()
        and (path / "book.txt").exists()
        and (path / "metadata.json").exists()
    ]


@pytest.mark.parametrize(
    "book_dir",
    get_book_directories(),
    ids=lambda path: path.name,
)
def test_real_book_pipeline(book_dir: Path):
    document = load_document(book_dir)

    book_text = extract_book_text(document)

    cleaned_text = clean_text(book_text)

    sections = parse_sections(cleaned_text)

    assert sections, (
        f"No sections were parsed for book: {document.title}"
    )

    all_chunks = []

    for section in sections:
        chunks = chunk_section(
            section=section,
            book_id=document.book_id,
            max_chars=MAX_CHARS,
        )

        all_chunks.extend(chunks)

        for chunk in chunks:
            # Chunk must contain text
            assert chunk.text.strip(), (
                f"Empty chunk found in {document.title}"
            )

            # Chunk must respect our current character limit
            assert len(chunk.text) <= MAX_CHARS, (
                f"Chunk exceeds {MAX_CHARS} characters "
                f"in {document.title}: "
                f"{len(chunk.text)} characters"
            )

            # Book metadata must be preserved
            assert chunk.book_id == document.book_id

            # Structural metadata must be preserved
            assert chunk.part == section.part
            assert chunk.part_title == section.part_title

            assert chunk.book == section.book

            assert chunk.chapter == section.chapter
            assert chunk.chapter_title == section.chapter_title

            assert chunk.section == section.section

            assert chunk.content_type == "main_text"

    assert all_chunks, (
        f"No chunks were created for book: {document.title}"
    )

    print_book_summary(
        document=document,
        sections=sections,
        chunks=all_chunks,
    )


def print_book_summary(
    document,
    sections,
    chunks,
) -> None:
    print()
    print("=" * 80)

    print(f"BOOK: {document.title}")
    print(f"BOOK ID: {document.book_id}")
    print(f"SECTIONS: {len(sections)}")
    print(f"CHUNKS: {len(chunks)}")

    print("-" * 80)

    first_section = sections[0]

    print("FIRST SECTION")
    print(f"part: {first_section.part}")
    print(f"part_title: {first_section.part_title}")
    print(f"book: {first_section.book}")
    print(f"chapter: {first_section.chapter}")
    print(f"chapter_title: {first_section.chapter_title}")
    print(f"section: {first_section.section}")

    print()
    print("FIRST SECTION TEXT:")
    print(first_section.text[:300])

    print("-" * 80)

    last_section = sections[-1]

    print("LAST SECTION")
    print(f"part: {last_section.part}")
    print(f"part_title: {last_section.part_title}")
    print(f"book: {last_section.book}")
    print(f"chapter: {last_section.chapter}")
    print(f"chapter_title: {last_section.chapter_title}")
    print(f"section: {last_section.section}")

    print()
    print("LAST SECTION TEXT:")
    print(last_section.text[-300:])

    print("-" * 80)

    print("FIRST CHUNK:")
    print(chunks[0].text[:300])

    print("-" * 80)

    middle_chunk = chunks[len(chunks) // 2]

    print("MIDDLE CHUNK:")
    print(middle_chunk.text[:300])

    print("-" * 80)

    print("LAST CHUNK:")
    print(chunks[-1].text[-300:])

    print("=" * 80)