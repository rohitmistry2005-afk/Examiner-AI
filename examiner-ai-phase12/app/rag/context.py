from __future__ import annotations


def format_retrieved_context(chunks: list[dict], max_chars: int = 7000) -> str:
    if not chunks:
        return ""
    parts: list[str] = []
    used = 0
    for i, chunk in enumerate(chunks, start=1):
        text = " ".join(str(chunk.get("content", "")).split())
        if not text:
            continue
        page = chunk.get("page_number")
        label = f"Document excerpt {i}"
        if page:
            label += f" (page {page})"
        block = f"[{label}]\n{text}"
        if used + len(block) > max_chars:
            remaining = max_chars - used
            if remaining < 200:
                break
            block = block[:remaining]
        parts.append(block)
        used += len(block)
        if used >= max_chars:
            break
    return "\n\n".join(parts)
