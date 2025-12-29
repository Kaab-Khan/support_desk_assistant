"""
Integration tests for RAG endpoint with conversation history.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app


class TestRagEndpointWithConversationHistory:
    """Integration tests for POST /api/v1/rag/query with conversation history."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.mark.integration
    def test_rag_query_without_conversation_history_real(self, client):
        """
        Test RAG query without conversation history (backward compatibility).
        
        Scenario: Submit a query without conversation history using real services.
        
        Expected behavior:
        - Returns 200 status code
        - Response contains answer and sources
        - Works as before (backward compatible)
        """
        # Arrange
        payload = {
            "query": "How do I reset my password?"
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        
        print(f"\n✅ Query without history: {data['answer'][:100]}...")

    @pytest.mark.integration
    def test_rag_query_with_conversation_history_real(self, client):
        """
        Test RAG query with conversation history using real services.
        
        Scenario: Submit a follow-up query with conversation history.
        
        Expected behavior:
        - Returns 200 status code
        - Response contains answer considering conversation context
        - Follow-up question is understood in context
        """
        # Arrange
        payload = {
            "query": "What about the second step?",
            "conversation_history": [
                {"role": "user", "content": "How do I reset my password?"},
                {"role": "assistant", "content": "Follow these steps: 1. Go to Settings 2. Click Reset Password 3. Check email"}
            ]
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        
        # The answer should reference or understand context
        print(f"\n✅ Query with history: {data['answer'][:100]}...")

    @pytest.mark.integration
    def test_rag_query_with_empty_conversation_history(self, client):
        """
        Test RAG query with empty conversation history list.
        
        Scenario: Submit query with empty history list.
        
        Expected behavior:
        - Returns 200 status code
        - Handles empty list gracefully
        """
        # Arrange
        payload = {
            "query": "How do I login?",
            "conversation_history": []
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)

    @pytest.mark.integration
    def test_rag_query_with_long_conversation_history(self, client):
        """
        Test RAG query with long conversation history.
        
        Scenario: Submit query with many previous messages.
        
        Expected behavior:
        - Returns 200 status code
        - System handles long history without errors
        - Token usage is managed (truncation happens in backend)
        """
        # Arrange - Create a long conversation
        long_history = []
        for i in range(10):
            long_history.append({"role": "user", "content": f"Question {i}?"})
            long_history.append({"role": "assistant", "content": f"Answer {i}"})
        
        payload = {
            "query": "What was my first question?",
            "conversation_history": long_history
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)

    @pytest.mark.integration
    @patch('app.core.services.rag_service.RagService.answer')
    def test_rag_query_passes_conversation_history_to_service(self, mock_answer, client):
        """
        Test that endpoint correctly passes conversation history to RAG service.
        
        Scenario: Verify the data flow from endpoint to service.
        
        Expected behavior:
        - Endpoint receives conversation history
        - Passes it to RAG service.answer() method
        """
        # Arrange
        mock_answer.return_value = {
            "answer": "Test answer",
            "tags": ["test"],
            "confidence": "high",
            "sources": []
        }
        
        payload = {
            "query": "Test query",
            "conversation_history": [
                {"role": "user", "content": "Previous question"},
                {"role": "assistant", "content": "Previous answer"}
            ]
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 200
        
        # Verify RAG service was called with conversation history
        mock_answer.assert_called_once()
        call_kwargs = mock_answer.call_args.kwargs
        
        assert call_kwargs["query"] == "Test query"
        assert call_kwargs["conversation_history"] is not None
        assert len(call_kwargs["conversation_history"]) == 2

    @pytest.mark.integration
    def test_rag_query_invalid_conversation_history_format(self, client):
        """
        Test RAG query with invalid conversation history format.
        
        Scenario: Submit query with malformed conversation history.
        
        Expected behavior:
        - Returns 422 validation error
        - Error message indicates invalid format
        """
        # Arrange - Missing 'role' field
        payload = {
            "query": "Test query",
            "conversation_history": [
                {"content": "Missing role field"}
            ]
        }
        
        # Act
        response = client.post("/api/v1/rag/query", json=payload)
        
        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_multiple_sequential_queries_with_building_history(self, client):
        """
        Test multiple sequential queries simulating a conversation.
        
        Scenario: Simulate a real conversation with multiple turns.
        
        Expected behavior:
        - Each query succeeds
        - History grows with each turn
        - System maintains context across queries
        """
        conversation_history = []
        
        # Turn 1
        payload1 = {"query": "How do I reset my password?"}
        response1 = client.post("/api/v1/rag/query", json=payload1)
        assert response1.status_code == 200
        answer1 = response1.json()["answer"]
        
        conversation_history.append({"role": "user", "content": payload1["query"]})
        conversation_history.append({"role": "assistant", "content": answer1})
        
        # Turn 2 - Follow-up with history
        payload2 = {
            "query": "What if I don't have access to my email?",
            "conversation_history": conversation_history
        }
        response2 = client.post("/api/v1/rag/query", json=payload2)
        assert response2.status_code == 200
        answer2 = response2.json()["answer"]
        
        conversation_history.append({"role": "user", "content": payload2["query"]})
        conversation_history.append({"role": "assistant", "content": answer2})
        
        # Turn 3 - Another follow-up
        payload3 = {
            "query": "Can you clarify that?",
            "conversation_history": conversation_history
        }
        response3 = client.post("/api/v1/rag/query", json=payload3)
        assert response3.status_code == 200
        
        print(f"\n✅ Multi-turn conversation successful: {len(conversation_history)} messages")
