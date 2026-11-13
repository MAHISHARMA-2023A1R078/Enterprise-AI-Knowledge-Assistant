
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])


# Request body validation
class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question about the uploaded PDF documents"
    )


@router.post("/")
def chat(request: ChatRequest):

    try:
        result = answer_question(request.question)
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(error)}"
        )
