"""
RAG (Retrieval-Augmented Generation) service.

Combines vector store retrieval with LLM to answer queries
using relevant context from the knowledge base.
"""

from typing import Any, Dict, Optional

from app.infrastructure.vectorstores.pinecone_client import (
    VectorStoreClient,
    get_vectorstore_client,
)
from app.infrastructure.clients.openai_client import OpenAIClient, get_openai_client


# Module-level cache for RagService singleton
_rag_service: Optional["RagService"] = None


class RagService:
    """
    Service for answering queries using RAG (Retrieval-Augmented Generation).

    Retrieves relevant documents from the vector store and uses LLM
    to generate contextual answers.
    """

    def __init__(
        self,
        vectorstore_client: VectorStoreClient,
        openai_client: Optional[OpenAIClient] = None,
    ) -> None:
        """
        Initialize the RAG service.

        Args:
            vectorstore_client: Client for vector store operations.
            openai_client: OpenAI client for LLM calls. If None, uses singleton.
        """
        self._vectorstore = vectorstore_client
        self._openai_client = openai_client or get_openai_client()

    def answer(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answer a query using retrieval-augmented generation.

        Args:
            query: The user's question
            top_k: Number of relevant documents to retrieve for context

        Returns:
            Dictionary containing:
                - "answer": str - The generated answer
                - "tags": List[str] - Extracted tags/categories
                - "confidence": str - Confidence level (high/medium/low)
                - "sources": List[Dict[str, Any]] - Retrieved source documents
        """
        # Retrieve relevant documents from vector store
        matches = self._vectorstore.query_similar(query, top_k=top_k)

        # Build context chunks from retrieved documents
        context_chunks = []
        for idx, match in enumerate(matches, 1):
            text = match.get("metadata", {}).get("text", "")
            if text:
                context_chunks.append(f"Document {idx}:\n{text}")

        # Use OpenAI client to generate answer WITH tags
        rag_result = self._openai_client.generate_rag_response(
            query=query, context_chunks=context_chunks
        )

        # Format sources
        sources = []
        for match in matches:
            sources.append(
                {
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "metadata": match.get("metadata", {}),
                }
            )

        # Return combined result with answer, tags, confidence, and sources
        return {
            "answer": rag_result.get("answer", ""),
            "tags": rag_result.get("tags", []),
            "confidence": rag_result.get("confidence", "low"),
            "sources": sources,
        }


def get_rag_service() -> RagService:
    """
    Return a singleton instance of RagService.

    Initializes the service on first call using the vectorstore client
    and caches it for subsequent calls.

    Returns:
        RagService: The singleton RAG service instance
    """

    global _rag_service

    if _rag_service is None:
        vectorstore_client = get_vectorstore_client()
        _rag_service = RagService(vectorstore_client)

    return _rag_service
