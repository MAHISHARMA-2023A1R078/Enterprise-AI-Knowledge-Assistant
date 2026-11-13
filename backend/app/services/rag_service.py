
from app.services.retrieval_service import search_similar_chunks
from app.services.ollama_service import generate_answer


def answer_question(question: str) -> dict:
    """Answer a question using relevant PDF content."""

    # 1. Retrieve relevant chunks from Qdrant
    retrieved_chunks = search_similar_chunks(
        query=question,
        limit=10
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
1. Answer the exact question directly using relevant information from the context.
2. Keep the answer concise, preferably within 1-3 sentences.
3. Do not include reasoning, analysis, or unrelated details.
4. Never invent, assume, or infer information that is not explicitly supported by the context.
5. Distinguish between general document information and specific filled-in details.
6. If a field contains a blank, placeholder, or is left unfilled, treat that specific information as not specified.
7. If some parts of the answer are available and others are missing, provide the available information and clearly mention what is missing. Do not reject the entire answer.
8. For questions about parties, include their names when explicitly available. If a party's name is not filled in, mention its role and clarify that its name is not specified.
9. For questions about the loan purpose, distinguish the facility or agreement type from the specific purpose entered in the agreement.
10. Do not confuse the agreement title with a completed field in the agreement.

If the requested information is entirely missing, return exactly:
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
