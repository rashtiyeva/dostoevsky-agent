from retrieval.retriever import DenseRetriever


QUERIES = [
    # Crime and Punishment
    "Почему Раскольников совершил убийство?",
    "Почему Раскольников признался в убийстве?",
    "Какова теория Раскольникова о необыкновенных людях?",

    # The Idiot
    "Кто такой князь Мышкин?",
    "Какие отношения между князем Мышкиным и Настасьей Филипповной?",
    "Кто такой Рогожин и как он относится к Настасье Филипповне?",

    # The Brothers Karamazov
    "Каковы отношения Ивана и Алёши Карамазовых?",
    "Почему Дмитрий Карамазов конфликтует с отцом?",
    "Какие взгляды Иван Карамазов выражает о Боге и страдании?",

    # Demons
    "Кто такой Ставрогин?",
    "Как Пётр Верховенский относится к Ставрогину?",
    "Какие политические идеи продвигает Пётр Верховенский?",

    # Notes from Underground
    "Как подпольный человек относится к обществу и другим людям?",
    "Почему подпольный человек критикует рациональный эгоизм?",
    "Каковы отношения подпольного человека с Лизой?",
]


def main() -> None:
    retriever = DenseRetriever()

    for query in QUERIES:
        print(f"\n{'=' * 80}")
        print(f"QUERY: {query}")
        print("=" * 80)

        results = retriever.retrieve(
            query=query,
            limit=5,
        )

        for rank, result in enumerate(results, start=1):
            print(f"\n--- #{rank} | score={result.score:.4f} ---")
            print(f"Book: {result.book_id}")
            print(f"Section: {result.section}")
            print(result.text)


if __name__ == "__main__":
    main()