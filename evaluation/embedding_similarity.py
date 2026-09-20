from embeddings.embedder import EmbeddingModel


PASSAGE = (
    "Раскольников совершил убийство "
    "старухи-процентщицы."
)

QUERIES = {
    "RU": "Кого убил Раскольников?",
    "EN": "Whom did Raskolnikov kill?",
    "AZ": "Raskolnikov kimi öldürdü?",
    "UNRELATED": "Как приготовить картошку?",
}


def dot_product(
    first: list[float],
    second: list[float],
) -> float:
    return sum(
        a * b
        for a, b in zip(first, second)
    )


def main() -> None:
    model = EmbeddingModel()

    passage_embedding = model.embed(PASSAGE)

    for language, query in QUERIES.items():
        query_embedding = model.embed(query)

        similarity = dot_product(
            passage_embedding,
            query_embedding,
        )

        print(
            f"{language}: "
            f"{similarity:.4f}"
        )


if __name__ == "__main__":
    main()