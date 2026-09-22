from uuid import NAMESPACE_URL, uuid5

from qdrant_client.models import PointStruct

from chunking.models import Chunk


def build_point_id(chunk: Chunk) -> str:
    source = "|".join(
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

    return str(
        uuid5(
            NAMESPACE_URL,
            source,
        )
    )


def to_point(
    chunk: Chunk,
    embedding: list[float],
) -> PointStruct:
    return PointStruct(
        id=build_point_id(chunk),
        vector=embedding,
        payload={
            "book_id": chunk.book_id,
            "part": chunk.part,
            "part_title": chunk.part_title,
            "book": chunk.book,
            "chapter": chunk.chapter,
            "chapter_title": chunk.chapter_title,
            "section": chunk.section,
            "section_title": chunk.section_title,
            "text": chunk.text,
            "chunk_index": chunk.chunk_index,
            "content_type": chunk.content_type,
        },
    )