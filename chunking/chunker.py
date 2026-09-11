import re

import tiktoken

from chunking.config import MAX_TOKENS, OVERLAP_TOKENS
from chunking.models import Chunk
from ingestion.models import Section

SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?…])\s+")
ENCODING = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(
        ENCODING.encode(text)
    )


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


def split_long_text(
    text: str,
    max_tokens: int,
) -> list[str]:
    tokens = ENCODING.encode(text)

    return [
        ENCODING.decode(tokens[i:i + max_tokens]).strip()
        for i in range(0, len(tokens), max_tokens)
        if tokens[i:i + max_tokens]
    ]


def split_large_paragraph(
    paragraph: str,
    max_tokens: int,
) -> list[str]:
    sentences = split_into_sentences(paragraph)

    parts: list[str] = []
    current_sentences: list[str] = []

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        if sentence_tokens > max_tokens:
            if current_sentences:
                parts.append(
                    " ".join(current_sentences)
                )
                current_sentences = []

            parts.extend(
                split_long_text(
                    sentence,
                    max_tokens,
                )
            )
            continue

        candidate = " ".join(
            current_sentences + [sentence]
        )

        if (
            current_sentences
            and count_tokens(candidate) > max_tokens
        ):
            parts.append(
                " ".join(current_sentences)
            )
            current_sentences = []

        current_sentences.append(sentence)

    if current_sentences:
        parts.append(
            " ".join(current_sentences)
        )

    return parts


def normalize_chunk_units(
    paragraphs: list[str],
    max_tokens: int,
) -> list[str]:
    units: list[str] = []

    for paragraph in paragraphs:
        if count_tokens(paragraph) > max_tokens:
            units.extend(
                split_large_paragraph(
                    paragraph,
                    max_tokens,
                )
            )
        else:
            units.append(paragraph)

    return units


def get_overlap_text(
    text: str,
    next_text: str,
    overlap_tokens: int,
    max_tokens: int,
) -> str:
    if overlap_tokens <= 0:
        return ""

    sentences = split_into_sentences(text)

    overlap_sentences: list[str] = []

    for sentence in reversed(sentences):
        candidate_sentences = [
            sentence,
            *overlap_sentences,
        ]

        candidate_overlap = " ".join(
            candidate_sentences
        )

        if count_tokens(candidate_overlap) > overlap_tokens:
            break

        candidate_chunk = (
            f"{candidate_overlap}\n\n{next_text}"
        )

        if count_tokens(candidate_chunk) > max_tokens:
            break

        overlap_sentences = candidate_sentences

    return " ".join(overlap_sentences)


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


def chunk_section(
    section: Section,
    book_id: str,
    max_tokens: int = MAX_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[Chunk]:
    if overlap_tokens < 0:
        raise ValueError(
            "overlap_tokens cannot be negative"
        )

    if overlap_tokens >= max_tokens:
        raise ValueError(
            "overlap_tokens must be smaller than max_tokens"
        )

    paragraphs = split_into_paragraphs(section)

    units = normalize_chunk_units(
        paragraphs,
        max_tokens,
    )

    chunks: list[Chunk] = []
    current_parts: list[str] = []

    for unit in units:
        candidate = "\n\n".join(
            current_parts + [unit]
        )

        if (
            current_parts
            and count_tokens(candidate) > max_tokens
        ):
            current_text = "\n\n".join(
                current_parts
            )

            append_chunk(
                chunks,
                section,
                book_id,
                current_parts,
            )

            overlap = get_overlap_text(
                text=current_text,
                next_text=unit,
                overlap_tokens=overlap_tokens,
                max_tokens=max_tokens,
            )

            current_parts = (
                [overlap]
                if overlap
                else []
            )

        current_parts.append(unit)

    if current_parts:
        append_chunk(
            chunks,
            section,
            book_id,
            current_parts,
        )

    return chunks