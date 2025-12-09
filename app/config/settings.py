"""
Configuration management for the AI Support Desk Assistant.

Uses pydantic-settings to load environment variables and provide
application configuration as a singleton.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        OPENAI_API_KEY: OpenAI API key for LLM and embeddings
        PINECONE_API_KEY: Pinecone API key for vector store
        PINECONE_INDEX_NAME: Name of the Pinecone index
        DB_URL: SQLite database connection URL
        DOCS_DIR: Path to the documentation files directory
        VECTORSTORE_DIR: Path to the Chroma vectorstore persistence directory
    """

    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    DB_URL: str = "sqlite:///data/support.db"
    DOCS_DIR: str = "data/docs"
    VECTORSTORE_DIR: str = "data/vectorstore"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Return a singleton instance of Settings.

    Returns:
        Settings: The application configuration instance
    """
    return Settings()
