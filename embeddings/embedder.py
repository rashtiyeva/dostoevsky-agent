from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"


class EmbeddingModel:
    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

    def embed(self, text: str) -> list[float]:
        embedding = self.model.encode(text)

        return embedding.tolist()