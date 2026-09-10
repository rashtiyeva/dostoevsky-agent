import re
from dataclasses import dataclass, field

from ingestion.models import Section


PART_PATTERN = re.compile(
    r"(Часть\s+(?:[IVXLCDM]+|[А-Яа-яЁё]+)|Эпилог)",
    re.IGNORECASE,
)

BOOK_PATTERN = re.compile(
    r"Книга\s+.+",
    re.IGNORECASE,
)

CHAPTER_PATTERN = re.compile(
    r"Глава\s+.+",
    re.IGNORECASE,
)

SECTION_PATTERN = re.compile(
    r"[IVXLCDM]+\.?",
    re.IGNORECASE,
)

NOTES_PATTERN = re.compile(
    r"(Примечания|notes)",
    re.IGNORECASE,
)


@dataclass
class ParserState:
    part: str | None = None
    part_title: str | None = None

    book: str | None = None

    chapter: str | None = None
    chapter_title: str | None = None

    section: str | None = None

    text: list[str] = field(default_factory=list)
    waiting_for_title: str | None = None


def _build_section(state: ParserState) -> Section | None:
    text = "\n".join(state.text).strip()

    if not text:
        return None

    return Section(
        part=state.part,
        part_title=state.part_title,
        book=state.book,
        chapter=state.chapter,
        chapter_title=state.chapter_title,
        section=state.section,
        text=text,
    )


def _save_current_section(
    sections: list[Section],
    state: ParserState,
) -> None:
    section = _build_section(state)

    if section:
        sections.append(section)

    state.text = []


def _start_part(
    state: ParserState,
    part: str,
) -> None:
    state.part = part
    state.part_title = None

    state.book = None

    state.chapter = None
    state.chapter_title = None

    state.section = None
    state.waiting_for_title = "part"


def _start_book(
    state: ParserState,
    book: str,
) -> None:
    state.book = book

    state.chapter = None
    state.chapter_title = None

    state.section = None

    # The book title is already part of the heading:
    # "Книга двенадцатая: Судебная ошибка"
    state.waiting_for_title = None


def _start_chapter(
    state: ParserState,
    chapter: str,
) -> None:
    state.chapter = chapter
    state.chapter_title = None

    state.section = None
    state.waiting_for_title = "chapter"


def _start_section(
    state: ParserState,
    section: str,
) -> None:
    state.section = section.rstrip(".")
    state.waiting_for_title = None


def _set_optional_title(
    state: ParserState,
    line: str,
) -> bool:
    if state.waiting_for_title == "part":
        state.part_title = line
        state.waiting_for_title = None
        return True

    if state.waiting_for_title == "chapter":
        state.chapter_title = line
        state.waiting_for_title = None
        return True

    return False


def parse_sections(text: str) -> list[Section]:
    sections: list[Section] = []
    state = ParserState()

    for line in text.splitlines():
        stripped_line = line.strip()

        if not stripped_line:
            if state.text:
                state.text.append("")
            continue

        if NOTES_PATTERN.fullmatch(stripped_line):
            _save_current_section(
                sections,
                state,
            )
            break

        if PART_PATTERN.fullmatch(stripped_line):
            _save_current_section(
                sections,
                state,
            )

            _start_part(
                state,
                stripped_line,
            )
            continue

        if BOOK_PATTERN.fullmatch(stripped_line):
            _save_current_section(
                sections,
                state,
            )

            _start_book(
                state,
                stripped_line,
            )
            continue

        if CHAPTER_PATTERN.fullmatch(stripped_line):
            _save_current_section(
                sections,
                state,
            )

            _start_chapter(
                state,
                stripped_line,
            )
            continue

        if SECTION_PATTERN.fullmatch(stripped_line):
            _save_current_section(
                sections,
                state,
            )

            _start_section(
                state,
                stripped_line,
            )
            continue

        if _set_optional_title(
            state,
            stripped_line,
        ):
            continue

        state.text.append(line)

    else:
        _save_current_section(
            sections,
            state,
        )

    return sections