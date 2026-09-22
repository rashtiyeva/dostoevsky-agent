from unittest.mock import MagicMock, patch

from embeddings.embedder import EmbeddingModel


@patch("embeddings.embedder.SentenceTransformer")
def test_embed_returns_normalized_list(mock_sentence_transformer):
    mock_model = MagicMock()
    mock_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
        0.3,
    ]
    mock_sentence_transformer.return_value = mock_model

    embedding_model = EmbeddingModel()

    result = embedding_model.embed("test text")

    assert result == [
        0.1,
        0.2,
        0.3,
    ]

    mock_sentence_transformer.assert_called_once_with(
        "BAAI/bge-m3"
    )
    mock_model.encode.assert_called_once_with(
        "test text",
        normalize_embeddings=True,
    )


@patch("embeddings.embedder.SentenceTransformer")
def test_embed_batch_returns_normalized_lists(
    mock_sentence_transformer,
):
    mock_model = MagicMock()
    mock_model.encode.return_value.tolist.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]
    mock_sentence_transformer.return_value = mock_model

    embedding_model = EmbeddingModel()

    result = embedding_model.embed_batch(
        [
            "first text",
            "second text",
        ]
    )

    assert result == [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    mock_sentence_transformer.assert_called_once_with(
        "BAAI/bge-m3"
    )
    mock_model.encode.assert_called_once_with(
        [
            "first text",
            "second text",
        ],
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False,
    )