from retrieval.models import RetrievedChunk


def build_rag_prompt(
    query: str,
    chunks: list[RetrievedChunk],
) -> str:
    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            "\n".join(
                [
                    f"[{index}]",
                    f"Book: {chunk.book_id}",
                    f"Chapter: {chunk.chapter or '-'}",
                    f"Section: {chunk.section or '-'}",
                    f"Text: {chunk.text}",
                ]
            )
        )

    context = "\n\n".join(context_parts)

    return f"""Answer the user's question using only the provided excerpts from Dostoevsky's works.

If the excerpts do not contain enough information to answer the question, say that the provided sources are insufficient.

Do not invent information that is not supported by the excerpts.

Cite supporting excerpts using their numbers, for example [1] or [2].

Answer in the same language as the user's question.

Question:
{query}

Excerpts:
{context}
"""