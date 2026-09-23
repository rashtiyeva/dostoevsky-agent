from dataclasses import dataclass
from typing import Protocol

from evaluation.retrieval.models import RetrievalEvaluationCase
from retrieval.models import RetrievedChunk
from retrieval.retriever import DenseRetriever


class Retriever(Protocol):
    def retrieve(
        self,
        query: str,
        limit: int = 10,
    ) -> list[RetrievedChunk]:
        ...


@dataclass
class RetrievalEvaluationResult:
    query: str
    rank: int | None

    @property
    def found(self) -> bool:
        return self.rank is not None


class RetrievalEvaluator:
    def __init__(
        self,
        retriever: Retriever | None = None,
    ) -> None:
        self.retriever = retriever or DenseRetriever()

    def evaluate_case(
        self,
        case: RetrievalEvaluationCase,
        limit: int = 10,
    ) -> RetrievalEvaluationResult:
        results = self.retriever.retrieve(
            query=case.query,
            limit=limit,
        )

        for rank, result in enumerate(results, start=1):
            if result.book_id != case.expected_book_id:
                continue

            if any(
                expected_text.casefold() in result.text.casefold()
                for expected_text in case.expected_texts
            ):
                return RetrievalEvaluationResult(
                    query=case.query,
                    rank=rank,
                )

        return RetrievalEvaluationResult(
            query=case.query,
            rank=None,
        )