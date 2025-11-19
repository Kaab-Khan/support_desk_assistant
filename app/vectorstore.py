"""
Pinecone vector store management.

Provides a client for managing document embeddings and similarity search
using Pinecone as the cloud vector store and OpenAI for embeddings.
"""

from typing import Any, Dict, List, Optional

from openai import OpenAI
from pinecone import Pinecone, Index, ServerlessSpec

from app.config import get_settings


# Module-level cache for VectorStoreClient singleton
_vectorstore_client: Optional["VectorStoreClient"] = None


class VectorStoreClient:
    """
    Client for managing Pinecone vector store operations.
    
    Handles initialization of Pinecone client, index management,
    document upsertion, and similarity search queries.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Pinecone vector store client.
        
        - Load settings (API keys, index name, etc.)
        - Initialize Pinecone client
        - Connect to or create the Pinecone index
        - Set up OpenAI embeddings
        """
        settings = get_settings()
        
        # Initialize Pinecone client
        self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Initialize OpenAI client
        self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Embedding model configuration
        self._embedding_model = "text-embedding-ada-002"
        self._dimension = 1536
        
        # Get or create index
        index_name = settings.PINECONE_INDEX_NAME

        # Check if index exists and create if needed
        if not self._pc.has_index(index_name):
            self._pc.create_index(
                name=index_name,
                dimension=self._dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1",
                ),
            )
        
        # Connect to index
        self._index: Index = self._pc.Index(index_name)
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each a list of floats)
        """
        response = self._openai_client.embeddings.create(
            model=self._embedding_model,
            input=texts,
        )
        
        return [item.embedding for item in response.data]
    
    def upsert_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Upsert documents into the Pinecone vector store.
        
        Args:
            texts: List of text documents to embed and store
            metadatas: Optional list of metadata dictionaries for each document
            ids: Optional list of unique IDs for each document
            
        - Generate embeddings using OpenAI
        - Upsert vectors with metadata into Pinecone index
        """
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc-{i}" for i in range(len(texts))]
        
        # Use empty dicts if metadatas not provided
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # Generate embeddings
        embeddings = self._embed_texts(texts)
        
        # Build vectors for upsert
        vectors = []
        for doc_id, embedding, text, metadata in zip(ids, embeddings, texts, metadatas):
            # Merge text into metadata
            full_metadata = {**metadata, "text": text}
            vectors.append(
                {
                    "id": doc_id,
                    "values": embedding,
                    "metadata": full_metadata,
                }
            )
        
        # Upsert to Pinecone
        self._index.upsert(vectors=vectors)
    
    def query_similar(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query for similar documents using semantic search.
        
        Args:
            query: The query text to search for
            top_k: Number of most similar documents to return
            filter: Optional metadata filter for the search
            
        Returns:
            List of matches with scores and metadata
            
        - Generate query embedding using OpenAI
        - Perform similarity search in Pinecone
        - Return formatted results with text and metadata
        """
        # Generate query embedding
        query_embedding = self._embed_texts([query])[0]
        
        # Query Pinecone
        query_params: Dict[str, Any] = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True,
        }
        
        if filter is not None:
            query_params["filter"] = filter
        
        results = self._index.query(**query_params)
        
        # Format results
        matches: List[Dict[str, Any]] = []
        for match in results.matches:
            matches.append(
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata,
                }
            )
        
        return matches


def get_vectorstore_client() -> VectorStoreClient:
    """
    Return a singleton instance of VectorStoreClient.
    
    Initializes the client on first call and caches it for subsequent calls.
    
    Returns:
        VectorStoreClient: The singleton vector store client instance
    """
    global _vectorstore_client
    
    if _vectorstore_client is None:
        _vectorstore_client = VectorStoreClient()
    
    return _vectorstore_client
