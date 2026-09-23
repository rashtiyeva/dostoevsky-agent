from pathlib import Path

from chunking.chunker import chunk_section
from chunking.models import Chunk
from ingestion.cleaner import clean_text
from ingestion.extractor import extract_book_text
from ingestion.loader import load_document
from ingestion.parser import parse_sections

BOOKS_DIR = Path("data/books")


def load_corpus_chunks(
    books_dir: Path = BOOKS_DIR,
) -> list[Chunk]:
    chunks: list[Chunk] = []

    for book_dir in sorted(books_dir.iterdir()):
        if not book_dir.is_dir():
            continue

        document = load_document(book_dir)
        book_text = extract_book_text(document)
        cleaned_text = clean_text(book_text)

        sections = parse_sections(
            cleaned_text,
            has_section_titles=document.has_section_titles,
        )

        for section in sections:
            chunks.extend(
                chunk_section(
                    section=section,
                    book_id=document.book_id,
                )
            )

    return chunks