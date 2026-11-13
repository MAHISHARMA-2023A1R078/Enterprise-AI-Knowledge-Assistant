
import ollama
import json

from app.config import settings


# Connect to the local Ollama server
client = ollama.Client(host=settings.OLLAMA_BASE_URL)








def generate_answer(prompt: str) -> str:
    """Generate a structured, concise answer using the configured chat model."""

    response = client.chat(
        model=settings.OLLAMA_CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        think=False,
        format={
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "maxLength": 500
                }
            },
            "required": ["answer"],
            "additionalProperties": False
        },
        options={
            "num_predict": 300,
            "temperature": 0.1
        }
    )

    response_content = response.message.content

    try:
        result = json.loads(response_content)
        answer = result["answer"].strip()
    except (json.JSONDecodeError, KeyError, TypeError):
        raise ValueError(
            "The AI model did not return a valid structured answer."
        )

    if not answer:
        raise ValueError("The AI model returned an empty answer.")

    return answer







def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector using the configured embedding model."""

    response = client.embed(
        model=settings.OLLAMA_EMBEDDING_MODEL,
        input=text
    )

    return response["embeddings"][0]


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple text chunks in one request."""

    response = client.embed(
        model=settings.OLLAMA_EMBEDDING_MODEL,
        input=texts
    )

    return response["embeddings"]

