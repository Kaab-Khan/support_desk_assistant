"""
Integration tests for RAG Service end-to-end functionality.

These tests verify the complete RAG workflow with real external services:
1. Real Pinecone vector database queries
2. Real OpenAI API calls for answer generation
3. Complete RAG service flow (retrieval + generation)
4. RAG service singleton behavior
5. Error handling with real services
6. API endpoint integration

Note: These tests hit REAL APIs and require:
- Valid OPENAI_API_KEY in .env
- Valid PINECONE_API_KEY in .env
- Valid PINECONE_INDEX_NAME in .env
- Documents already ingested in Pinecone
- These tests COST MONEY (minimal, but real API charges)
"""
import pytest
from fastapi.testclient import TestClient
from app.core.services.rag_service import RagService, get_rag_service
from app.infrastructure.vectorstores.pinecone_client import get_vectorstore_client
from app.infrastructure.clients.openai_client import get_openai_client
from app.main import app
from app.config.settings import get_settings


class TestRagServiceIntegration:
    """Integration tests for RAG Service with real Pinecone and OpenAI."""

    @pytest.fixture
    def rag_service(self):
        """Get real RAG service instance (not mocked)."""
        return get_rag_service()

    @pytest.fixture
    def vectorstore_client(self):
        """Get real vectorstore client (not mocked)."""
        return get_vectorstore_client()

    @pytest.fixture
    def openai_client(self):
        """Get real OpenAI client (not mocked)."""
        return get_openai_client()

    @pytest.mark.integration
    def test_end_to_end_rag_query_with_real_services(self, rag_service):
        """
        Test complete RAG workflow with real Pinecone and OpenAI.
        
        Scenario: User asks a question that should have relevant docs
        in the knowledge base. The system should:
        1. Query Pinecone for relevant documents
        2. Retrieve context from vector database
        3. Generate answer using OpenAI with that context
        4. Return answer with sources
        
        Expected behavior:
        - Query returns relevant documents from Pinecone
        - OpenAI generates a coherent answer based on context
        - Response includes answer string and sources list
        - Sources contain document metadata
        - Answer is not "INSUFFICIENT_CONTEXT"
        """
        # Arrange
        query = "How do I reset my password?"
        
        # Act
        result = rag_service.answer(query=query, top_k=5)
        
        # Assert - Check response structure
        assert "answer" in result
        assert "sources" in result
        
        # Assert - Answer should be a non-empty string
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0
        
        # Assert - Answer should not be insufficient context for common query
        assert result["answer"] != "INSUFFICIENT_CONTEXT"
        
        # Assert - Sources should be a list
        assert isinstance(result["sources"], list)
        
        # Assert - Sources should contain documents (if knowledge base has data)
        # Note: This assumes your Pinecone index has documents
        if len(result["sources"]) > 0:
            # Check first source has expected structure
            first_source = result["sources"][0]
            assert "id" in first_source
            assert "score" in first_source
            assert "metadata" in first_source
            
            # Check metadata has text content
            assert isinstance(first_source["metadata"], dict)
            
            # Score should be a float between 0 and 1
            assert isinstance(first_source["score"], (int, float))
        
        print(f"\n✅ RAG end-to-end query successful")
        print(f"Query: {query}")
        print(f"Answer length: {len(result['answer'])} characters")
        print(f"Sources found: {len(result['sources'])}")
        print(f"Answer preview: {result['answer'][:100]}...")

    @pytest.mark.integration
    def test_rag_service_with_technical_query(self, rag_service):
        """
        Test RAG service with a technical support query.
        
        Scenario: User asks a technical question about the product/service.
        
        Expected behavior:
        - System retrieves relevant technical documentation
        - OpenAI generates helpful technical answer
        - Response includes technical details from knowledge base
        """
        # Arrange
        query = "What are the system requirements?"
        
        # Act
        result = rag_service.answer(query=query, top_k=3)
        
        # Assert
        assert "answer" in result
        assert "sources" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0
        
        print(f"\n✅ Technical query processed")
        print(f"Query: {query}")
        print(f"Answer: {result['answer'][:150]}...")

    @pytest.mark.integration
    def test_rag_service_with_query_not_in_knowledge_base(self, rag_service):
        """
        Test RAG service when query has no relevant documents.
        
        Scenario: User asks about something not covered in knowledge base.
        
        Expected behavior:
        - Pinecone returns no relevant documents (or low scores)
        - OpenAI should return "INSUFFICIENT_CONTEXT" or indicate it can't answer
        - Sources list may be empty or have low-score matches
        """
        # Arrange
        query = "How do I configure the quantum flux capacitor for time travel?"
        
        # Act
        result = rag_service.answer(query=query, top_k=5)
        
        # Assert
        assert "answer" in result
        assert "sources" in result
        
        # Answer should indicate insufficient context
        # (Either INSUFFICIENT_CONTEXT or a message about not finding info)
        answer_lower = result["answer"].lower()
        assert (
            "insufficient" in answer_lower or
            "cannot" in answer_lower or
            "don't have" in answer_lower or
            "not found" in answer_lower or
            result["answer"] == "INSUFFICIENT_CONTEXT"
        )
        
        print(f"\n✅ Out-of-scope query handled correctly")
        print(f"Query: {query}")
        print(f"Answer: {result['answer']}")

    @pytest.mark.integration
    def test_rag_service_with_different_top_k_values(self, rag_service):
        """
        Test RAG service with different numbers of retrieved documents.
        
        Scenario: Test with top_k=1, top_k=3, top_k=10 to verify
        the service handles different context sizes.
        
        Expected behavior:
        - All queries complete successfully
        - Answers may vary based on amount of context
        - No errors with different top_k values
        """
        # Arrange
        query = "How do I update my profile information?"
        
        # Act & Assert for different top_k values
        for top_k in [1, 3, 10]:
            result = rag_service.answer(query=query, top_k=top_k)
            
            assert "answer" in result
            assert "sources" in result
            assert isinstance(result["answer"], str)
            assert len(result["sources"]) <= top_k
            
            print(f"\n✅ Query with top_k={top_k} successful")
            print(f"Sources retrieved: {len(result['sources'])}")

    @pytest.mark.integration
    def test_rag_service_singleton_behavior(self):
        """
        Test that get_rag_service() returns the same instance.
        
        Scenario: Call get_rag_service() multiple times.
        
        Expected behavior:
        - Same instance is returned (singleton pattern)
        - Service is initialized only once
        - Reduces overhead of recreating clients
        """
        # Act
        service1 = get_rag_service()
        service2 = get_rag_service()
        service3 = get_rag_service()
        
        # Assert - All references point to same instance
        assert service1 is service2
        assert service2 is service3
        assert service1 is service3
        
        print("\n✅ RAG service singleton pattern verified")

    @pytest.mark.integration
    def test_rag_service_with_vectorstore_and_openai_separately(
        self,
        vectorstore_client,
        openai_client
    ):
        """
        Test RAG service initialization with explicit dependencies.
        
        Scenario: Create RAG service by passing vectorstore and OpenAI clients.
        
        Expected behavior:
        - Service initializes with provided clients
        - Service can execute queries successfully
        - Dependencies are properly injected
        """
        # Arrange
        rag_service = RagService(
            vectorstore_client=vectorstore_client,
            openai_client=openai_client
        )
        
        query = "What is your return policy?"
        
        # Act
        result = rag_service.answer(query=query, top_k=5)
        
        # Assert
        assert "answer" in result
        assert "sources" in result
        assert isinstance(result["answer"], str)
        
        print("\n✅ RAG service with explicit dependencies works")

    @pytest.mark.integration
    def test_rag_service_retrieves_correct_metadata(self, rag_service):
        """
        Test that RAG service returns proper document metadata.
        
        Scenario: Execute a query and verify retrieved sources
        have complete metadata.
        
        Expected behavior:
        - Sources include id, score, and metadata
        - Metadata contains text snippets
        - Metadata may contain source document names
        """
        # Arrange
        query = "How do I contact support?"
        
        # Act
        result = rag_service.answer(query=query, top_k=5)
        
        # Assert
        assert "sources" in result
        sources = result["sources"]
        
        if len(sources) > 0:
            for source in sources:
                # Each source must have these fields
                assert "id" in source
                assert "score" in source
                assert "metadata" in source
                
                # Metadata should be a dictionary
                assert isinstance(source["metadata"], dict)
                
                # Score should be numeric
                assert isinstance(source["score"], (int, float))
                
            print(f"\n✅ Retrieved {len(sources)} sources with proper metadata")
            print(f"Sample source ID: {sources[0]['id']}")
            print(f"Sample score: {sources[0]['score']}")
            print(f"Sample metadata keys: {list(sources[0]['metadata'].keys())}")

    @pytest.mark.integration
    def test_rag_service_performance_reasonable_response_time(self, rag_service):
        """
        Test that RAG service responds in reasonable time.
        
        Scenario: Execute a query and measure response time.
        
        Expected behavior:
        - Query completes within reasonable time (< 10 seconds)
        - No timeouts
        - Service is responsive
        
        Note: Actual time depends on network latency and API response times.
        """
        import time
        
        # Arrange
        query = "How do I change my email address?"
        
        # Act
        start_time = time.time()
        result = rag_service.answer(query=query, top_k=5)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # Assert
        assert "answer" in result
        assert elapsed_time < 10.0, f"Query took too long: {elapsed_time:.2f}s"
        
        print(f"\n✅ RAG query completed in {elapsed_time:.2f} seconds")


