import re

from generation.models import Citation
from retrieval.models import RetrievedChunk

CITATION_PATTERN = re.compile(r"\[(\d+)\]")


def map_citations(
    answer: str,
    chunks: list[RetrievedChunk],
) -> list[Citation]:
    citation_numbers = {
        int(match)
        for match in CITATION_PATTERN.findall(answer)
    }

    citations = []

    for number in sorted(citation_numbers):
        index = number - 1

        if index < 0 or index >= len(chunks):
            continue

        chunk = chunks[index]

        citations.append(
            Citation(
                number=number,
                book_id=chunk.book_id,
                chapter=chunk.chapter,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )
        )

    return citations