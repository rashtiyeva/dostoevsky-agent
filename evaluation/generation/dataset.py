from evaluation.generation.models import GenerationEvaluationCase

EVALUATION_CASES = [
    GenerationEvaluationCase(
        query="Почему Раскольников совершил убийство?",
    ),
    GenerationEvaluationCase(
        query="Какова теория Раскольникова о необыкновенных людях?",
    ),
    GenerationEvaluationCase(
        query="Кто такой князь Мышкин?",
    ),
    GenerationEvaluationCase(
        query="Кто такой Рогожин и как он относится к Настасье Филипповне?",
    ),
    GenerationEvaluationCase(
        query="Почему Дмитрий Карамазов конфликтует с отцом?",
    ),
    GenerationEvaluationCase(
        query="Какие взгляды Иван Карамазов выражает о Боге и морали?",
    ),
    GenerationEvaluationCase(
        query="Как Пётр Верховенский относится к Ставрогину?",
    ),
    GenerationEvaluationCase(
        query="Какие политические идеи продвигает Пётр Верховенский?",
    ),
    GenerationEvaluationCase(
        query="Как подпольный человек относится к обществу и другим людям?",
    ),
    GenerationEvaluationCase(
        query="Каковы отношения подпольного человека с Лизой?",
    ),

    # The corpus should not be able to answer this.
    GenerationEvaluationCase(
        query="Что Достоевский писал о смартфонах?",
        should_answer=False,
    ),
]