
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_and_chunk_pdf(file_path: str) -> list[dict]:
    # Step 1: Read the PDF
    reader = PdfReader(file_path)

    # Step 2: Extract text page by page
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page_number": page_number,
                "text": text
            })

    if not pages:
        raise ValueError("No readable text found in the PDF.")

    # Step 3: Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Step 4: Split extracted text into chunks
    chunks = []

    for page in pages:
        page_chunks = text_splitter.split_text(page["text"])

        for chunk_index, chunk in enumerate(page_chunks):
            chunks.append({
                "page_number": page["page_number"],
                "chunk_index": chunk_index,
                "text": chunk
            })

    return chunks
