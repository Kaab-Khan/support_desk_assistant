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
