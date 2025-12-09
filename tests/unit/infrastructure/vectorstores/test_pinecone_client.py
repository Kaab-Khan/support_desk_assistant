"""
Unit tests for VectorStoreClient.query_similar() function.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.infrastructure.vectorstores.pinecone_client import VectorStoreClient


class TestQuerySimilar:
    """Test suite for VectorStoreClient.query_similar() method."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        mock = Mock()
        # Mock embeddings generation
        mock.generate_embeddings.return_value = [[0.1, 0.2, 0.3] * 512]  # 1536 dimensions
        return mock

    @pytest.mark.unit
    @patch('app.infrastructure.vectorstores.pinecone_client.Pinecone')
    @patch('app.infrastructure.vectorstores.pinecone_client.get_settings')
    def test_query_similar_with_results_found(
        self,
        mock_get_settings,
        mock_pinecone_class,
        mock_openai_client
    ):
        """
        Test query_similar() when relevant documents are found.
        
        Scenario: User queries for similar documents and Pinecone
        returns relevant matches.
        
        Expected behavior:
        - Query text is embedded using OpenAI
        - Pinecone is queried with the embedding
        - Returns list of matches with scores and metadata
        - Matches are formatted correctly
        """
        # Arrange
        query = "How do I reset my password?"
        top_k = 5
        
        # Mock settings
        mock_settings = Mock()
        mock_settings.PINECONE_API_KEY = "test-pinecone-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_get_settings.return_value = mock_settings
        
        # Mock Pinecone index
        mock_index = Mock()
        mock_pinecone_instance = Mock()
        
        # Mock list_indexes() to return existing index (Pinecone 5.x API)
        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pinecone_instance.list_indexes.return_value = [mock_index_obj]
        
        mock_pinecone_instance.Index.return_value = mock_index
        mock_pinecone_class.return_value = mock_pinecone_instance
        
        # Mock Pinecone query response
        mock_match1 = Mock()
        mock_match1.id = "doc1"
        mock_match1.score = 0.95
        mock_match1.metadata = {
            "source": "user_guide.pdf",
            "text": "To reset your password, go to Settings."
        }
        
        mock_match2 = Mock()
        mock_match2.id = "doc2"
        mock_match2.score = 0.87
        mock_match2.metadata = {
            "source": "faq.pdf",
            "text": "Password reset requires email verification."
        }
        
        mock_query_response = Mock()
        mock_query_response.matches = [mock_match1, mock_match2]
        mock_index.query.return_value = mock_query_response
        
        # Act
        client = VectorStoreClient(openai_client=mock_openai_client)
        result = client.query_similar(query=query, top_k=top_k)
        
        # Assert - Check OpenAI embeddings was called
        mock_openai_client.generate_embeddings.assert_called_once_with([query])
        
        # Assert - Check Pinecone query was called correctly
        mock_index.query.assert_called_once()
        call_kwargs = mock_index.query.call_args.kwargs
        assert call_kwargs["top_k"] == top_k
        assert call_kwargs["include_metadata"] is True
        assert "vector" in call_kwargs
        
        # Assert - Check the returned results
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Check first match
        assert result[0]["id"] == "doc1"
        assert result[0]["score"] == 0.95
        assert result[0]["metadata"]["source"] == "user_guide.pdf"
        assert result[0]["metadata"]["text"] == "To reset your password, go to Settings."
        
        # Check second match
        assert result[1]["id"] == "doc2"
        assert result[1]["score"] == 0.87
        assert result[1]["metadata"]["source"] == "faq.pdf"

    @pytest.mark.unit
    @patch('app.infrastructure.vectorstores.pinecone_client.Pinecone')
    @patch('app.infrastructure.vectorstores.pinecone_client.get_settings')
    def test_query_similar_with_no_results(
        self,
        mock_get_settings,
        mock_pinecone_class,
        mock_openai_client
    ):
        """
        Test query_similar() when no documents match the query.
        
        Scenario: User queries for documents but Pinecone returns
        no matches (empty list).
        
        Expected behavior:
        - Query text is embedded using OpenAI
        - Pinecone is queried with the embedding
        - Returns empty list
        - Does not crash or raise exceptions
        """
        # Arrange
        query = "How do I configure quantum flux capacitor?"
        top_k = 5
        
        # Mock settings
        mock_settings = Mock()
        mock_settings.PINECONE_API_KEY = "test-pinecone-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_get_settings.return_value = mock_settings
        
        # Mock Pinecone index
        mock_index = Mock()
        mock_pinecone_instance = Mock()
        
        # Mock list_indexes() to return existing index (Pinecone 5.x API)
        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pinecone_instance.list_indexes.return_value = [mock_index_obj]
        
        mock_pinecone_instance.Index.return_value = mock_index
        mock_pinecone_class.return_value = mock_pinecone_instance
        
        # Mock Pinecone query response (no matches)
        mock_query_response = Mock()
        mock_query_response.matches = []
        mock_index.query.return_value = mock_query_response
        
        # Act
        client = VectorStoreClient(openai_client=mock_openai_client)
        result = client.query_similar(query=query, top_k=top_k)
        
        # Assert - Check OpenAI embeddings was called
        mock_openai_client.generate_embeddings.assert_called_once_with([query])
        
        # Assert - Check Pinecone query was called
        mock_index.query.assert_called_once()
        
        # Assert - Check the returned results
        assert isinstance(result, list)
        assert len(result) == 0
        assert result == []
