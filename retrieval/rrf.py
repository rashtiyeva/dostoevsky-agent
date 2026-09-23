from collections import defaultdict
from dataclasses import replace

from retrieval.models import RetrievedChunk

RRF_K = 60


def reciprocal_rank_fusion(
    rankings: list[list[RetrievedChunk]],
    limit: int = 10,
) -> list[RetrievedChunk]:
    scores: dict[str, float] = defaultdict(float)
    chunks: dict[str, RetrievedChunk] = {}

    for ranking in rankings:
        for rank, chunk in enumerate(ranking, start=1):
            chunk_id = build_chunk_id(chunk)

            scores[chunk_id] += 1 / (RRF_K + rank)
            chunks[chunk_id] = chunk

    ranked_ids = sorted(
        scores,
        key=lambda chunk_id: scores[chunk_id],
        reverse=True,
    )[:limit]

    return [
        replace(
            chunks[chunk_id],
            score=scores[chunk_id],
        )
        for chunk_id in ranked_ids
    ]


def build_chunk_id(chunk: RetrievedChunk) -> str:
    return "|".join(
        [
            chunk.book_id,
            chunk.part or "",
            chunk.book or "",
            chunk.chapter or "",
            chunk.section or "",
            str(chunk.chunk_index),
            chunk.text,
        ]
    )