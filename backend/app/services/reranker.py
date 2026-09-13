import json

from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_LLM_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def rerank(
    question,
    chunks,
    top_k=6
):

    if not chunks:
        return []

    candidates = []

    for index, chunk in enumerate(chunks):

        candidates.append(
            f"""
CANDIDATE {index}

File:
{chunk.get('file_path')}

Language:
{chunk.get('language')}

Code type:
{chunk.get('chunk_type')}

Name:
{chunk.get('name')}

Parent:
{chunk.get('parent')}

Lines:
{chunk.get('start_line')}-{chunk.get('end_line')}

Code:
{chunk.get('content')}
"""
        )

    candidate_text = "\n".join(
        candidates
    )

    prompt = f"""
You are a code retrieval reranker.

Your task is to rank code candidates according
to how useful they are for answering the
developer's question.

Developer question:

{question}

Code candidates:

{candidate_text}

Ranking rules:

1. Prefer code that directly answers the question.
2. Prefer the implementation over unrelated callers.
3. Prefer the most specific function or method.
4. Prefer code whose class/module context is relevant.
5. Exact names mentioned in the question are strong signals.
6. Do not rank a candidate highly merely because
   it contains common words.
7. If a candidate is unrelated, rank it low.
8. Do not invent information.

Return ONLY valid JSON.

Format:

[
    {{
        "candidate": 0,
        "score": 0.95
    }},
    {{
        "candidate": 3,
        "score": 0.82
    }}
]

Return at most {top_k} candidates.
Sort from highest score to lowest score.
"""

    response = client.models.generate_content(
        model=GEMINI_LLM_MODEL,
        contents=prompt
    )

    text = response.text.strip()

    # Remove markdown code fences if Gemini
    # happens to return them.
    if text.startswith("```"):

        text = text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

    try:

        rankings = json.loads(
            text
        )

    except json.JSONDecodeError:

        # Safe fallback:
        # preserve vector-search ordering.
        return chunks[:top_k]

    reranked = []

    for item in rankings:

        index = item.get(
            "candidate"
        )

        if not isinstance(
            index,
            int
        ):
            continue

        if index < 0 or index >= len(chunks):
            continue

        chunk = chunks[index].copy()

        chunk["rerank_score"] = float(
            item.get(
                "score",
                0
            )
        )

        reranked.append(
            chunk
        )

    return reranked[:top_k]