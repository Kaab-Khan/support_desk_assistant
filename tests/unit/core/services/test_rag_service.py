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

