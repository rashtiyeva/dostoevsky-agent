from sentence_transformers import CrossEncoder

from retrieval.models import RetrievedChunk

RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"


class Reranker:
    def __init__(self) -> None:
        self.model = CrossEncoder(RERANKER_MODEL_NAME)

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        pairs = [
            (query, chunk.text)
            for chunk in chunks
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            RetrievedChunk(
                text=chunk.text,
                score=float(score),
                book_id=chunk.book_id,
                part=chunk.part,
                part_title=chunk.part_title,
                book=chunk.book,
                chapter=chunk.chapter,
                chapter_title=chunk.chapter_title,
                section=chunk.section,
                section_title=chunk.section_title,
                chunk_index=chunk.chunk_index,
                content_type=chunk.content_type,
            )
            for chunk, score in ranked[:limit]
        ]