from evaluation.retrieval.dataset import EVALUATION_CASES
from evaluation.retrieval.evaluator import RetrievalEvaluator
from evaluation.retrieval.metrics import (
    mean_reciprocal_rank,
    recall_at_k,
)


def main() -> None:
    evaluator = RetrievalEvaluator()

    results = [
        evaluator.evaluate_case(
            case=case,
            limit=10,
        )
        for case in EVALUATION_CASES
    ]

    print(f"Evaluation cases: {len(results)}")
    print(f"Recall@1:  {recall_at_k(results, 1):.4f}")
    print(f"Recall@3:  {recall_at_k(results, 3):.4f}")
    print(f"Recall@5:  {recall_at_k(results, 5):.4f}")
    print(f"Recall@10: {recall_at_k(results, 10):.4f}")
    print(f"MRR:       {mean_reciprocal_rank(results):.4f}")

    print("\nResults:")

    for result in results:
        rank = result.rank if result.rank is not None else "NOT FOUND"
        print(f"- {result.query}: {rank}")


if __name__ == "__main__":
    main()