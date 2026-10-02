from app.llm.openai_client import generate_response
from generation.citation_mapper import map_citations
from generation.models import GeneratedAnswer
from generation.prompt_builder import build_rag_prompt
from retrieval.reranked_retriever import RerankedRetriever

retriever = RerankedRetriever()


async def generate_rag_response(query: str) -> GeneratedAnswer:
    chunks = retriever.retrieve(
        query=query,
        limit=5,
    )

    prompt = build_rag_prompt(
        query=query,
        chunks=chunks,
    )

    answer = await generate_response(prompt)

    citations = map_citations(
        answer=answer,
        chunks=chunks,
    )

    return GeneratedAnswer(
        answer=answer,
        citations=citations,
    )