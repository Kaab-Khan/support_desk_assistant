"""
Integration tests for Pinecone vector database connection.

These tests verify real Pinecone connectivity and functionality:
1. Pinecone connection works with real API keys
2. Index exists and is accessible
3. Documents can be queried and retrieved
4. Retrieved documents have correct format and content

Note: These tests hit the REAL Pinecone API and require:
- Valid PINECONE_API_KEY in .env
- Valid PINECONE_INDEX_NAME in .env
- Documents already ingested (139 vectors from 8 docs)
"""
import pytest
from app.infrastructure.vectorstores.pinecone_client import get_vectorstore_client
from app.config.settings import get_settings


class TestPineconeIntegration:
    """Integration tests for Pinecone vector database."""

    @pytest.fixture
    def vectorstore_client(self):
        """Get the real vectorstore client (not mocked)."""
        return get_vectorstore_client()

    @pytest.mark.integration
    def test_pinecone_client_initialization(self, vectorstore_client):
        """
        Test that Pinecone client initializes successfully.
        
        Scenario: Application starts and connects to Pinecone.
        
        Expected behavior:
        - Client instance is created
        - No connection errors
        - Index is accessible
        - Settings are loaded correctly
        """
        # Assert - Client exists and has required attributes
        assert vectorstore_client is not None
        assert hasattr(vectorstore_client, '_index')
        assert hasattr(vectorstore_client, '_pc')
        assert hasattr(vectorstore_client, '_openai_client')
        
        # Verify settings are loaded
        settings = get_settings()
        assert settings.PINECONE_API_KEY is not None
        assert settings.PINECONE_INDEX_NAME is not None
        assert len(settings.PINECONE_API_KEY) > 0
        assert len(settings.PINECONE_INDEX_NAME) > 0
        
        print(f"\n✅ Successfully connected to Pinecone index: {settings.PINECONE_INDEX_NAME}")

    @pytest.mark.integration
    def test_query_pinecone_returns_results(self, vectorstore_client):
        """
        Test querying Pinecone with a known topic from ingested documents.
        
        Scenario: Query for "password reset" which should exist in FAQ docs.
        
        Expected behavior:
        - Query executes without errors
        - Returns list of results
        - Results have proper structure (id, score, metadata)
        - At least one result has relevance score > 0.5
        """
        # Arrange
        query = "How do I reset my password?"
        top_k = 5
        
        # Act
        results = vectorstore_client.query_similar(query=query, top_k=top_k)
        
        # Assert - Results structure
        assert isinstance(results, list), "Results should be a list"
        assert len(results) > 0, "Should return at least one result"
        assert len(results) <= top_k, f"Should return at most {top_k} results"
        
        # Assert - First result structure
        first_result = results[0]
        assert "id" in first_result, "Result should have 'id' field"
        assert "score" in first_result, "Result should have 'score' field"
        assert "metadata" in first_result, "Result should have 'metadata' field"
        
        # Assert - Score quality (relevant match)
        assert first_result["score"] > 0.5, \
            f"Top result should have high relevance (> 0.5), got {first_result['score']:.4f}"
        
        # Assert - Metadata contains text
        metadata = first_result["metadata"]
        assert "text" in metadata, "Metadata should contain 'text' field"
        assert len(metadata["text"]) > 0, "Text should not be empty"
        
        print(f"\n✅ Query: '{query}'")
        print(f"✅ Returned {len(results)} results")
        print(f"✅ Top result score: {first_result['score']:.4f}")
        print(f"✅ Top result preview: {metadata['text'][:150]}...")

    @pytest.mark.integration
    def test_query_with_different_topics(self, vectorstore_client):
        """
        Test querying multiple topics from ingested documents.
        
        Scenario: Query various topics that should exist in the knowledge base
        (billing, API, troubleshooting, compliance, etc.)
        
        Expected behavior:
        - All queries return results
        - Each query returns relevant documents
        - No errors or timeouts
        - Scores indicate relevance
        """
        # Arrange - Different topics from your 8 ingested documents
        test_queries = [
            "How do I handle billing issues?",
            "What are the API integration steps?",
            "How to troubleshoot ticket problems?",
            "What is the incident response procedure?",
            "How do I comply with GDPR?"
        ]
        
        results_summary = []
        
        # Act & Assert - Test each query
        for query in test_queries:
            results = vectorstore_client.query_similar(query=query, top_k=3)
            
            # Assert each query returns results
            assert len(results) > 0, f"Query '{query}' should return results"
            
            # Assert results have reasonable relevance (not random)
            assert results[0]["score"] > 0.3, \
                f"Query '{query}' should have relevant results (score > 0.3), got {results[0]['score']:.4f}"
            
            results_summary.append({
                "query": query,
                "num_results": len(results),
                "top_score": results[0]["score"]
            })
        
        # Print summary
        print("\n✅ All topic queries successful:")
        for item in results_summary:
            query_preview = item['query'][:50] + "..." if len(item['query']) > 50 else item['query']
            print(f"   '{query_preview}' → {item['num_results']} results (score: {item['top_score']:.4f})")

    @pytest.mark.integration
    def test_pinecone_index_statistics(self, vectorstore_client):
        """
        Test that Pinecone index contains the expected number of vectors.
        
        Scenario: After ingestion, verify vectors are stored correctly.
        
        Expected behavior:
        - Index contains vectors (not empty)
        - Vector count matches expected count from ingestion (139 vectors)
        - Index dimensions are correct (1536 for OpenAI embeddings)
        """
        # Act - Get index stats
        index = vectorstore_client._index
        stats = index.describe_index_stats()
        
        # Assert - Index has vectors
        total_vectors = stats.total_vector_count
        assert total_vectors > 0, "Index should contain vectors after ingestion"
        
        # We ingested 139 chunks, so we should have at least that many
        expected_vectors = 139
        assert total_vectors >= expected_vectors, \
            f"Expected at least {expected_vectors} vectors from ingestion, got {total_vectors}"
        
        # Assert - Dimensions are correct for OpenAI embeddings
        dimension = stats.dimension
        assert dimension == 1536, f"Expected dimension 1536 (OpenAI ada-002), got {dimension}"
        
        print(f"\n✅ Pinecone Index Statistics:")
        print(f"   Total vectors: {total_vectors}")
        print(f"   Expected: {expected_vectors}")
        print(f"   Dimensions: {dimension}")
        print(f"   Namespaces: {stats.namespaces}")

    @pytest.mark.integration
    def test_query_returns_source_metadata(self, vectorstore_client):
        """
        Test that query results include proper source metadata.
        
        Scenario: Query documents and verify metadata includes source info.
        
        Expected behavior:
        - Results have metadata
        - Metadata includes 'source' field (document filename)
        - Metadata includes 'text' field (actual content)
        - Source names match ingested document names
        """
        # Arrange
        query = "What is the compliance procedure?"
        
        # Act
        results = vectorstore_client.query_similar(query=query, top_k=3)
        
        # Assert - At least one result
        assert len(results) > 0, "Should return results"
        
        # Assert - Check metadata structure for all results
        for i, result in enumerate(results):
            metadata = result["metadata"]
            
            # Should have source information
            assert "source" in metadata, f"Result {i} should have 'source' in metadata"
            assert isinstance(metadata["source"], str), "Source should be a string"
            assert len(metadata["source"]) > 0, "Source should not be empty"
            
            # Source should be a .txt filename (from our ingestion)
            assert metadata["source"].endswith(".txt"), \
                f"Source should be a .txt file, got: {metadata['source']}"
            
            # Should have text content
            assert "text" in metadata, f"Result {i} should have 'text' in metadata"
            assert isinstance(metadata["text"], str), "Text should be a string"
            assert len(metadata["text"]) > 10, "Text should be substantial (> 10 chars)"
        
        print(f"\n✅ All {len(results)} results have proper metadata:")
        for i, result in enumerate(results):
            source = result['metadata']['source']
            text_len = len(result['metadata']['text'])
            print(f"   {i+1}. Source: {source} (text length: {text_len} chars)")

    @pytest.mark.integration
    def test_query_with_no_expected_results(self, vectorstore_client):
        """
        Test querying with a topic that likely doesn't exist in documents.
        
        Scenario: Query for something not in knowledge base.
        
        Expected behavior:
        - Query executes without errors
        - May return results but with low relevance scores
        - System doesn't crash
        """
        # Arrange - Query about something not in our HelpDeskFlow docs
        query = "How do I bake a chocolate cake?"
        
        # Act
        results = vectorstore_client.query_similar(query=query, top_k=3)
        
        # Assert - Query completes successfully
        assert isinstance(results, list), "Should return a list even if not relevant"
        
        # If results returned, they should have low scores (not relevant)
        if len(results) > 0:
            # Results exist but should have low relevance
            print(f"\n✅ Query returned {len(results)} results (likely not relevant)")
            print(f"   Top score: {results[0]['score']:.4f} (low = not relevant)")
        else:
            print(f"\n✅ Query returned no results (expected for unrelated topic)")
