from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_BATCH_SIZE = 32


class EmbeddingModel:
    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

    def embed(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()