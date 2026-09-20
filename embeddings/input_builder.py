from chunking.models import Chunk


def build_embedding_input(chunk: Chunk) -> str:
    context = [
        chunk.part,
        chunk.part_title,
        chunk.book,
        chunk.chapter,
        chunk.chapter_title,
        chunk.section,
        chunk.section_title,
    ]
    
    parts = [
        value 
        for value in context
        if value
    ]
    
    parts.append(chunk.text)
    
    return "\n".join(parts)