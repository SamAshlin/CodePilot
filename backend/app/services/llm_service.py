from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_LLM_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(question, chunks):

    context_parts = []

    for index, chunk in enumerate(chunks):

        context_parts.append(
            f"""
SOURCE {index + 1}

File: {chunk['file_path']}
Lines: {chunk['start_line']}-{chunk['end_line']}
Language: {chunk['language']}

Code:
{chunk['content']}
"""
        )

    context = "\n".join(context_parts)


    prompt = f"""
You are an expert software engineer
analyzing a GitHub repository.

Answer the developer's question using ONLY
the repository context provided below.

IMPORTANT RULES:

1. Do not invent files.
2. Do not invent functions.
3. Do not invent classes.
4. Do not invent line numbers.
5. Do not assume code that is not provided.
6. Explain the answer clearly.
7. Mention relevant file paths.
8. Mention line ranges when available.
9. If the context is insufficient, say so.

Developer question:

{question}


Repository context:

{context}
"""


    response = client.models.generate_content(
        model=GEMINI_LLM_MODEL,
        contents=prompt
    )


    return response.text