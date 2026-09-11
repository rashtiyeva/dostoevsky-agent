import json
from pathlib import Path

from ingestion.models import Document


def load_document(book_dir: Path) -> Document:
    metadata_path = book_dir / "metadata.json"
    text_path = book_dir / "book.txt"

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    with text_path.open("r", encoding="utf-8") as file:
        text = file.read()

    return Document(
        book_id=metadata["book_id"],
        title=metadata["title"],
        author=metadata["author"],
        language=metadata["language"],
        text=text,
        start_marker=metadata.get("start_marker"),
        end_marker=metadata.get("end_marker"),
        has_section_titles=metadata.get(
            "has_section_titles",
            False,
        ),
    )
