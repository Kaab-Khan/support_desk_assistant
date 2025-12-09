"""
OpenAI API client.

Centralized client for all OpenAI API interactions.
"""
import json
from typing import List, Dict, Any
from openai import OpenAI

from app.config.settings import get_settings
from app.schemas.prompts import RagPrompts, PromptValidator


class OpenAIClient:
    """
    Client for OpenAI API.
    
    Handles all interactions with OpenAI's API including:
    - Chat completions
    - Embeddings generation
    """
    
    def __init__(self, api_key: str | None = None, model_name: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, loads from settings.
            model_name: Default model to use for chat completions.
        """
        settings = get_settings()
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._client = OpenAI(api_key=self._api_key)
        self._model_name = model_name
    
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> str:
        """
        Generate a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Model to use. If None, uses default model.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.
        
        Returns:
            Generated text response.
        """
        response = self._client.chat.completions.create(
            model=model or self._model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed.
            model: Embedding model to use.
        
        Returns:
            List of embedding vectors (each is a list of floats).
        """
        response = self._client.embeddings.create(
            model=model,
            input=texts
        )
        
        return [item.embedding for item in response.data]
    
    def generate_rag_response(
        self,
        query: str,
        context_chunks: List[str],
        model: str | None = None
    ) -> Dict[str, Any]:
        """
        Generate a RAG (Retrieval-Augmented Generation) response with tags.
        
        Args:
            query: User's query.
            context_chunks: Retrieved context chunks from knowledge base.
            model: Model to use. If None, uses default model.
        
        Returns:
            Dictionary containing:
                - "answer": str - Generated answer
                - "tags": List[str] - Extracted tags
                - "confidence": str - Confidence level (high/medium/low)
        """
        # Build context string
        context = "\n\n".join(context_chunks)
        
        # Use centralized prompt from schema
        messages = [
            {
                "role": "system",
                "content": RagPrompts.SYSTEM_PROMPT_WITH_TAGS
            },
            {
                "role": "user",
                "content": RagPrompts.build_user_prompt(context, query)
            }
        ]
        
        response_text = self.generate_chat_completion(messages, model=model)
        
        # Parse JSON response
        try:
            result = json.loads(response_text)
            
            # Validate response structure
            if PromptValidator.validate_rag_response(result):
                return result
            else:
                # Invalid structure - return safe default
                return {
                    "answer": response_text,
                    "tags": [],
                    "confidence": "low"
                }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "answer": response_text,
                "tags": [],
                "confidence": "low"
            }
    
    def generate_summary_with_tags(
        self,
        text: str,
        max_sentences: int = 2,
        model: str | None = None
    ) -> str:
        """
        Generate a summary and extract tags from text.
        
        Args:
            text: Text to summarize.
            max_sentences: Maximum number of sentences in summary.
            model: Model to use. If None, uses default model.
        
        Returns:
            JSON string with 'summary' and 'tags' fields.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that summarizes text and extracts relevant tags. "
                    "Always respond with valid JSON containing 'summary' and 'tags' fields."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Summarize the following text in {max_sentences} sentence(s) or less, "
                    f"and extract 3-5 relevant tags/keywords.\n\n"
                    f"Text: {text}\n\n"
                    f"Respond in JSON format: {{\"summary\": \"...\", \"tags\": [\"tag1\", \"tag2\", ...]}}"
                )
            }
        ]
        
        return self.generate_chat_completion(messages, model=model, temperature=0.3)


# Singleton instance
_openai_client: OpenAIClient | None = None


def get_openai_client() -> OpenAIClient:
    """
    Get singleton OpenAI client instance.
    
    Returns:
        OpenAIClient: Singleton instance.
    """
    global _openai_client
    
    if _openai_client is None:
        _openai_client = OpenAIClient()
    
    return _openai_client
