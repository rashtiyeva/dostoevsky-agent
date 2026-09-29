from dataclasses import dataclass


@dataclass
class GenerationEvaluationCase:
    query: str
    should_answer: bool = True


@dataclass
class GenerationEvaluationResult:
    query: str
    answer: str
    relevance_score: int
    groundedness_score: int
    citation_score: int
    abstention_score: int
    passed: bool