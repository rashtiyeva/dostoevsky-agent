from evaluation.retrieval.models import RetrievalEvaluationCase

EVALUATION_CASES: list[RetrievalEvaluationCase] = [
    # Crime and Punishment
    RetrievalEvaluationCase(
        query="Почему Раскольников совершил убийство?",
        expected_book_id="crime_and_punishment",
        expected_texts=[
            "что именно могло склонить его к смертоубийству",
            "тут теоретически раздраженное сердце",
        ],
    ),
    RetrievalEvaluationCase(
        query="Какова теория Раскольникова о необыкновенных людях?",
        expected_book_id="crime_and_punishment",
        expected_texts=[
            "люди, по закону природы, разделяются вообще на два разряда",
            "имеющих дар или талант сказать в среде своей новое слово",
        ],
    ),

    # The Idiot
    RetrievalEvaluationCase(
        query="Кто такой князь Мышкин?",
        expected_book_id="idiot",
        expected_texts=[
            "Князь Лев Николаевич Мышкин",
            "князей Мышкиных теперь и совсем нет, кроме меня",
        ],
    ),
    RetrievalEvaluationCase(
        query="Кто такой Рогожин и как он относится к Настасье Филипповне?",
        expected_book_id="idiot",
        expected_texts=[
            "Настасья Филипповна",
            "Рогожин",
        ],
    ),

    # The Brothers Karamazov
    RetrievalEvaluationCase(
        query="Почему Дмитрий Карамазов конфликтует с отцом?",
        expected_book_id="brothers_karamazov",
        expected_texts=[
            "Митеньке теперь пересекает дорогу старикашка отец",
            "тот по Грушеньке с ума вдруг сошел",
        ],
    ),
    RetrievalEvaluationCase(
        query="Какие взгляды Иван Карамазов выражает о Боге и морали?",
        expected_book_id="brothers_karamazov",
        expected_texts=[
            "все будет позволено",
            "не верующего ни в Бога, ни в бессмертие свое",
        ],
    ),

    # Demons
    RetrievalEvaluationCase(
        query="Как Пётр Верховенский относится к Ставрогину?",
        expected_book_id="demons",
        expected_texts=[
            "Вы мой идол!",
            "Вы предводитель, вы солнце, а я ваш червяк",
        ],
    ),
    RetrievalEvaluationCase(
        query="Какие политические идеи продвигает Пётр Верховенский?",
        expected_book_id="demons",
        expected_texts=[
            "Мы провозгласим разрушение",
            "Мы пустим пожары",
        ],
    ),

    # Notes from Underground
    RetrievalEvaluationCase(
        query="Как подпольный человек относится к обществу и другим людям?",
        expected_book_id="notes_from_underground",
        expected_texts=[
            "лучше ничего не делать! Лучше сознательная инерция",
            "да здравствует подполье",
        ],
    ),
    RetrievalEvaluationCase(
        query="Каковы отношения подпольного человека с Лизой?",
        expected_book_id="notes_from_underground",
        expected_texts=[
            "Я оскорбил ее окончательно",
            "не в состоянии любить ее",
        ],
    ),
]