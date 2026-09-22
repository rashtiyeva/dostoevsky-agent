from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from chunking.models import Chunk
from vector_store.point_mapper import to_point

COLLECTION_NAME = "dostoevsky_chunks"
VECTOR_SIZE = 1024
QDRANT_BATCH_SIZE = 100


class QdrantStore:
    def __init__(self, url: str = "http://localhost:6333") -> None:
        self.client = QdrantClient(url=url)

    def create_collection(self) -> None:
        if self.client.collection_exists(COLLECTION_NAME):
            return

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def recreate_collection(self) -> None:
        if self.client.collection_exists(COLLECTION_NAME):
            self.client.delete_collection(COLLECTION_NAME)

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def upsert_chunk(
        self,
        chunk: Chunk,
        embedding: list[float],
    ) -> None:
        point = to_point(
            chunk=chunk,
            embedding=embedding,
        )

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point],
        )

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings must have the same length."
            )

        if not chunks:
            return

        points = [
            to_point(
                chunk=chunk,
                embedding=embedding,
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        for start in range(0, len(points), QDRANT_BATCH_SIZE):
            batch = points[start:start + QDRANT_BATCH_SIZE]

            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch,
            )

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ):
        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        return response.points