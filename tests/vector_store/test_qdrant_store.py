from unittest.mock import MagicMock, patch

from qdrant_client.models import Distance

from chunking.models import Chunk
from vector_store.point_mapper import build_point_id
from vector_store.qdrant_store import (
    COLLECTION_NAME,
    VECTOR_SIZE,
    QdrantStore,
)


@patch("vector_store.qdrant_store.QdrantClient")
def test_create_collection(mock_qdrant_client):
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False
    mock_qdrant_client.return_value = mock_client

    store = QdrantStore()

    store.create_collection()

    mock_client.collection_exists.assert_called_once_with(
        COLLECTION_NAME
    )

    mock_client.create_collection.assert_called_once()

    call = mock_client.create_collection.call_args

    assert call.kwargs["collection_name"] == COLLECTION_NAME
    assert call.kwargs["vectors_config"].size == VECTOR_SIZE
    assert call.kwargs["vectors_config"].distance == Distance.COSINE


@patch("vector_store.qdrant_store.QdrantClient")
def test_create_collection_does_nothing_when_collection_exists(
    mock_qdrant_client,
):
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    mock_qdrant_client.return_value = mock_client

    store = QdrantStore()

    store.create_collection()

    mock_client.create_collection.assert_not_called()


def test_upsert_chunk():
    client = MagicMock()

    store = QdrantStore()
    store.client = client

    chunk = Chunk(
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

    embedding = [0.1, 0.2, 0.3]

    store.upsert_chunk(
        chunk=chunk,
        embedding=embedding,
    )

    client.upsert.assert_called_once()

    call = client.upsert.call_args

    assert call.kwargs["collection_name"] == COLLECTION_NAME

    point = call.kwargs["points"][0]

    assert point.id == build_point_id(chunk)
    assert point.vector == embedding

    assert point.payload["book_id"] == "crime_and_punishment"
    assert point.payload["chapter"] == "Глава I"
    assert point.payload["text"] == "В начале июля..."
    assert point.payload["chunk_index"] == 0