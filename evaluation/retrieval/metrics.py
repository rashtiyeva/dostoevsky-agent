from evaluation.retrieval.evaluator import RetrievalEvaluationResult


def recall_at_k(
    results: list[RetrievalEvaluationResult],
    k: int,
) -> float:
    if not results:
        return 0.0

    hits = sum(
        1
        for result in results
        if result.rank is not None and result.rank <= k
    )

    return hits / len(results)


def mean_reciprocal_rank(
    results: list[RetrievalEvaluationResult],
) -> float:
    if not results:
        return 0.0

    reciprocal_ranks = [
        1 / result.rank
        if result.rank is not None
        else 0.0
        for result in results
    ]

    return sum(reciprocal_ranks) / len(results)