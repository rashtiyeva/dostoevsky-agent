from pathlib import Path

from chunking.chunker import chunk_section
from embeddings.embedder import EmbeddingModel
from embeddings.input_builder import build_embedding_input
from ingestion.cleaner import clean_text
from ingestion.extractor import extract_book_text
from ingestion.loader import load_document
from ingestion.parser import parse_sections


BOOK_DIR = Path("data/books/crime_and_punishment")


def main() -> None:
    document = load_document(BOOK_DIR)

    book_text = extract_book_text(document)
    cleaned_text = clean_text(book_text)

    sections = parse_sections(
        cleaned_text,
        has_section_titles=document.has_section_titles,
    )

    chunks = []

    for section in sections:
        chunks.extend(
            chunk_section(
                section=section,
                book_id=document.book_id,
            )
        )

        if len(chunks) >= 3:
            break

    chunks = chunks[:3]

    inputs = [
        build_embedding_input(chunk)
        for chunk in chunks
    ]

    model = EmbeddingModel()
    embeddings = model.embed_batch(inputs)

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings),
        start=1,
    ):
        print(f"\nCHUNK {index}")
        print("=" * 80)
        print(f"Text: {chunk.text[:200]}...")
        print(f"Embedding dimensions: {len(embedding)}")


if __name__ == "__main__":
    main()