from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from chunking.chunker import chunk_section, count_tokens
from chunking.config import MIN_CHUNK_TOKENS
from ingestion.cleaner import clean_text
from ingestion.extractor import extract_book_text
from ingestion.loader import load_document
from ingestion.parser import parse_sections

BOOKS_DIR = Path("data/books")
SMALL_CHUNK_THRESHOLD = MIN_CHUNK_TOKENS


def collect_chunks():
    collected_chunks = []

    for book_dir in BOOKS_DIR.iterdir():
        if not book_dir.is_dir():
            continue

        document = load_document(book_dir)

        book_text = extract_book_text(document)
        cleaned_text = clean_text(book_text)
        sections = parse_sections(
            cleaned_text,
            has_section_titles=document.has_section_titles,
        )

        for section in sections:
            chunks = chunk_section(
                section=section,
                book_id=document.book_id,
            )

            for chunk in chunks:
                collected_chunks.append(chunk)

    return collected_chunks


def print_chunk_statistics(chunks) -> None:
    token_counts = [
        count_tokens(chunk.text)
        for chunk in chunks
    ]

    total_chunks = len(token_counts)

    under_50 = sum(
        count < 50
        for count in token_counts
    )

    between_50_99 = sum(
        50 <= count < 100
        for count in token_counts
    )

    between_100_299 = sum(
        100 <= count < 300
        for count in token_counts
    )

    between_300_499 = sum(
        300 <= count < 500
        for count in token_counts
    )

    between_500_600 = sum(
        500 <= count <= 600
        for count in token_counts
    )

    small_chunks = sum(
        count < SMALL_CHUNK_THRESHOLD
        for count in token_counts
    )

    print("\nGLOBAL CHUNK STATISTICS")
    print("=" * 80)

    print(f"Total chunks: {total_chunks}")
    print(f"Minimum tokens: {min(token_counts)}")
    print(f"Maximum tokens: {max(token_counts)}")
    print(f"Average tokens: {mean(token_counts):.2f}")
    print(f"Median tokens: {median(token_counts):.2f}")

    print("\nDistribution:")
    print(f"< 50 tokens: {under_50}")
    print(f"50-99 tokens: {between_50_99}")
    print(f"100-299 tokens: {between_100_299}")
    print(f"300-499 tokens: {between_300_499}")
    print(f"500-600 tokens: {between_500_600}")

    small_percentage = (
        small_chunks / total_chunks * 100
        if total_chunks
        else 0
    )

    print(
        f"\nChunks under {SMALL_CHUNK_THRESHOLD}: "
        f"{small_chunks} ({small_percentage:.2f}%)"
    )


def print_book_statistics(chunks) -> None:
    chunks_by_book = defaultdict(list)

    for chunk in chunks:
        chunks_by_book[chunk.book_id].append(chunk)

    print("\nPER-BOOK STATISTICS")
    print("=" * 80)

    for book_id, book_chunks in sorted(
        chunks_by_book.items()
    ):
        token_counts = [
            count_tokens(chunk.text)
            for chunk in book_chunks
        ]

        small_chunks = sum(
            count < SMALL_CHUNK_THRESHOLD
            for count in token_counts
        )

        small_percentage = (
            small_chunks / len(token_counts) * 100
        )

        print(f"\nBook: {book_id}")
        print(f"Chunks: {len(token_counts)}")
        print(f"Minimum: {min(token_counts)}")
        print(f"Maximum: {max(token_counts)}")
        print(f"Average: {mean(token_counts):.2f}")
        print(f"Median: {median(token_counts):.2f}")
        print(
            f"Under {SMALL_CHUNK_THRESHOLD}: "
            f"{small_chunks} "
            f"({small_percentage:.2f}%)"
        )


def print_small_chunks(
    chunks,
    threshold: int = SMALL_CHUNK_THRESHOLD,
) -> None:
    print(
        f"\nCHUNKS UNDER {threshold} TOKENS"
    )
    print("=" * 80)

    small_chunks_found = False

    for chunk in chunks:
        token_count = count_tokens(chunk.text)

        if token_count >= threshold:
            continue

        small_chunks_found = True

        print("\n" + "=" * 80)
        print(f"Book: {chunk.book_id}")
        print(f"Tokens: {token_count}")
        print(f"Part: {chunk.part}")
        print(f"Book section: {chunk.book}")
        print(f"Chapter: {chunk.chapter}")
        print(f"Chapter title: {chunk.chapter_title}")
        print(f"Section: {chunk.section}")
        print(f"Section title: {chunk.section_title}")
        print("\nTEXT:")
        print(repr(chunk.text))

    if not small_chunks_found:
        print(
            f"\nNo chunks under {threshold} tokens."
        )


def main() -> None:
    chunks = collect_chunks()

    if not chunks:
        print("No chunks found.")
        return

    print_chunk_statistics(chunks)
    print_book_statistics(chunks)
    print_small_chunks(chunks)


if __name__ == "__main__":
    main()