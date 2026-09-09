def clean_text(text: str) -> str:
    lines = text.splitlines()

    cleaned_lines = []
    previous_was_empty = False

    for line in lines:
        stripped_line = line.strip()

        if stripped_line:
            cleaned_lines.append(stripped_line)
            previous_was_empty = False

        elif not previous_was_empty:
            cleaned_lines.append("")
            previous_was_empty = True

    return "\n".join(cleaned_lines).strip()