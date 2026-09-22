from chunking.models import Chunk
from vector_store.point_mapper import (
    build_point_id,
    to_point,
)


def create_chunk() -> Chunk:
    return Chunk(
        book_id="crime_and_punishment",
        part="Часть первая",
        part_title=None,
        book=None,
        chapter="Глава I",
        chapter_title=None,
        section="I",
        section_title=None,
        text="В начале июля...",
        chunk_index=0,
        content_type="main_text",
    )


def test_build_point_id_is_deterministic():
    chunk = create_chunk()

    first_id = build_point_id(chunk)
    second_id = build_point_id(chunk)

    assert first_id == second_id


def test_different_chunks_have_different_ids():
    first_chunk = create_chunk()
    second_chunk = create_chunk()
    second_chunk.text = "Другой текст"

    assert build_point_id(first_chunk) != build_point_id(second_chunk)


def test_to_point():
    chunk = create_chunk()
    embedding = [0.1, 0.2, 0.3]

    point = to_point(
        chunk=chunk,
        embedding=embedding,
    )

    assert point.id == build_point_id(chunk)
    assert point.vector == embedding

    assert point.payload["book_id"] == "crime_and_punishment"
    assert point.payload["chapter"] == "Глава I"
    assert point.payload["text"] == "В начале июля..."
    assert point.payload["chunk_index"] == 0