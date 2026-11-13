
from fastapi import FastAPI
from app.routes import health, documents, chat

app = FastAPI(
    title="Enterprise AI Knowledge Assistant",
    description="A RAG-based application for querying PDF documents",
    version="1.0.0"
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Enterprise AI Knowledge Assistant"
    }
