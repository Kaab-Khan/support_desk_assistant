"""
Summarisation service.

Provides text summarisation and tag extraction using OpenAI LLM.
"""

import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from app.config import get_settings


# Module-level cache for SummariserService singleton
_summariser_service: Optional["SummariserService"] = None


class SummariserService:
    """
    Service for text summarisation and tag extraction.
    
    Uses OpenAI LLM to generate concise summaries and extract relevant tags/keywords.
    """
    
    def __init__(self, model_name: Optional[str] = None) -> None:
        """
        Initialize the summarisation service.
        
        Args:
            model_name: OpenAI model name to use for summarisation (e.g., 'gpt-4', 'gpt-3.5-turbo')
            
        - Store the model name for OpenAI calls
        - Initialize OpenAI client using settings
        """
        settings = get_settings()
        self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model_name = model_name or "gpt-4o-mini"
    
    def summarise(
        self,
        text: str,
        max_sentences: int = 3
    ) -> Dict[str, Any]:
        """
        Summarise text and extract tags/keywords.
        
        Args:
            text: The text content to summarise
            max_sentences: Maximum number of sentences in the summary
            
        Returns:
            Dictionary containing:
                - "summary": str - The generated summary
                - "tags": List[str] - Extracted tags/keywords
                
        - Call OpenAI to generate a concise summary
        - Extract relevant tags/keywords from the text
        - Format and return response with summary and tags
        """
        system_message = (
            "You are a text summarisation assistant. "
            "You MUST respond with ONLY valid JSON in this exact format:\n"
            "{\"summary\": \"...\", \"tags\": [\"...\", \"...\"]}"
            "The summary should be concise and capture the main points. "
            "Tags should be 3-7 short keywords or phrases that categorize the content."
        )
        
        user_message = (
            f"Summarise the following text in approximately {max_sentences} sentences "
            f"and extract 3-7 relevant tags.\n\n"
            f"Text:\n{text}\n\n"
            f"Respond with ONLY the JSON object, no other text."
        )
        
        response = self._openai_client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        content = response.choices[0].message.content
        
        # Attempt to parse JSON response
        try:
            result = json.loads(content)
            return {
                "summary": result.get("summary", ""),
                "tags": result.get("tags", [])
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "summary": content,
                "tags": []
            }


def get_summariser_service() -> SummariserService:
    """
    Return a singleton instance of SummariserService.
    
    Initializes the service on first call and caches it for subsequent calls.
    
    Returns:
        SummariserService: The singleton summarisation service instance
    """
    global _summariser_service
    
    if _summariser_service is None:
        _summariser_service = SummariserService()
    
    return _summariser_service
