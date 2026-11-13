
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, documents, chat

app = FastAPI(
    title="Enterprise AI Knowledge Assistant",
    description="A RAG-based application for querying PDF documents",
    version="1.0.0"
)

# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Enterprise AI Knowledge Assistant"
    }
