def chunk_code(
    content,
    file_path,
    language,
    chunk_size=80,
    overlap=15
):
    lines = content.splitlines()

    chunks = []

    start = 0

    while start < len(lines):

        end = min(
            start + chunk_size,
            len(lines)
        )

        chunk_lines = lines[start:end]

        text = "\n".join(chunk_lines)

        if text.strip():
            chunks.append({
                "content": text,
                "file_path": file_path,
                "language": language,
                "start_line": start + 1,
                "end_line": end
            })

        # Move forward safely
        if end >= len(lines):
            break

        start = end - overlap

    return chunks