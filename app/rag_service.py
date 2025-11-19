"""
RAG (Retrieval-Augmented Generation) service.

Combines vector store retrieval with OpenAI LLM to answer queries
using relevant context from the knowledge base.
"""

from typing import Any, Dict, List, Optional

from openai import OpenAI

from app.config import get_settings
from app.vectorstore import VectorStoreClient, get_vectorstore_client


# Module-level cache for RagService singleton
_rag_service: Optional["RagService"] = None


class RagService:
    """
    Service for answering queries using RAG (Retrieval-Augmented Generation).
    
    Retrieves relevant documents from the vector store and uses OpenAI LLM
    to generate contextual answers.
    """
    
    def __init__(
        self,
        vectorstore_client: VectorStoreClient,
        model_name: Optional[str] = None
    ) -> None:
        """
        Initialize the RAG service.
        
        Args:
            vectorstore_client: Client for vector store operations
            model_name: OpenAI model name to use for generation (e.g., 'gpt-4', 'gpt-3.5-turbo')
            
        - Store the vectorstore client reference
        - Store the model name for OpenAI calls
        - Initialize any required OpenAI client configuration
        """
        self._vectorstore = vectorstore_client
        self._model_name = model_name if model_name is not None else "gpt-4o-mini"
        
        # Initialize OpenAI client
        settings = get_settings()
        self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def answer(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a query using retrieval-augmented generation.
        
        Args:
            query: The user's question
            top_k: Number of relevant documents to retrieve for context
            
        Returns:
            Dictionary containing:
                - "answer": str - The generated answer
                - "sources": List[Dict[str, Any]] - Retrieved source documents
                    Each source contains snippet text and metadata
                    
        - Use vectorstore_client to retrieve top_k relevant documents
        - Construct a prompt with query + retrieved context
        - Call OpenAI API to generate answer
        - Format and return response with answer and sources
        """
        # Retrieve relevant documents from vector store
        matches = self._vectorstore.query_similar(query, top_k=top_k)
        
        # Build context from retrieved documents
        context_parts = []
        for idx, match in enumerate(matches, 1):
            text = match.get("metadata", {}).get("text", "")
            if text:
                context_parts.append(f"Document {idx}:\n{text}")
        
        context = "\n\n".join(context_parts)
        
        # Construct chat messages
        system_message = (
            "You are a helpful AI support desk assistant. "
            "Answer the user's question using ONLY the provided context documents. "
            "If you cannot find the answer in the context, say you don't know. "
            "Be concise and accurate."
        )
        
        user_message = f"""Context:
{context}

Question: {query}

Answer based only on the context above:"""
        
        # Call OpenAI API
        response = self._openai_client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract answer
        answer = response.choices[0].message.content
        
        # Format sources
        sources = []
        for match in matches:
            sources.append({
                "id": match.get("id"),
                "score": match.get("score"),
                "metadata": match.get("metadata", {})
            })
        
        return {
            "answer": answer,
            "sources": sources
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
