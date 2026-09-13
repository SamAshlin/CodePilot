from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_embedding(text: str):

    response = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
        config={
            "output_dimensionality": 1536
        }
    )

    return response.embeddings[0].values