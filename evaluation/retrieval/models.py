from dataclasses import dataclass


@dataclass
class RetrievalEvaluationCase:
    query: str
    expected_book_id: str
    expected_texts: list[str]