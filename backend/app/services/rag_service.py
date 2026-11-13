
from app.services.retrieval_service import search_similar_chunks
from app.services.ollama_service import generate_answer


def answer_question(question: str) -> dict:
    """Answer a question using relevant PDF content."""

    # 1. Retrieve relevant chunks from Qdrant
    retrieved_chunks = search_similar_chunks(
        query=question,
        limit=5
    )

    if not retrieved_chunks:
        return {
            "answer": "No relevant information found in the uploaded documents.",
            "sources": []
        }

    # 2. Prepare context from retrieved chunks
    context = "\n\n".join(
        f"Source: {chunk['filename']}, Page: {chunk['page_number']}\n"
        f"{chunk['text']}"
        for chunk in retrieved_chunks
    )

    
    
    
    prompt = f"""
You are a professional document question-answering assistant.

Answer the question using ONLY the provided context.

Rules:
1. Give only the information needed to answer the question.
2. Keep the answer within 1-3 sentences.
3. Do not include your reasoning or analysis.
4. Never invent missing information.
5. If the requested information is missing or represented by an unfilled placeholder, return exactly:
"The requested information is not specified in the uploaded document."

Context:
{context}

Question:
{question}
"""


  

    # 4. Generate answer using the chat model
    answer = generate_answer(prompt)

    # 5. Prepare source references
    sources = [
        {
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "score": round(chunk["score"], 3)
        }
        for chunk in retrieved_chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }
