
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4

from app.services.pdf_service import extract_and_chunk_pdf
from app.services.qdrant_service import store_chunks

router = APIRouter(prefix="/documents", tags=["Documents"])

# Upload directory
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # 1. Validate file extension
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # 2. Read uploaded file
    file_content = await file.read()

    if not file_content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    # 3. Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF size must not exceed 20 MB."
        )

    # 4. Generate a unique filename
    document_id = str(uuid4())
    file_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        # 5. Save PDF
        file_path.write_bytes(file_content)

        # 6. Extract text and create chunks
        chunks = extract_and_chunk_pdf(str(file_path))


        stored_points = store_chunks(
            chunks=chunks,
            document_id=document_id,
            filename=file.filename
        )

        return {
            "message": "PDF uploaded and processed successfully",
            "document_id": document_id,
            "filename": file.filename,
            "total_chunks": len(chunks),
            "stored_points": stored_points,
            "pages_processed": len(set(
                chunk["page_number"] for chunk in chunks
            )),
            "preview": chunks[0]["text"][:300]
        }

    except Exception as error:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=f"PDF processing failed: {str(error)}"
        )

    finally:
        await file.close()
