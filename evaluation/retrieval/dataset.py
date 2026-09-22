from evaluation.retrieval.models import RetrievalEvaluationCase

EVALUATION_CASES: list[RetrievalEvaluationCase] = [
    RetrievalEvaluationCase(
        query="Почему Раскольников совершил убийство?",
        expected_book_id="crime_and_punishment",
        expected_texts=[
            "что именно могло склонить его к смертоубийству",
            "тут теоретически раздраженное сердце",
        ],
    ),
]