class TestRagAPIEndpointIntegration:
    """Integration tests for /api/v1/rag/query endpoint."""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        return TestClient(app)

    @pytest.mark.integration
    def test_rag_query_endpoint_with_valid_request(self, client):
        """
        Test POST /api/v1/rag/query with valid request.
        
        Scenario: User sends a valid query to RAG endpoint.
        
        Expected behavior:
        - Returns 200 status code
        - Response contains answer and sources
        - Answer is a non-empty string
        - Sources is a list of documents with doc_name and snippet
        """
        # Arrange
        payload = {
            "query": "How do I reset my password?"
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert - Check status code
        assert response.status_code == 200
        
        # Assert - Check response structure
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        
        # Assert - Check answer
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        
        # Assert - Check sources structure
        assert isinstance(data["sources"], list)
        
        if len(data["sources"]) > 0:
            first_source = data["sources"][0]
            assert "doc_name" in first_source
            assert "snippet" in first_source
            assert isinstance(first_source["doc_name"], str)
            assert isinstance(first_source["snippet"], str)
        
        print(f"\n✅ RAG API endpoint returned valid response")
        print(f"Answer preview: {data['answer'][:100]}...")
        print(f"Sources count: {len(data['sources'])}")

    @pytest.mark.integration
    def test_rag_query_endpoint_with_empty_query(self, client):
        """
        Test POST /api/v1/rag/query with empty query.
        
        Scenario: User sends empty query string.
        
        Expected behavior:
        - Returns 422 validation error (or handles gracefully)
        """
        # Arrange
        payload = {
            "query": ""
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert - Should return validation error or handle gracefully
        # Depending on your validation logic
        assert response.status_code in [200, 422, 400]
        
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data
            print("\n✅ Empty query properly validated")
        else:
            print("\n✅ Empty query handled gracefully")

    @pytest.mark.integration
    def test_rag_query_endpoint_with_missing_query_field(self, client):
        """
        Test POST /api/v1/rag/query with missing required field.
        
        Scenario: User sends request without 'query' field.
        
        Expected behavior:
        - Returns 422 validation error
        - Error details indicate missing field
        """
        # Arrange
        payload = {
            "wrong_field": "This should fail"
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        print("\n✅ Missing field validation works")

    @pytest.mark.integration
    def test_rag_query_endpoint_with_long_query(self, client):
        """
        Test POST /api/v1/rag/query with very long query.
        
        Scenario: User sends a query with thousands of characters.
        
        Expected behavior:
        - System handles long query without crashing
        - Returns response (may truncate or handle appropriately)
        """
        # Arrange
        long_query = "How do I reset my password? " * 200  # Very long query
        payload = {
            "query": long_query
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert - Should not crash
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            print("\n✅ Long query handled successfully")
        else:
            print(f"\n✅ Long query rejected with status {response.status_code}")

    @pytest.mark.integration
    def test_rag_query_endpoint_with_special_characters(self, client):
        """
        Test POST /api/v1/rag/query with special characters.
        
        Scenario: User sends query with special characters, unicode, emojis.
        
        Expected behavior:
        - System handles special characters properly
        - Returns valid response
        - No encoding errors
        """
        # Arrange
        payload = {
            "query": "How do I reset my password? 🔒 (français: réinitialiser) <special&chars>"
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        
        print("\n✅ Special characters handled properly")

    @pytest.mark.integration
    def test_rag_query_endpoint_response_format_matches_schema(self, client):
        """
        Test that RAG endpoint response matches defined schema.
        
        Scenario: Execute query and verify response format.
        
        Expected behavior:
        - Response matches RagQueryResponse schema
        - All required fields present
        - Field types are correct
        """
        # Arrange
        payload = {
            "query": "What are the payment methods?"
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check response schema
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        
        # Check each source follows RagSource schema
        for source in data["sources"]:
            assert "doc_name" in source
            assert "snippet" in source
            assert isinstance(source["doc_name"], str)
            assert isinstance(source["snippet"], str)
        
        print("\n✅ Response format matches schema")

    @pytest.mark.integration
    def test_rag_query_endpoint_with_wrong_data_type(self, client):
        """
        Test POST /api/v1/rag/query with wrong data type for query field.
        
        Scenario: User sends integer instead of string for 'query'.
        
        Expected behavior:
        - Returns 422 validation error
        - Error details indicate type mismatch
        - Does not crash the server
        """
        # Arrange
        payload = {
            "query": 12345  # Integer instead of string
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        print("\n✅ Wrong data type validation works")
    @pytest.mark.skip(reason="Skipping due to potential DoS with extremely long query")
    @pytest.mark.integration
    def test_rag_query_endpoint_with_extremely_long_query(self, client):
        """
        Test POST /api/v1/rag/query with extremely long query (potential DoS).
        
        Scenario: User sends query with 1MB of text.
        
        Expected behavior:
        - System handles gracefully (accepts or rejects with 422)
        - Does not crash or hang
        - Returns response within reasonable time
        """
        # Arrange - Create 1MB query (potential DoS attack)
        long_query = "a" * (1024 * 1024)  # 1 MB of 'a's
        payload = {
            "query": long_query
        }
        
        # Act
        import time
        start_time = time.time()
        response = client.post("/api/v1/rag/query", json=payload)
        elapsed_time = time.time() - start_time
        
        # Assert - Should handle gracefully (either accept or reject)
        assert response.status_code in [200, 422, 413]  # OK, Validation Error, or Payload Too Large
        
        # Assert - Should respond quickly (not hang)
        assert elapsed_time < 30.0, f"Request took too long: {elapsed_time:.2f}s"
        
        if response.status_code == 422:
            print("\n✅ Extremely long query rejected with 422")
        elif response.status_code == 413:
            print("\n✅ Extremely long query rejected with 413 (Payload Too Large)")
        else:
            print(f"\n✅ Extremely long query handled (response in {elapsed_time:.2f}s)")
