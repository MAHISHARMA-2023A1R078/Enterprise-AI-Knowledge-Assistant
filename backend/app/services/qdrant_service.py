
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import settings
from uuid import uuid4
from qdrant_client.models import PointStruct

from app.services.ollama_service import generate_embeddings

# Connect to the Qdrant server
client = QdrantClient(url=settings.QDRANT_URL)


def initialize_collection():
    """Create the collection if it does not already exist."""

    collection_name = settings.QDRANT_COLLECTION

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE
            )
        )

        print(f"Collection '{collection_name}' created successfully.")

    else:
        print(f"Collection '{collection_name}' already exists.")



def store_chunks(
    chunks: list[dict],
    document_id: str,
    filename: str
) -> int:
    """Generate embeddings and store PDF chunks in Qdrant."""

    if not chunks:
        return 0

    # 1. Make sure the collection exists
    initialize_collection()

    # 2. Extract text from all chunks
    texts = [chunk["text"] for chunk in chunks]

    # 3. Generate embeddings using Ollama
    embeddings = generate_embeddings(texts)

    # 4. Create Qdrant points
    points = []

    for chunk, embedding in zip(chunks, embeddings):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"]
                }
            )
        )

    # 5. Store points in Qdrant
    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
        wait=True
    )

    return len(points)


def delete_document_chunks(document_id: str) -> None:
    """Delete all chunks belonging to a specific document from Qdrant."""

    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        ),
        wait=True
    )

