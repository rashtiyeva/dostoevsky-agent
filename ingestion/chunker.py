from ingestion.models import Chapter, Chunk


def split_into_paragraphs(chapter: Chapter) -> list[str]:
    return [
        paragraph.strip()
        for paragraph in chapter.text.split("\n\n")
        if paragraph.strip()
    ]


def build_chunk(
    chapter: Chapter,
    book_id: str,
    paragraphs: list[str],
    chunk_index: int,
) -> Chunk:
    return Chunk(
        book_id=book_id,
        part=chapter.part,
        chapter=chapter.chapter,
        text="\n\n".join(paragraphs),
        chunk_index=chunk_index,
    )


def append_chunk(
    chunks: list[Chunk],
    chapter: Chapter,
    book_id: str,
    paragraphs: list[str],
) -> None:
    chunks.append(
        build_chunk(
            chapter=chapter,
            book_id=book_id,
            paragraphs=paragraphs,
            chunk_index=len(chunks),
        )
    )


def split_large_paragraph(
    paragraph: str,
    max_chars: int,
) -> list[str]:
    return [
        paragraph[i:i + max_chars]
        for i in range(0, len(paragraph), max_chars)
    ]


def chunk_chapter(
    chapter: Chapter,
    book_id: str,
    max_chars: int = 2500,
) -> list[Chunk]:
    paragraphs = split_into_paragraphs(chapter)

    chunks: list[Chunk] = []
    current_paragraphs: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        if paragraph_length > max_chars:
            if current_paragraphs:
                append_chunk(
                    chunks,
                    chapter,
                    book_id,
                    current_paragraphs,
                )

                current_paragraphs = []
                current_length = 0

            for part in split_large_paragraph(paragraph, max_chars):
                append_chunk(
                    chunks,
                    chapter,
                    book_id,
                    [part],
                )

            continue

        separator_length = 2 if current_paragraphs else 0

        if (
            current_paragraphs
            and current_length + separator_length + paragraph_length > max_chars
        ):
            append_chunk(
                chunks,
                chapter,
                book_id,
                current_paragraphs,
            )

            current_paragraphs = []
            current_length = 0
            separator_length = 0

        current_paragraphs.append(paragraph)
        current_length += separator_length + paragraph_length

    if current_paragraphs:
        append_chunk(
            chunks,
            chapter,
            book_id,
            current_paragraphs,
        )

    return chunks