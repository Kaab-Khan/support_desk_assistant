"""
Unit tests for request schemas with conversation history support.
"""
import pytest
from pydantic import ValidationError
from app.schemas.requests import RagQueryRequest, ConversationMessage


class TestConversationMessage:
    """Test suite for ConversationMessage model."""

    @pytest.mark.unit
    def test_create_valid_conversation_message(self):
        """
        Test creating a valid ConversationMessage.
        
        Expected behavior:
        - Message is created with role and content
        - Fields are accessible as attributes
        """
        # Arrange & Act
        message = ConversationMessage(role="user", content="Hello!")
        
        # Assert
        assert message.role == "user"
        assert message.content == "Hello!"

    @pytest.mark.unit
    def test_create_assistant_message(self):
        """
        Test creating an assistant message.
        
        Expected behavior:
        - Message is created with assistant role
        """
        # Arrange & Act
        message = ConversationMessage(role="assistant", content="How can I help?")
        
        # Assert
        assert message.role == "assistant"
        assert message.content == "How can I help?"


class TestRagQueryRequestWithConversationHistory:
    """Test suite for RagQueryRequest with conversation history."""

    @pytest.mark.unit
    def test_create_request_without_conversation_history(self):
        """
        Test creating RagQueryRequest without conversation history.
        
        Expected behavior:
        - Request is created successfully
        - conversation_history defaults to None
        - Backward compatible with old API
        """
        # Arrange & Act
        request = RagQueryRequest(query="How do I reset my password?")
        
        # Assert
        assert request.query == "How do I reset my password?"
        assert request.conversation_history is None

    @pytest.mark.unit
    def test_create_request_with_empty_conversation_history(self):
        """
        Test creating RagQueryRequest with empty conversation history.
        
        Expected behavior:
        - Request accepts empty list
        - conversation_history is an empty list
        """
        # Arrange & Act
        request = RagQueryRequest(
            query="What's next?",
            conversation_history=[]
        )
        
        # Assert
        assert request.query == "What's next?"
        assert request.conversation_history == []

    @pytest.mark.unit
    def test_create_request_with_conversation_history(self):
        """
        Test creating RagQueryRequest with conversation history.
        
        Expected behavior:
        - Request accepts list of ConversationMessage objects
        - History is preserved and accessible
        """
        # Arrange
        history = [
            ConversationMessage(role="user", content="How do I reset my password?"),
            ConversationMessage(role="assistant", content="Go to Settings > Security."),
            ConversationMessage(role="user", content="What if I forgot my email?")
        ]
        
        # Act
        request = RagQueryRequest(
            query="Can you clarify?",
            conversation_history=history
        )
        
        # Assert
        assert request.query == "Can you clarify?"
        assert len(request.conversation_history) == 3
        assert request.conversation_history[0].role == "user"
        assert request.conversation_history[0].content == "How do I reset my password?"
        assert request.conversation_history[1].role == "assistant"
        assert request.conversation_history[2].role == "user"

    @pytest.mark.unit
    def test_create_request_with_dict_conversation_history(self):
        """
        Test creating RagQueryRequest with dict-based conversation history.
        
        Expected behavior:
        - Pydantic auto-converts dicts to ConversationMessage objects
        - Request is valid and history is accessible
        """
        # Arrange & Act
        request = RagQueryRequest(
            query="Follow-up question",
            conversation_history=[
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"}
            ]
        )
        
        # Assert
        assert len(request.conversation_history) == 2
        assert isinstance(request.conversation_history[0], ConversationMessage)
        assert request.conversation_history[0].role == "user"
        assert request.conversation_history[0].content == "First question"

    @pytest.mark.unit
    def test_query_validation_strips_whitespace(self):
        """
        Test that query validation strips whitespace.
        
        Expected behavior:
        - Leading/trailing whitespace is removed
        - Validation still works with conversation history
        """
        # Arrange & Act
        request = RagQueryRequest(
            query="  How do I login?  ",
            conversation_history=[
                {"role": "user", "content": "Previous question"}
            ]
        )
        
        # Assert
        assert request.query == "How do I login?"  # Whitespace stripped

    @pytest.mark.unit
    def test_empty_query_raises_validation_error(self):
        """
        Test that empty query raises validation error even with history.
        
        Expected behavior:
        - Empty query should fail validation
        - Conversation history doesn't bypass query validation
        """
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RagQueryRequest(
                query="   ",
                conversation_history=[
                    {"role": "user", "content": "Previous question"}
                ]
            )
        
        assert "Query cannot be empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_long_conversation_history_accepted(self):
        """
        Test that long conversation history is accepted.
        
        Expected behavior:
        - System accepts large conversation histories
        - No artificial limits on history length (client manages truncation)
        """
        # Arrange
        long_history = []
        for i in range(20):
            long_history.append({"role": "user", "content": f"Question {i}"})
            long_history.append({"role": "assistant", "content": f"Answer {i}"})
        
        # Act
        request = RagQueryRequest(
            query="Latest question",
            conversation_history=long_history
        )
        
        # Assert
        assert len(request.conversation_history) == 40
        assert request.query == "Latest question"
