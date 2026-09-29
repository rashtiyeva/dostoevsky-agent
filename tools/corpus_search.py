from retrieval.reranked_retriever import RerankedRetriever
from tools.models import CorpusSearchResult, CorpusSource


class CorpusSearchTool:
    def __init__(self) -> None:
        self.retriever = RerankedRetriever()

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> CorpusSearchResult:
        chunks = self.retriever.retrieve(
            query=query,
            limit=limit,
        )

        sources = [
            CorpusSource(
                number=index,
                book_id=chunk.book_id,
                chapter=chunk.chapter,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )
            for index, chunk in enumerate(chunks, start=1)
        ]

        return CorpusSearchResult(
            sources=sources,
        )