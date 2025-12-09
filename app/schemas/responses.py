"""
Response schemas (Pydantic models for API outputs).
"""
from datetime import datetime
from pydantic import BaseModel


class RagSource(BaseModel):
    """Source document in RAG response."""
    doc_name: str
    snippet: str


class RagQueryResponse(BaseModel):
    """Response for RAG query."""
    answer: str
    sources: list[RagSource]


class TicketAgentResponse(BaseModel):
    """Response for ticket processing."""
    id: int
    action: str
    reply: str | None
    reason: str
    tags: list[str]


class TicketRecord(BaseModel):
    """Complete ticket record."""
    id: int
    text: str
    action: str
    reply: str | None
    tags: list[str] | None
    reason: str | None
    created_at: datetime
    human_label: str | None
