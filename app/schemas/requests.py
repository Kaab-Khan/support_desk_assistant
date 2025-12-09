"""
Request schemas (Pydantic models for API inputs).
"""
from pydantic import BaseModel, field_validator


class RagQueryRequest(BaseModel):
    """Request for RAG query."""
    query: str
    
    @field_validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty or whitespace')
        return v.strip()


class TicketAgentRequest(BaseModel):
    """Request for ticket processing."""
    ticket: str


class TicketFeedbackRequest(BaseModel):
    """Request for ticket feedback."""
    ticket_id: int
    human_label: str
