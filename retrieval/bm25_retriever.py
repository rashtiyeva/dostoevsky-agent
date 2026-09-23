import re

from rank_bm25 import BM25Okapi

from chunking.models import Chunk
from retrieval.models import RetrievedChunk

TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.casefold())


class BM25Retriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks

        tokenized_corpus = [
            tokenize(chunk.text)
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(
        self,
        query: str,
        limit: int = 10,
    ) -> list[RetrievedChunk]:
        if not self.chunks:
            return []

        tokenized_query = tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:limit]

        return [
            self._to_retrieved_chunk(
                chunk=self.chunks[index],
                score=float(scores[index]),
            )
            for index in ranked_indices
        ]

    @staticmethod
    def _to_retrieved_chunk(
        chunk: Chunk,
        score: float,
    ) -> RetrievedChunk:
        return RetrievedChunk(
            text=chunk.text,
            score=score,
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