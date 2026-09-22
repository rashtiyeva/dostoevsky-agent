from pathlib import Path

from chunking.chunker import chunk_section
from embeddings.embedder import EmbeddingModel
from embeddings.input_builder import build_embedding_input
from ingestion.cleaner import clean_text
from ingestion.extractor import extract_book_text
from ingestion.loader import load_document
from ingestion.parser import parse_sections
from vector_store.qdrant_store import QdrantStore

BOOKS_DIR = Path("data/books")


class CorpusIndexer:
    def __init__(
        self,
        books_dir: Path = BOOKS_DIR,
    ) -> None:
        self.books_dir = books_dir
        self.embedding_model = EmbeddingModel()
        self.store = QdrantStore()

    def index(self) -> None:
        self.store.recreate_collection()

        total_chunks = 0

        for book_dir in sorted(self.books_dir.iterdir()):
            if not book_dir.is_dir():
                continue

            print(f"Indexing: {book_dir.name}")

            document = load_document(book_dir)

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

            if not chunks:
                print(
                    f"No chunks found for {document.book_id}, "
                    "skipping."
                )
                continue

            embedding_inputs = [
                build_embedding_input(chunk)
                for chunk in chunks
            ]

            embeddings = self.embedding_model.embed_batch(
                embedding_inputs
            )

            self.store.upsert_chunks(
                chunks=chunks,
                embeddings=embeddings,
            )

            total_chunks += len(chunks)

            print(
                f"Indexed {len(chunks)} chunks "
                f"from {document.book_id}"
            )

        print(
            f"Done. Total indexed chunks: {total_chunks}"
        )