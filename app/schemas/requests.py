"""
Request schemas (Pydantic models for API inputs).
"""
from typing import List, Optional
from pydantic import BaseModel, field_validator


class ConversationMessage(BaseModel):
    """Single message in a conversation."""
    
    role: str  # "user" or "assistant"
    content: str


class RagQueryRequest(BaseModel):
    """Request for RAG query."""

    query: str
    session_id: str  # Session identifier for rate limiting
    conversation_history: Optional[List[ConversationMessage]] = None

    @field_validator("query")
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty or whitespace")
        return v.strip()
    
    @field_validator("session_id")
    def session_id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty or whitespace")
        return v.strip()

class TicketAgentRequest(BaseModel):
    """Request for ticket processing."""

    ticket: str


class TicketFeedbackRequest(BaseModel):
    """Request for ticket feedback."""

    ticket_id: int
    human_label: str
