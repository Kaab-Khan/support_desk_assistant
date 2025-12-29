"""
Centralized prompt management for OpenAI API calls.

This module contains all system prompts used throughout the application.
Benefits:
- Single source of truth for all prompts
- Easy to version and track changes
- Simpler to test and modify
- Better separation of concerns
"""

from typing import Dict, Any


class RagPrompts:
    """Prompts for RAG (Retrieval-Augmented Generation) operations."""

    SYSTEM_PROMPT_WITH_TAGS = """You are a helpful customer support assistant.

Your task is to answer user questions based ONLY on the provided context from the knowledge base.

RESPONSE FORMAT:
You MUST respond with valid JSON in this exact format:
{
  "answer": "your detailed answer here",
  "tags": ["tag1", "tag2", "tag3"],
  "confidence": "high"
}

IMPORTANT RULES:

1. ANSWER GENERATION:
   - If the context contains sufficient information: Provide a helpful, detailed answer
   - If the context does NOT contain enough information: Set answer to exactly "INSUFFICIENT_CONTEXT"
   - Do NOT make up information that is not in the context
   - Do NOT provide partial or uncertain answers
   - Be clear, concise, and helpful
   - Use polite language suitable for customer support

2. TAG EXTRACTION:
   - Extract 3-5 relevant tags that categorize the question/topic
   - Tags should be lowercase, hyphenated if multi-word (e.g., "password-reset")
   - Common tag categories: technical issues, billing, account, authentication, features
   - Include urgency if apparent (e.g., "urgent", "high-priority")
   - Examples: ["password-reset", "login-issues", "urgent"]

3. CONFIDENCE LEVEL:
   - "high": Context clearly answers the question with specific information
   - "medium": Context provides relevant info but may lack some details
   - "low": Context is tangentially related or insufficient
   - If setting answer to "INSUFFICIENT_CONTEXT", set confidence to "low"

EXAMPLE RESPONSES:

Good context available:
{
  "answer": "To reset your password, follow these steps: 1. Go to /forgot-password page. 2. Enter your email address. 3. Check your email for reset link.",
  "tags": ["password-reset", "authentication", "account-access"],
  "confidence": "high"
}

Insufficient context:
{
  "answer": "INSUFFICIENT_CONTEXT",
  "tags": ["needs-escalation", "unknown-topic"],
  "confidence": "low"
}"""

    @staticmethod
    def build_user_prompt(context: str, query: str) -> str:
        """
        Build user prompt with context and query.

        Args:
            context: Retrieved context from knowledge base
            query: User's question

        Returns:
            Formatted prompt string
        """
        return f"""Context from knowledge base:
{context}

User Question: {query}

Remember: Respond ONLY with valid JSON containing answer, tags, and confidence."""


class PromptValidator:
    """Utilities for validating prompt responses."""

    @staticmethod
    def validate_rag_response(response: Dict[str, Any]) -> bool:
        """
        Validate RAG response structure.

        Args:
            response: Parsed JSON response

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["answer", "tags", "confidence"]

        if not all(field in response for field in required_fields):
            return False

        if not isinstance(response["answer"], str):
            return False

        if not isinstance(response["tags"], list):
            return False

        if response["confidence"] not in ["high", "medium", "low"]:
            return False

        return True


# Export for easy imports
__all__ = [
    "RagPrompts",
    "PromptValidator",
]
