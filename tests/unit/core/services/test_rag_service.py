"""
Unit tests for RagService.answer() function.
"""
import pytest
from unittest.mock import Mock
from app.core.services.rag_service import RagService


class TestRagServiceAnswer:
    """Test suite for RagService.answer() method."""

    @pytest.fixture
    def mock_vectorstore_client(self):
        """Mock vectorstore client."""
        mock = Mock()
        return mock

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        mock = Mock()
        return mock

    @pytest.fixture
    def rag_service(self, mock_vectorstore_client, mock_openai_client):
        """Create RagService instance with mocked dependencies."""
        return RagService(
            vectorstore_client=mock_vectorstore_client,
            openai_client=mock_openai_client
        )

    @pytest.mark.unit
    def test_answer_with_relevant_documents_found(
        self,
        rag_service,
        mock_vectorstore_client,
        mock_openai_client
    ):
        """
        Test answer() when vectorstore finds relevant documents.
        
        Scenario: User asks a question, vectorstore returns relevant docs,
        OpenAI generates a helpful answer based on those docs.
        
        Expected behavior:
        - Vectorstore is queried with the question
        - Context chunks are built from retrieved documents
        - OpenAI generates answer using context
        - Returns answer and sources in correct format
        """
        # Arrange
        query = "How do I reset my password?"
        top_k = 5
        
        # Mock vectorstore response (relevant documents found)
        mock_vectorstore_client.query_similar.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {
                    "source": "user_guide.pdf",
                    "text": "To reset your password, navigate to Settings > Security."
                }
            },
            {
                "id": "doc2",
                "score": 0.87,
                "metadata": {
                    "source": "faq.pdf",
                    "text": "Password reset requires email verification."
                }
            }
        ]
        
        # Mock OpenAI response (now returns dict with answer, tags, confidence)
        mock_openai_client.generate_rag_response.return_value = {
            "answer": "To reset your password, go to Settings > Security > Reset Password. "
                     "You will need to verify your email address.",
            "tags": ["password-reset", "authentication"],
            "confidence": "high"
        }
        
        # Act
        result = rag_service.answer(query=query, top_k=top_k)
        
        # Assert - Check return structure
        assert "answer" in result
        assert "tags" in result
        assert "confidence" in result
        assert "sources" in result
        
        # Assert - Check answer content
        assert result["answer"] == (
            "To reset your password, go to Settings > Security > Reset Password. "
            "You will need to verify your email address."
        )
        
        # Assert - Check tags were extracted
        assert result["tags"] == ["password-reset", "authentication"]
        assert result["confidence"] == "high"
        
        # Assert - Check sources format
        assert len(result["sources"]) == 2
        assert result["sources"][0]["id"] == "doc1"
        assert result["sources"][0]["score"] == 0.95
        assert result["sources"][0]["metadata"]["source"] == "user_guide.pdf"
        assert result["sources"][1]["id"] == "doc2"
        assert result["sources"][1]["score"] == 0.87
        
        # Assert - Verify vectorstore was called correctly
        mock_vectorstore_client.query_similar.assert_called_once_with(query, top_k=top_k)
        
        # Assert - Verify OpenAI was called with context chunks
        mock_openai_client.generate_rag_response.assert_called_once()
        call_args = mock_openai_client.generate_rag_response.call_args
        
        # Check that query was passed
        assert call_args.kwargs["query"] == query
        
        # Check that context chunks were built correctly
        context_chunks = call_args.kwargs["context_chunks"]
        assert len(context_chunks) == 2
        assert "Document 1:" in context_chunks[0]
        assert "To reset your password, navigate to Settings > Security." in context_chunks[0]
        assert "Document 2:" in context_chunks[1]
        assert "Password reset requires email verification." in context_chunks[1]

    @pytest.mark.unit
    def test_answer_when_no_documents_found(
        self,
        rag_service,
        mock_vectorstore_client,
        mock_openai_client
    ):
        """
        Test answer() when vectorstore finds no relevant documents.
        
        Scenario: User asks a question, but vectorstore returns empty list
        (no documents match the query).
        
        Expected behavior:
        - Vectorstore is queried with the question
        - Context chunks will be empty list
        - OpenAI is still called with empty context
        - OpenAI should return "INSUFFICIENT_CONTEXT"
        - Returns answer and empty sources list
        """
        # Arrange
        query = "How do I configure the quantum flux capacitor?"
        top_k = 5
        
        # Mock vectorstore response (no documents found)
        mock_vectorstore_client.query_similar.return_value = []
        
        # Mock OpenAI response (insufficient context - now returns dict)
        mock_openai_client.generate_rag_response.return_value = {
            "answer": "INSUFFICIENT_CONTEXT",
            "tags": ["needs-escalation"],
            "confidence": "low"
        }
        
        # Act
        result = rag_service.answer(query=query, top_k=top_k)
        
        # Assert - Check return structure
        assert "answer" in result
        assert "tags" in result
        assert "confidence" in result
        assert "sources" in result
        
        # Assert - Check answer is INSUFFICIENT_CONTEXT
        assert result["answer"] == "INSUFFICIENT_CONTEXT"
        assert result["tags"] == ["needs-escalation"]
        assert result["confidence"] == "low"
        
        # Assert - Check sources is empty
        assert len(result["sources"]) == 0
        assert result["sources"] == []
        
        # Assert - Verify vectorstore was called correctly
        mock_vectorstore_client.query_similar.assert_called_once_with(query, top_k=top_k)
        
        # Assert - Verify OpenAI was called with empty context
        mock_openai_client.generate_rag_response.assert_called_once()
        call_args = mock_openai_client.generate_rag_response.call_args
        
        # Check that query was passed
        assert call_args.kwargs["query"] == query
        
        # Check that context chunks is empty
        context_chunks = call_args.kwargs["context_chunks"]
        assert len(context_chunks) == 0
        assert context_chunks == []

    @pytest.mark.unit
    def test_answer_with_conversation_history(
        self,
        rag_service,
        mock_vectorstore_client,
        mock_openai_client
    ):
        """
        Test answer() with conversation history provided.
        
        Scenario: User asks a follow-up question with conversation history.
        
        Expected behavior:
        - Vectorstore is queried with the question
        - Context chunks are built from retrieved documents
        - OpenAI is called with context AND conversation history
        - Returns answer with sources
        """
        # Arrange
        query = "What about the second step?"
        top_k = 5
        
        # Create conversation history
        from app.schemas.requests import ConversationMessage
        conversation_history = [
            ConversationMessage(role="user", content="How do I reset my password?"),
            ConversationMessage(role="assistant", content="Follow these steps: 1. Go to Settings...")
        ]
        
        # Mock vectorstore response
        mock_vectorstore_client.query_similar.return_value = [
            {
                "id": "doc1",
                "score": 0.92,
                "metadata": {
                    "source": "guide.pdf",
                    "text": "Step 2: Click on Reset Password button."
                }
            }
        ]
        
        # Mock OpenAI response
        mock_openai_client.generate_rag_response.return_value = {
            "answer": "Step 2 is to click on the Reset Password button.",
            "tags": ["password-reset", "follow-up"],
            "confidence": "high"
        }
        
        # Act
        result = rag_service.answer(query=query, conversation_history=conversation_history, top_k=top_k)
        
        # Assert - Check return structure
        assert result["answer"] == "Step 2 is to click on the Reset Password button."
        assert result["tags"] == ["password-reset", "follow-up"]
        assert result["confidence"] == "high"
        
        # Assert - Verify OpenAI was called with conversation history
        mock_openai_client.generate_rag_response.assert_called_once()
        call_args = mock_openai_client.generate_rag_response.call_args
        
        # Check that conversation history was passed
        assert call_args.kwargs["conversation_history"] is not None
        history_dicts = call_args.kwargs["conversation_history"]
        assert len(history_dicts) == 2
        assert history_dicts[0]["role"] == "user"
        assert history_dicts[0]["content"] == "How do I reset my password?"
        assert history_dicts[1]["role"] == "assistant"

    @pytest.mark.unit
    def test_answer_without_conversation_history(
        self,
        rag_service,
        mock_vectorstore_client,
        mock_openai_client
    ):
        """
        Test answer() without conversation history (backward compatibility).
        
        Scenario: User asks a question without providing conversation history.
        
        Expected behavior:
        - OpenAI is called with conversation_history=None
        - System still works as before
        """
        # Arrange
        query = "How do I login?"
        
        # Mock vectorstore response
        mock_vectorstore_client.query_similar.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {"source": "guide.pdf", "text": "Login at /login"}
            }
        ]
        
        # Mock OpenAI response
        mock_openai_client.generate_rag_response.return_value = {
            "answer": "Go to /login page",
            "tags": ["login"],
            "confidence": "high"
        }
        
        # Act - Call without conversation_history parameter
        result = rag_service.answer(query=query)
        
        # Assert
        assert result["answer"] == "Go to /login page"
        
        # Verify OpenAI was called with conversation_history=None (default)
        call_args = mock_openai_client.generate_rag_response.call_args
        # Check if conversation_history was passed or is None
        history = call_args.kwargs.get("conversation_history")
        assert history is None

    @pytest.mark.unit
    def test_answer_with_empty_conversation_history(
        self,
        rag_service,
        mock_vectorstore_client,
        mock_openai_client
    ):
        """
        Test answer() with empty conversation history list.
        
        Scenario: Conversation history is an empty list.
        
        Expected behavior:
        - System handles empty list gracefully
        - OpenAI is called with empty list (converted to None or empty)
        """
        # Arrange
        query = "First question"
        conversation_history = []
        
        # Mock responses
        mock_vectorstore_client.query_similar.return_value = [
            {"id": "doc1", "score": 0.9, "metadata": {"source": "doc", "text": "Answer text"}}
        ]
        mock_openai_client.generate_rag_response.return_value = {
            "answer": "Answer",
            "tags": ["tag"],
            "confidence": "high"
        }
        
        # Act
        result = rag_service.answer(query=query, conversation_history=conversation_history)
        
        # Assert - Should work normally
        assert result["answer"] == "Answer"
        
        # Verify OpenAI was called
        mock_openai_client.generate_rag_response.assert_called_once()
