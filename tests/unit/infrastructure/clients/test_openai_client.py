"""
Unit tests for OpenAIClient.generate_chat_completion() function.
"""
import pytest
from unittest.mock import Mock, patch
from app.infrastructure.clients.openai_client import OpenAIClient


class TestGenerateChatCompletion:
    """Test suite for OpenAIClient.generate_chat_completion() method."""

    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI API response."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "This is the generated response from OpenAI."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response

    @pytest.mark.unit
    @patch('app.infrastructure.clients.openai_client.OpenAI')
    def test_generate_chat_completion_with_default_parameters(
        self,
        mock_openai_class,
        mock_openai_response
    ):
        """
        Test generate_chat_completion() with default parameters.
        
        Scenario: Call chat completion with messages only,
        using default model and temperature.
        
        Expected behavior:
        - OpenAI API is called with correct messages
        - Uses default model (gpt-4o-mini)
        - Uses default temperature (0.7)
        - Returns the generated text content
        """
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client_instance
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"}
        ]
        
        # Act
        with patch('app.infrastructure.clients.openai_client.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-api-key"
            client = OpenAIClient()
            result = client.generate_chat_completion(messages=messages)
        
        # Assert - Check OpenAI API was called correctly
        mock_client_instance.chat.completions.create.assert_called_once()
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        
        assert call_kwargs["model"] == "gpt-4o-mini"  # Default model
        assert call_kwargs["messages"] == messages
        assert call_kwargs["temperature"] == 0.7  # Default temperature
        assert call_kwargs["max_tokens"] is None  # Default no limit
        
        # Assert - Check the returned content
        assert result == "This is the generated response from OpenAI."

    @pytest.mark.unit
    @patch('app.infrastructure.clients.openai_client.OpenAI')
    def test_generate_chat_completion_with_custom_parameters(
        self,
        mock_openai_class,
        mock_openai_response
    ):
        """
        Test generate_chat_completion() with custom parameters.
        
        Scenario: Call chat completion with custom model, temperature,
        and max_tokens.
        
        Expected behavior:
        - OpenAI API is called with custom parameters
        - Overrides default model and temperature
        - Respects max_tokens limit
        - Returns the generated text content
        """
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client_instance
        
        messages = [
            {"role": "user", "content": "Summarize this text briefly."}
        ]
        custom_model = "gpt-4"
        custom_temperature = 0.2
        custom_max_tokens = 100
        
        # Act
        with patch('app.infrastructure.clients.openai_client.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-api-key"
            client = OpenAIClient()
            result = client.generate_chat_completion(
                messages=messages,
                model=custom_model,
                temperature=custom_temperature,
                max_tokens=custom_max_tokens
            )
        
        # Assert - Check OpenAI API was called with custom parameters
        mock_client_instance.chat.completions.create.assert_called_once()
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        
        assert call_kwargs["model"] == "gpt-4"
        assert call_kwargs["messages"] == messages
        assert call_kwargs["temperature"] == 0.2
        assert call_kwargs["max_tokens"] == 100
        
        # Assert - Check the returned content
        assert result == "This is the generated response from OpenAI."


class TestGenerateRagResponseWithConversationHistory:
    """Test suite for OpenAIClient.generate_rag_response() with conversation history."""

    @pytest.fixture
    def mock_openai_response_json(self):
        """Create a mock OpenAI API response with JSON."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = '{"answer": "Password reset requires email verification.", "tags": ["password-reset", "authentication"], "confidence": "high"}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response

    @pytest.mark.unit
    @patch('app.infrastructure.clients.openai_client.OpenAI')
    def test_generate_rag_response_without_conversation_history(
        self,
        mock_openai_class,
        mock_openai_response_json
    ):
        """
        Test generate_rag_response() without conversation history.
        
        Scenario: Generate RAG response with context but no conversation history.
        
        Expected behavior:
        - OpenAI is called with system prompt and user prompt
        - No conversation context is included in prompt
        - Returns parsed JSON with answer, tags, confidence
        """
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response_json
        mock_openai_class.return_value = mock_client_instance
        
        query = "How do I reset my password?"
        context_chunks = [
            "Document 1:\nPassword reset is available in Settings.",
            "Document 2:\nVerify your email for password reset."
        ]
        
        # Act
        with patch('app.infrastructure.clients.openai_client.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-api-key"
            client = OpenAIClient()
            result = client.generate_rag_response(
                query=query,
                context_chunks=context_chunks,
                conversation_history=None
            )
        
        # Assert - Check result structure
        assert result["answer"] == "Password reset requires email verification."
        assert result["tags"] == ["password-reset", "authentication"]
        assert result["confidence"] == "high"
        
        # Assert - Check OpenAI was called
        mock_client_instance.chat.completions.create.assert_called_once()
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        
        # Verify prompt doesn't contain conversation context
        user_message = call_kwargs["messages"][1]["content"]
        assert "Previous conversation context:" not in user_message

    @pytest.mark.unit
    @patch('app.infrastructure.clients.openai_client.OpenAI')
    def test_generate_rag_response_with_conversation_history(
        self,
        mock_openai_class,
        mock_openai_response_json
    ):
        """
        Test generate_rag_response() with conversation history.
        
        Scenario: Generate RAG response with context and conversation history.
        
        Expected behavior:
        - OpenAI is called with system prompt and user prompt
        - Conversation summary is included in prompt
        - Returns parsed JSON with answer, tags, confidence
        - History is summarized (last 6 messages)
        """
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response_json
        mock_openai_class.return_value = mock_client_instance
        
        query = "What about the second step?"
        context_chunks = [
            "Document 1:\nPassword reset steps: 1. Go to Settings 2. Click Reset Password 3. Check email"
        ]
        conversation_history = [
            {"role": "user", "content": "How do I reset my password?"},
            {"role": "assistant", "content": "Follow these steps: 1. Go to Settings..."}
        ]
        
        # Act
        with patch('app.infrastructure.clients.openai_client.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-api-key"
            client = OpenAIClient()
            result = client.generate_rag_response(
                query=query,
                context_chunks=context_chunks,
                conversation_history=conversation_history
            )
        
        # Assert - Check result structure
        assert result["answer"] == "Password reset requires email verification."
        assert result["tags"] == ["password-reset", "authentication"]
        
        # Assert - Check OpenAI was called
        mock_client_instance.chat.completions.create.assert_called_once()
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        
        # Verify prompt contains conversation context
        user_message = call_kwargs["messages"][1]["content"]
        assert "Previous conversation context:" in user_message
        assert "User: How do I reset my password?" in user_message
        assert "Assistant: Follow these steps:" in user_message

    @pytest.mark.unit
    @patch('app.infrastructure.clients.openai_client.OpenAI')
    def test_generate_rag_response_truncates_long_history(
        self,
        mock_openai_class,
        mock_openai_response_json
    ):
        """
        Test that long conversation history is truncated.
        
        Scenario: User has a long conversation history (>6 messages).
        
        Expected behavior:
        - Only last 6 messages are included in summary
        - Older messages are dropped to control token usage
        """
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response_json
        mock_openai_class.return_value = mock_client_instance
        
        query = "Latest question"
        context_chunks = ["Document 1:\nSome context"]
        
        # Create 10 messages (should only use last 6)
        conversation_history = []
        for i in range(10):
            conversation_history.append({"role": "user", "content": f"Question {i}"})
        
        # Act
        with patch('app.infrastructure.clients.openai_client.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-api-key"
            client = OpenAIClient()
            result = client.generate_rag_response(
                query=query,
                context_chunks=context_chunks,
                conversation_history=conversation_history
            )
        
        # Assert - Check OpenAI was called
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        user_message = call_kwargs["messages"][1]["content"]
        
        # Verify only recent messages are in prompt
        assert "Question 9" in user_message  # Most recent
        assert "Question 8" in user_message
        assert "Question 7" in user_message
        assert "Question 6" in user_message
        assert "Question 5" in user_message
        assert "Question 4" in user_message
        assert "Question 3" not in user_message  # Older messages excluded
        assert "Question 0" not in user_message

    @pytest.mark.unit
    @patch('app.infrastructure.clients.openai_client.OpenAI')
    def test_generate_rag_response_truncates_long_messages(
        self,
        mock_openai_class,
        mock_openai_response_json
    ):
        """
        Test that long messages in history are truncated.
        
        Scenario: Conversation history contains very long messages.
        
        Expected behavior:
        - Each message is truncated to 150 characters
        - Prevents excessive token usage
        """
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response_json
        mock_openai_class.return_value = mock_client_instance
        
        query = "Follow-up"
        context_chunks = ["Document 1:\nContext"]
        
        long_message = "A" * 300  # 300 character message
        conversation_history = [
            {"role": "user", "content": long_message}
        ]
        
        # Act
        with patch('app.infrastructure.clients.openai_client.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-api-key"
            client = OpenAIClient()
            result = client.generate_rag_response(
                query=query,
                context_chunks=context_chunks,
                conversation_history=conversation_history
            )
        
        # Assert
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        user_message = call_kwargs["messages"][1]["content"]
        
        # Verify message was truncated (150 chars + "...")
        assert user_message.count("A") <= 153  # 150 + "..." = 153
