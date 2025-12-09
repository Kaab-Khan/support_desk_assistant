"""
Integration tests for OpenAI API connection.

These tests verify real OpenAI API connectivity and functionality:
1. OpenAI connection works with real API key
2. Chat completions generate responses
3. Embeddings are generated correctly
4. RAG responses work with context
5. Summary generation works

Note: These tests hit the REAL OpenAI API and require:
- Valid OPENAI_API_KEY in .env
- These tests COST MONEY (minimal, but real API charges)
- Tests use gpt-4o-mini to minimize costs
"""
import pytest
from app.infrastructure.clients.openai_client import OpenAIClient, get_openai_client
from app.config.settings import get_settings


class TestOpenAIIntegration:
    """Integration tests for OpenAI API."""

    @pytest.fixture
    def openai_client(self):
        """Get the real OpenAI client (not mocked)."""
        return get_openai_client()

    @pytest.mark.integration
    def test_openai_client_initialization(self, openai_client):
        """
        Test that OpenAI client initializes successfully.
        
        Scenario: Application starts and connects to OpenAI.
        
        Expected behavior:
        - Client instance is created
        - API key is loaded from settings
        - No connection errors
        """
        # Assert - Client exists and has required attributes
        assert openai_client is not None
        assert hasattr(openai_client, '_client')
        assert hasattr(openai_client, '_api_key')
        assert hasattr(openai_client, '_model_name')
        
        # Verify settings are loaded
        settings = get_settings()
        assert settings.OPENAI_API_KEY is not None
        assert len(settings.OPENAI_API_KEY) > 0
        assert settings.OPENAI_API_KEY.startswith("sk-"), "OpenAI key should start with 'sk-'"
        
        # Verify default model
        assert openai_client._model_name == "gpt-4o-mini"
        
        print(f"\n✅ Successfully initialized OpenAI client")
        print(f"✅ Using model: {openai_client._model_name}")

    @pytest.mark.integration
    def test_generate_chat_completion_simple(self, openai_client):
        """
        Test basic chat completion with simple prompt.
        
        Scenario: Send a simple question to OpenAI and get a response.
        
        Expected behavior:
        - API call succeeds
        - Returns non-empty string response
        - Response is relevant to the question
        """
        # Arrange
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2 + 2?"}
        ]
        
        # Act
        response = openai_client.generate_chat_completion(messages=messages)
        
        # Assert - Response exists
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Assert - Response contains expected answer
        assert "4" in response, "Response should contain the answer '4'"
        
        print(f"\n✅ Chat completion successful")
        print(f"✅ Question: 'What is 2 + 2?'")
        print(f"✅ Response: {response[:100]}...")

    @pytest.mark.integration
    def test_generate_chat_completion_with_custom_parameters(self, openai_client):
        """
        Test chat completion with custom temperature and max_tokens.
        
        Scenario: Request a short, creative response with custom parameters.
        
        Expected behavior:
        - API respects temperature setting
        - API respects max_tokens limit
        - Returns valid response
        """
        # Arrange
        messages = [
            {"role": "user", "content": "Write a one-sentence fun fact about Python programming."}
        ]
        
        # Act
        response = openai_client.generate_chat_completion(
            messages=messages,
            temperature=0.9,  # High creativity
            max_tokens=50     # Short response
        )
        
        # Assert - Response exists and is reasonable length
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        assert len(response.split()) < 100, "Response should be relatively short due to max_tokens"
        
        # Assert - Response mentions Python
        assert "python" in response.lower(), "Response should be about Python"
        
        print(f"\n✅ Custom parameters chat completion successful")
        print(f"✅ Response length: {len(response)} chars")
        print(f"✅ Response: {response}")

    @pytest.mark.integration
    def test_generate_embeddings_single_text(self, openai_client):
        """
        Test generating embeddings for a single text.
        
        Scenario: Convert text to vector embedding for semantic search.
        
        Expected behavior:
        - API generates embedding
        - Embedding is a list of floats
        - Embedding has correct dimensions (1536 for text-embedding-ada-002)
        """
        # Arrange
        texts = ["How do I reset my password?"]
        
        # Act
        embeddings = openai_client.generate_embeddings(texts)
        
        # Assert - Embeddings structure
        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1, "Should return one embedding for one text"
        
        # Assert - Embedding format
        embedding = embeddings[0]
        assert isinstance(embedding, list), "Embedding should be a list of floats"
        assert len(embedding) == 1536, "OpenAI ada-002 embeddings are 1536 dimensions"
        assert all(isinstance(x, float) for x in embedding), "All values should be floats"
        
        print(f"\n✅ Generated embedding for 1 text")
        print(f"✅ Embedding dimensions: {len(embedding)}")
        print(f"✅ Sample values: {embedding[:5]}")

    @pytest.mark.integration
    def test_generate_embeddings_multiple_texts(self, openai_client):
        """
        Test generating embeddings for multiple texts in batch.
        
        Scenario: Convert multiple texts to embeddings efficiently.
        
        Expected behavior:
        - API generates embeddings for all texts
        - Returns list of embeddings matching input count
        - All embeddings have correct dimensions
        """
        # Arrange
        texts = [
            "How do I reset my password?",
            "What is the billing process?",
            "How to troubleshoot connection issues?"
        ]
        
        # Act
        embeddings = openai_client.generate_embeddings(texts)
        
        # Assert - Embeddings count
        assert len(embeddings) == len(texts), f"Should return {len(texts)} embeddings"
        
        # Assert - All embeddings are valid
        for i, embedding in enumerate(embeddings):
            assert isinstance(embedding, list), f"Embedding {i} should be a list"
            assert len(embedding) == 1536, f"Embedding {i} should have 1536 dimensions"
        
        # Assert - Embeddings are different (not identical)
        assert embeddings[0] != embeddings[1], "Different texts should have different embeddings"
        assert embeddings[1] != embeddings[2], "Different texts should have different embeddings"
        
        print(f"\n✅ Generated {len(embeddings)} embeddings")
        print(f"✅ All embeddings have 1536 dimensions")
        print(f"✅ Embeddings are unique for different texts")

    @pytest.mark.integration
    def test_generate_rag_response_with_context(self, openai_client):
        """
        Test RAG response generation with provided context.
        
        Scenario: Provide context documents and ask a question.
        OpenAI should answer based on the context.
        
        Expected behavior:
        - API generates answer using context
        - Answer references information from context
        - Answer is coherent and relevant
        """
        # Arrange
        query = "How do I reset my password?"
        context_chunks = [
            "To reset your password, go to the login page and click 'Forgot Password'.",
            "Enter your email address and wait for the reset link.",
            "The reset link expires in 30 minutes for security reasons."
        ]
        
        # Act
        response = openai_client.generate_rag_response(
            query=query,
            context_chunks=context_chunks
        )
        
        # Assert - Response exists
        assert response is not None
        assert isinstance(response, dict)
        assert "answer" in response
        assert "tags" in response
        assert "confidence" in response
        assert len(response) > 0
        
        # Assert - Response uses context (mentions key concepts)
        response_lower = response["answer"].lower()
        assert any(keyword in response_lower for keyword in ["password", "reset", "email", "forgot"]), \
            "Response should mention password reset concepts"
        
        # Assert - Should NOT say insufficient context
        assert "INSUFFICIENT_CONTEXT" not in response, \
            "Should not return INSUFFICIENT_CONTEXT when context is provided"
        
        print(f"\n✅ RAG response generated successfully")
        print(f"✅ Query: '{query}'")
        print(f"✅ Response: {response['answer'][:150]}...")

    @pytest.mark.integration
    def test_generate_rag_response_with_empty_context(self, openai_client):
        """
        Test RAG response when no context is provided.
        
        Scenario: Ask question without providing context documents.
        OpenAI should return INSUFFICIENT_CONTEXT marker.
        
        Expected behavior:
        - API returns INSUFFICIENT_CONTEXT marker
        - Indicates that context is missing
        - System can detect this and escalate
        """
        # Arrange
        query = "How do I configure the quantum flux capacitor?"
        context_chunks = []  # Empty context
        
        # Act
        response = openai_client.generate_rag_response(
            query=query,
            context_chunks=context_chunks
        )
        
        # Assert - Should return insufficient context marker
        assert response is not None
        assert isinstance(response, dict)
        assert "answer" in response
        assert "tags" in response
        assert "confidence" in response
        assert "INSUFFICIENT_CONTEXT" in response["answer"], \
            "Should return INSUFFICIENT_CONTEXT marker when no context provided"
        
        print(f"\n✅ RAG correctly identified insufficient context")
        print(f"✅ Query: '{query}'")
        print(f"✅ Response: {response}")

    @pytest.mark.integration
    def test_generate_summary_with_tags(self, openai_client):
        """
        Test generating summary and extracting tags from text.
        
        Scenario: Provide a support ticket text and extract summary + tags.
        
        Expected behavior:
        - API returns valid JSON
        - JSON contains 'summary' and 'tags' fields
        - Summary is concise
        - Tags are relevant
        """
        # Arrange
        text = """
        Customer reports that they cannot access their account after password reset.
        They have tried multiple times but keep getting an error message saying
        'Invalid credentials'. This is urgent as they need to process a payment today.
        Customer is on the Premium plan.
        """
        
        # Act
        response = openai_client.generate_summary_with_tags(
            text=text,
            max_sentences=2
        )
        
        # Assert - Response is valid JSON string
        assert response is not None
        assert isinstance(response, str)
        
        # Try to parse as JSON
        import json
        parsed = json.loads(response)
        
        # Assert - Has required fields
        assert "summary" in parsed, "Response should contain 'summary' field"
        assert "tags" in parsed, "Response should contain 'tags' field"
        
        # Assert - Summary is meaningful
        summary = parsed["summary"]
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert any(keyword in summary.lower() for keyword in ["account", "password", "error"]), \
            "Summary should mention key concepts"
        
        # Assert - Tags are relevant
        tags = parsed["tags"]
        assert isinstance(tags, list)
        assert len(tags) > 0
        assert all(isinstance(tag, str) for tag in tags), "All tags should be strings"
        
        print(f"\n✅ Summary and tags generated successfully")
        print(f"✅ Summary: {summary}")
        print(f"✅ Tags: {tags}")

    @pytest.mark.integration
    def test_openai_returns_json_for_database_storage(self, openai_client):
        """
        Test that OpenAI responses are JSON-serializable for database storage.
        
        Scenario: Generate various types of responses and verify they can be
        stored in database as JSON.
        
        Expected behavior:
        - Chat completion response is valid string (JSON-serializable)
        - Embeddings are valid list of floats (JSON-serializable)
        - Summary response is valid JSON string
        - All responses can be stored in database without errors
        """
        import json
        
        # Test 1: Chat completion should be JSON-serializable string
        messages = [
            {"role": "user", "content": "Explain password reset in one sentence."}
        ]
        chat_response = openai_client.generate_chat_completion(messages=messages)
        
        # Should be able to serialize to JSON
        chat_json = json.dumps({"response": chat_response})
        assert chat_json is not None
        
        # Should be able to deserialize back
        chat_data = json.loads(chat_json)
        assert chat_data["response"] == chat_response
        
        print(f"\n✅ Chat completion is JSON-serializable")
        print(f"✅ Response: {chat_response[:100]}...")
        
        # Test 2: Embeddings should be JSON-serializable list
        texts = ["Test text for embedding"]
        embeddings = openai_client.generate_embeddings(texts)
        
        # Should be able to serialize embeddings to JSON
        embedding_json = json.dumps({"embedding": embeddings[0]})
        assert embedding_json is not None
        
        # Should be able to deserialize back
        embedding_data = json.loads(embedding_json)
        assert embedding_data["embedding"] == embeddings[0]
        
        print(f"✅ Embeddings are JSON-serializable")
        print(f"✅ Embedding dimensions: {len(embeddings[0])}")
        
        # Test 3: Summary response should be valid JSON
        text = "Customer cannot login after password reset. Urgent issue."
        summary_response = openai_client.generate_summary_with_tags(text=text)
        
        # Should already be valid JSON string
        summary_data = json.loads(summary_response)
        assert "summary" in summary_data
        assert "tags" in summary_data
        
        # Should be able to re-serialize for database
        db_ready_json = json.dumps(summary_data)
        assert db_ready_json is not None
        
        print(f"✅ Summary response is valid JSON")
        print(f"✅ Summary: {summary_data['summary']}")
        print(f"✅ Tags: {summary_data['tags']}")
        
        # Test 4: Complete ticket data structure (what goes to DB)
        ticket_data = {
            "id": 123,
            "text": "Original ticket text",
            "action": "reply",
            "reply": chat_response,
            "tags": summary_data["tags"],
            "reason": "Generated via RAG",
            "summary": summary_data["summary"],
            "embedding": embeddings[0][:10]  # Store first 10 dims as sample
        }
        
        # Should be able to serialize entire ticket structure
        ticket_json = json.dumps(ticket_data)
        assert ticket_json is not None
        
        # Should be able to deserialize back
        ticket_restored = json.loads(ticket_json)
        assert ticket_restored["id"] == 123
        assert ticket_restored["reply"] == chat_response
        assert ticket_restored["tags"] == summary_data["tags"]
        
        print(f"✅ Complete ticket data structure is JSON-serializable")
        print(f"✅ Ready for database storage")
        print(f"✅ Ticket JSON size: {len(ticket_json)} bytes")

    @pytest.mark.integration
    def test_openai_error_handling(self, openai_client):
        """
        Test that OpenAI client handles errors gracefully.
        
        Scenario: Send invalid request (empty messages).
        
        Expected behavior:
        - Should raise appropriate exception
        - Error is caught and can be handled
        """
        # Arrange
        messages = []  # Invalid: empty messages list
        
        # Act & Assert - Should raise an exception
        with pytest.raises(Exception) as exc_info:
            openai_client.generate_chat_completion(messages=messages)
        
        # Verify we got some kind of error
        assert exc_info.value is not None
        
        print(f"\n✅ Error handling works correctly")
        print(f"✅ Exception type: {type(exc_info.value).__name__}")
