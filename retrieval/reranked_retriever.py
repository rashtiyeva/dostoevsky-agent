from retrieval.hybrid_retriever import HybridRetriever
from retrieval.models import RetrievedChunk
from retrieval.reranker import Reranker


class RerankedRetriever:
    def __init__(self) -> None:
        self.hybrid_retriever = HybridRetriever()
        self.reranker = Reranker()

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        candidate_limit: int = 20,
    ) -> list[RetrievedChunk]:
        candidates = self.hybrid_retriever.retrieve(
            query=query,
            limit=candidate_limit,
            candidate_limit=candidate_limit,
        )

        return self.reranker.rerank(
            query=query,
            chunks=candidates,
            limit=limit,
        )