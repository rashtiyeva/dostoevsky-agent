import re

from ingestion.models import Chunk, Section


SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?…])\s+")


def split_into_sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in SENTENCE_SPLIT_PATTERN.split(text)
        if sentence.strip()
    ]


def split_into_paragraphs(section: Section) -> list[str]:
    return [
        paragraph.strip()
        for paragraph in section.text.split("\n\n")
        if paragraph.strip()
    ]


def build_chunk(
    section: Section,
    book_id: str,
    paragraphs: list[str],
    chunk_index: int,
) -> Chunk:
    return Chunk(
        book_id=book_id,
        part=section.part,
        part_title=section.part_title,
        book=section.book,
        chapter=section.chapter,
        chapter_title=section.chapter_title,
        section=section.section,
        text="\n\n".join(paragraphs),
        chunk_index=chunk_index,
        content_type="main_text",
    )


def append_chunk(
    chunks: list[Chunk],
    section: Section,
    book_id: str,
    paragraphs: list[str],
) -> None:
    chunks.append(
        build_chunk(
            section=section,
            book_id=book_id,
            paragraphs=paragraphs,
            chunk_index=len(chunks),
        )
    )


def split_long_text(
    text: str,
    max_chars: int,
) -> list[str]:
    return [
        text[i:i + max_chars]
        for i in range(0, len(text), max_chars)
    ]


def split_large_paragraph(
    paragraph: str,
    max_chars: int,
) -> list[str]:
    sentences = split_into_sentences(paragraph)

    parts: list[str] = []
    current_sentences: list[str] = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if sentence_length > max_chars:
            if current_sentences:
                parts.append(" ".join(current_sentences))
                current_sentences = []
                current_length = 0

            parts.extend(
                split_long_text(
                    sentence,
                    max_chars,
                )
            )

            continue

        separator_length = 1 if current_sentences else 0

        if (
            current_sentences
            and current_length + separator_length + sentence_length > max_chars
        ):
            parts.append(" ".join(current_sentences))

            current_sentences = []
            current_length = 0
            separator_length = 0

        current_sentences.append(sentence)
        current_length += separator_length + sentence_length

    if current_sentences:
        parts.append(" ".join(current_sentences))

    return parts


def chunk_section(
    section: Section,
    book_id: str,
    max_chars: int = 2500,
) -> list[Chunk]:
    paragraphs = split_into_paragraphs(section)

    chunks: list[Chunk] = []
    current_paragraphs: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        if paragraph_length > max_chars:
            if current_paragraphs:
                append_chunk(
                    chunks,
                    section,
                    book_id,
                    current_paragraphs,
                )

                current_paragraphs = []
                current_length = 0

            for part in split_large_paragraph(
                paragraph,
                max_chars,
            ):
                append_chunk(
                    chunks,
                    section,
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
                section,
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
            section,
            book_id,
            current_paragraphs,
        )

    return chunks