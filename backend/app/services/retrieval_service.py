
import re

from app.config import settings
from app.services.ollama_service import generate_embedding
from app.services.qdrant_service import client


STOPWORDS = {
    "what", "is", "the", "of", "a", "an", "in", "on",
    "to", "for", "and", "or", "was", "are", "were",
    "do", "does", "did", "please", "tell", "me"
}


def tokenize(text: str) -> set[str]:
    """Convert text into lowercase searchable words."""
    words = re.findall(r"\b[a-z0-9]+\b", text.lower())
    return set(words) - STOPWORDS


def get_all_chunks() -> list[dict]:
    """Retrieve all stored document chunks using pagination."""

    all_chunks = []
    offset = None

    while True:
        points, next_offset = client.scroll(
            collection_name=settings.QDRANT_COLLECTION,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        for point in points:
            payload = point.payload or {}

            if not payload.get("text"):
                continue

            all_chunks.append({
                "document_id": payload.get("document_id"),
                "filename": payload.get("filename"),
                "page_number": payload.get("page_number"),
                "chunk_index": payload.get("chunk_index"),
                "text": payload.get("text")
            })

        if next_offset is None:
            break

        offset = next_offset

    return all_chunks


def search_document_title(query: str) -> list[dict]:
    """Find document heading chunks for title-related questions."""

    title_question = re.search(
    r"\b(name|title)\s+of\s+(the\s+|this\s+)?(agreement|document|contract)\b"
    r"|\b(what\s+is\s+)?(the\s+)?(agreement|document|contract)\s+(called|titled)\b",
    query.lower()
)

    if not title_question:
        return []

    all_chunks = get_all_chunks()
    title_results = []

    for chunk in all_chunks:
        if chunk.get("page_number") != 1:
            continue

        lines = [
            line.strip()
            for line in chunk["text"].splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        first_line = lines[0]

        # Match a clear document heading.
        if (
            re.search(r"\b(agreement|contract)\b", first_line, re.I)
            and first_line.upper() == first_line
        ):
            chunk["score"] = 1.0
            chunk["rrf_score"] = 1.0
            title_results.append(chunk)

    return title_results


def search_similar_chunks(
    query: str,
    limit: int = 5
) -> list[dict]:

    # 1. Dedicated document-title retrieval
    title_results = search_document_title(query)

    if title_results:
        return title_results[:limit]

    # 2. Dense/vector retrieval
    query_vector = generate_embedding(query)

    response = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=20,
        with_payload=True
    )

    dense_results = []

    for point in response.points:
        payload = point.payload or {}

        if not payload.get("text"):
            continue

        dense_results.append({
            "score": point.score,
            "document_id": payload.get("document_id"),
            "filename": payload.get("filename"),
            "page_number": payload.get("page_number"),
            "chunk_index": payload.get("chunk_index"),
            "text": payload.get("text")
        })

    # 3. Independent keyword retrieval
    all_chunks = get_all_chunks()
    query_words = tokenize(query)

    keyword_results = []

    for chunk in all_chunks:
        chunk_words = tokenize(chunk["text"])

        if not query_words:
            continue

        matched_words = query_words & chunk_words

        if not matched_words:
            continue

        keyword_score = len(matched_words) / len(query_words)

        chunk["keyword_score"] = keyword_score
        keyword_results.append(chunk)

    keyword_results.sort(
        key=lambda item: item["keyword_score"],
        reverse=True
    )

    # 4. Combine rankings using Reciprocal Rank Fusion
    combined = {}

    def chunk_key(item):
        return (
            item.get("filename"),
            item.get("page_number"),
            item.get("chunk_index"),
            item.get("text")
        )

    for rank, item in enumerate(dense_results, start=1):
        key = chunk_key(item)

        if key not in combined:
            combined[key] = {
                **item,
                "rrf_score": 0.0
            }

        combined[key]["rrf_score"] += 1 / (60 + rank)

    for rank, item in enumerate(keyword_results, start=1):
        key = chunk_key(item)

        if key not in combined:
            combined[key] = {
                **item,
                "score": 0.0,
                "rrf_score": 0.0
            }

        combined[key]["rrf_score"] += 1 / (60 + rank)

    # 5. Sort and return top unique chunks
    results = sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    return results[:limit]
