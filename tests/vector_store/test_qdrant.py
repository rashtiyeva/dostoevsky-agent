from pathlib import Path

from chunking.chunker import chunk_section
from embeddings.embedder import EmbeddingModel
from embeddings.input_builder import build_embedding_input
from ingestion.cleaner import clean_text
from ingestion.extractor import extract_book_text
from ingestion.loader import load_document
from ingestion.parser import parse_sections
from vector_store.point_mapper import build_point_id
from vector_store.qdrant_store import (
    COLLECTION_NAME,
    QdrantStore,
)


BOOK_DIR = Path("data/books/crime_and_punishment")


def main() -> None:
    document = load_document(BOOK_DIR)

    book_text = extract_book_text(document)
    cleaned_text = clean_text(book_text)

    sections = parse_sections(
        cleaned_text,
        has_section_titles=document.has_section_titles,
    )

    chunks = chunk_section(
        section=sections[0],
        book_id=document.book_id,
    )

    chunk = chunks[0]

    embedding_input = build_embedding_input(chunk)

    embedding_model = EmbeddingModel()
    embedding = embedding_model.embed(embedding_input)

    store = QdrantStore()
    store.create_collection()

    store.upsert_chunk(
        chunk=chunk,
        embedding=embedding,
    )

    point_id = build_point_id(chunk)

    points = store.client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[point_id],
        with_payload=True,
        with_vectors=True,
    )

    point = points[0]

    print(f"Point ID: {point.id}")
    print(f"Vector dimensions: {len(point.vector)}")
    print(f"Book: {point.payload['book_id']}")
    print(f"Chunk index: {point.payload['chunk_index']}")
    print(f"Text: {point.payload['text'][:200]}...")


if __name__ == "__main__":
    main()