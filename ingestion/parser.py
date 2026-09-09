import re

from ingestion.models import Chapter

PART_PATTERN = re.compile(
    r"(Часть\s+(первая|вторая|третья|четвертая|пятая|шестая|седьмая|"
    r"восьмая|девятая|десятая|одиннадцатая|двенадцатая|тринадцатая|"
    r"четырнадцатая|пятнадцатая)|Эпилог)",
    re.IGNORECASE,
)

CHAPTER_PATTERN = re.compile(r"[IVXLCDM]+")

NOTES_PATTERN = re.compile(
    r"(Примечания|notes)",
    re.IGNORECASE,
)


def _build_chapter(
    part: str | None,
    chapter: str | None,
    text_lines: list[str],
) -> Chapter | None:
    if not part or not chapter:
        return None

    text = "\n".join(text_lines).strip()

    if not text:
        return None

    return Chapter(
        part=part,
        chapter=chapter,
        text=text,
    )


def parse_chapters(text: str) -> list[Chapter]:
    chapters: list[Chapter] = []

    current_part: str | None = None
    current_chapter: str | None = None
    current_text: list[str] = []

    for line in text.splitlines():
        stripped_line = line.strip()

        if NOTES_PATTERN.fullmatch(stripped_line):
            break

        if PART_PATTERN.fullmatch(stripped_line):
            chapter = _build_chapter(
                current_part,
                current_chapter,
                current_text,
            )

            if chapter:
                chapters.append(chapter)

            current_part = stripped_line
            current_chapter = None
            current_text = []
            continue

        if current_part and CHAPTER_PATTERN.fullmatch(stripped_line):
            chapter = _build_chapter(
                current_part,
                current_chapter,
                current_text,
            )

            if chapter:
                chapters.append(chapter)

            current_chapter = stripped_line
            current_text = []
            continue

        if current_part and current_chapter:
            current_text.append(line)

    chapter = _build_chapter(
        current_part,
        current_chapter,
        current_text,
    )

    if chapter:
        chapters.append(chapter)

    return chapters