import re

from rank_bm25 import BM25Okapi


def tokenize(text):

    return re.findall(
        r"[a-zA-Z_][a-zA-Z0-9_]*",
        text.lower()
    )


def build_bm25(chunks):

    documents = []

    for chunk in chunks:

        searchable_text = " ".join([
            chunk.get("file_path", ""),
            chunk.get("name") or "",
            chunk.get("parent") or "",
            " ".join(
                chunk.get("context", [])
            ),
            chunk.get("content", "")
        ])

        documents.append(
            tokenize(searchable_text)
        )

    return BM25Okapi(
        documents
    )


def search_bm25(
    question,
    chunks,
    limit=20
):

    if not chunks:
        return []

    bm25 = build_bm25(
        chunks
    )

    query_tokens = tokenize(
        question
    )

    scores = bm25.get_scores(
        query_tokens
    )

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indexes[:limit]:

        chunk = chunks[index].copy()

        chunk["bm25_score"] = float(
            scores[index]
        )

        results.append(chunk)

    return results