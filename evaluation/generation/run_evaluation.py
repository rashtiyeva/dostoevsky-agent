import asyncio

from app.services.rag_service import generate_rag_response
from evaluation.generation.dataset import EVALUATION_CASES
from evaluation.generation.evaluator import evaluate_answer


async def main() -> None:
    results = []

    for index, case in enumerate(EVALUATION_CASES, start=1):
        print(f"\n[{index}/{len(EVALUATION_CASES)}] {case.query}")

        answer = await generate_rag_response(case.query)

        result = evaluate_answer(
            case=case,
            result=answer,
        )

        results.append(result)

        print(f"Relevance:    {result.relevance_score}/5")
        print(f"Groundedness: {result.groundedness_score}/5")
        print(f"Citations:    {result.citation_score}/5")
        print(f"Abstention:   {result.abstention_score}/5")
        print(f"Passed:       {result.passed}")

    passed = sum(result.passed for result in results)

    print("\n=== SUMMARY ===")
    print(f"Cases:  {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")


if __name__ == "__main__":
    asyncio.run(main())