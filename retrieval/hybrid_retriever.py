from retrieval.bm25_retriever import BM25Retriever
from retrieval.corpus_loader import load_corpus_chunks
from retrieval.models import RetrievedChunk
from retrieval.retriever import DenseRetriever
from retrieval.rrf import reciprocal_rank_fusion


class HybridRetriever:
    def __init__(self) -> None:
        chunks = load_corpus_chunks()

        self.dense_retriever = DenseRetriever()
        self.bm25_retriever = BM25Retriever(chunks)

    def retrieve(
        self,
        query: str,
        limit: int = 10,
        candidate_limit: int = 20,
    ) -> list[RetrievedChunk]:
        dense_results = self.dense_retriever.retrieve(
            query=query,
            limit=candidate_limit,
        )

        bm25_results = self.bm25_retriever.retrieve(
            query=query,
            limit=candidate_limit,
        )

        return reciprocal_rank_fusion(
            rankings=[
                dense_results,
                bm25_results,
            ],
            limit=limit,
        )