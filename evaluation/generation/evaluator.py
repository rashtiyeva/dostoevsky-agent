import json

from openai import OpenAI

from app.config import OPENAI_API_KEY
from evaluation.generation.models import (
    GenerationEvaluationCase,
    GenerationEvaluationResult,
)
from generation.models import GeneratedAnswer

client = OpenAI(api_key=OPENAI_API_KEY)


def evaluate_answer(
    case: GenerationEvaluationCase,
    result: GeneratedAnswer,
) -> GenerationEvaluationResult:
    sources = "\n\n".join(
        f"[{citation.number}] {citation.text}"
        for citation in result.citations
    )

    prompt = f"""
You are evaluating a RAG system about Dostoevsky.

Question:
{case.query}

The system is expected to answer:
{case.should_answer}

Answer:
{result.answer}

Sources:
{sources}

Score each criterion from 1 to 5.

relevance:
Does the answer directly address the question?

groundedness:
Are the claims in the answer supported by the provided sources?

citation:
Do the citations support the claims they are attached to?

abstention:
If the question cannot be answered from the sources, does the answer correctly say that the evidence is insufficient?
If the question can be answered, give 5 when the system answers normally.

Return ONLY valid JSON in this format:

{{
  "relevance_score": 1,
  "groundedness_score": 1,
  "citation_score": 1,
  "abstention_score": 1
}}
"""

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt,
    )

    scores = json.loads(response.output_text)

    passed = all(
        scores[key] >= 4
        for key in [
            "relevance_score",
            "groundedness_score",
            "citation_score",
            "abstention_score",
        ]
    )

    return GenerationEvaluationResult(
        query=case.query,
        answer=result.answer,
        relevance_score=scores["relevance_score"],
        groundedness_score=scores["groundedness_score"],
        citation_score=scores["citation_score"],
        abstention_score=scores["abstention_score"],
        passed=passed,
    )