from retrieval.hybrid_retriever import HybridRetriever


def main() -> None:
    retriever = HybridRetriever()

    query = "Почему Раскольников совершил убийство?"

    results = retriever.retrieve(
        query=query,
        limit=5,
    )

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Score: {result.score:.4f}")
        print(f"Book: {result.book_id}")
        print(f"Chapter: {result.chapter}")
        print(f"Section: {result.section}")
        print(f"Text: {result.text[:500]}")


if __name__ == "__main__":
    main()