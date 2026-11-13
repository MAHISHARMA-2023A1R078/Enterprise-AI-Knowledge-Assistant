
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "qwen3:4b"
    OLLAMA_EMBEDDING_MODEL: str = "qwen3-embedding:0.6b"



     # Qdrant configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "pdf_documents"


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()


if __name__ == "__main__":
    print("Chat model:", settings.OLLAMA_CHAT_MODEL)
    print("Embedding model:", settings.OLLAMA_EMBEDDING_MODEL)
    print("Ollama:", settings.OLLAMA_BASE_URL)
    print("Qdrant:", settings.QDRANT_URL)
    print("Collection:", settings.QDRANT_COLLECTION)