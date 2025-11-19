"""
Pydantic schemas for API request and response models.

Defines the data structures used for input validation and output serialization
across all API endpoints.
"""

from datetime import datetime

from pydantic import BaseModel


# ============================================================================
# Request Models
# ============================================================================

class RagQueryRequest(BaseModel):
    """
    Request model for RAG query endpoint.
    
    Attributes:
        query: The user's question to be answered using RAG
    """
    
    query: str


class SummariseRequest(BaseModel):
    """
    Request model for text summarization endpoint.
    
    Attributes:
        text: The text content to be summarized
    """
    
    text: str


class TicketAgentRequest(BaseModel):
    """
    Request model for ticket triage agent endpoint.
    
    Attributes:
        ticket: The support ticket text to be processed
    """
    
    ticket: str


class TicketFeedbackRequest(BaseModel):
    """
    Request model for submitting human feedback on ticket classification.
    
    Attributes:
        ticket_id: The ID of the ticket being labeled
        human_label: The human-provided label/classification
    """
    
    ticket_id: int
    human_label: str


# ============================================================================
# Response Models
# ============================================================================

class RagSource(BaseModel):
    """
    A single source document used in RAG response.
    
    Attributes:
        doc_name: Name of the source document
        snippet: Relevant text excerpt from the document
    """
    
    doc_name: str
    snippet: str


class RagQueryResponse(BaseModel):
    """
    Response model for RAG query endpoint.
    
    Attributes:
        answer: The generated answer to the query
        sources: List of source documents used to generate the answer
    """
    
    answer: str
    sources: list[RagSource]


class SummariseResponse(BaseModel):
    """
    Response model for text summarization endpoint.
    
    Attributes:
        summary: The generated summary of the input text
        tags: List of extracted tags/keywords from the text
    """
    
    summary: str
    tags: list[str]


class TicketAgentResponse(BaseModel):
    """
    Response model for ticket triage agent endpoint.
    
    Attributes:
        id: The ticket ID assigned by the system
        action: The recommended action (e.g., 'reply', 'escalate', 'close')
        reply: The suggested reply text, if applicable
        reason: Explanation for the recommended action
        tags: List of tags categorizing the ticket
    """
    
    id: int
    action: str
    reply: str | None
    reason: str
    tags: list[str]


class TicketRecord(BaseModel):
    """
    Complete ticket record from the database.
    
    Attributes:
        id: Unique ticket identifier
        text: The original ticket text
        action: The action taken or recommended
        reply: The reply text, if any
        tags: List of tags assigned to the ticket
        reason: Explanation for the action taken
        created_at: Timestamp when the ticket was created
        human_label: Human-provided label/feedback, if any
    """
    
    id: int
    text: str
    action: str
    reply: str | None
    tags: list[str] | None
    reason: str | None
    created_at: datetime
    human_label: str | None
