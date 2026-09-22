from embeddings.embedder import EmbeddingModel
from retrieval.models import RetrievedChunk
from vector_store.qdrant_store import QdrantStore


class DenseRetriever:
    def __init__(self) -> None:
        self.embedding_model = EmbeddingModel()
        self.store = QdrantStore()

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        query_vector = self.embedding_model.embed(query)

        points = self.store.search(
            query_vector=query_vector,
            limit=limit,
        )

        return [
            RetrievedChunk(
                text=point.payload["text"],
                score=point.score,
                book_id=point.payload["book_id"],
                part=point.payload.get("part"),
                part_title=point.payload.get("part_title"),
                book=point.payload.get("book"),
                chapter=point.payload.get("chapter"),
                chapter_title=point.payload.get("chapter_title"),
                section=point.payload.get("section"),
                section_title=point.payload.get("section_title"),
                chunk_index=point.payload["chunk_index"],
                content_type=point.payload["content_type"],
            )
            for point in points
        ]