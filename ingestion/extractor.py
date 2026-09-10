from ingestion.models import Document


def extract_book_text(document: Document) -> str:
    lines = document.text.splitlines()

    start_index = 0
    end_index = len(lines)

    if document.start_marker:
        start_index = _find_marker(
            lines=lines,
            marker=document.start_marker,
        )

    if document.end_marker:
        end_index = _find_marker(
            lines=lines,
            marker=document.end_marker,
            start_index=start_index + 1,
        )

    return "\n".join(
        lines[start_index:end_index]
    ).strip()


def _find_marker(
    lines: list[str],
    marker: str,
    start_index: int = 0,
) -> int:
    normalized_marker = marker.strip().casefold()

    for index in range(start_index, len(lines)):
        if lines[index].strip().casefold() == normalized_marker:
            return index

    raise ValueError(
        f"Marker not found: {marker}"
    )