"""
FastAPI entrypoint for the AI Support Desk Assistant.

Exposes REST API endpoints for RAG query, summarisation, ticket processing,
feedback submission, and ticket listing.
"""

from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    RagQueryRequest,
    RagQueryResponse,
    RagSource,
    SummariseRequest,
    SummariseResponse,
    TicketAgentRequest,
    TicketAgentResponse,
    TicketFeedbackRequest,
    TicketRecord,
)
from app.rag_service import RagService, get_rag_service
from app.summariser import SummariserService, get_summariser_service
from app.agent_service import TicketAgentService, get_ticket_agent_service
from app import crud


app = FastAPI(
    title="AI Support Desk Assistant",
    description="API for RAG-based support, summarisation, and ticket triage.",
    version="0.1.0",
)


@app.post("/rag/query", response_model=RagQueryResponse)
def rag_query(
    request: RagQueryRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> RagQueryResponse:
    """
    Run a retrieval-augmented generation (RAG) query.

    Uses the RAG service to retrieve relevant knowledge base context
    and generate an answer to the user's query.
    """
    result = rag_service.answer(request.query)
    
    sources = []
    for match in result.get("sources", []):
        metadata = match.get("metadata", {})
        doc_name = metadata.get("source", match.get("id", "unknown"))
        snippet = metadata.get("text", "")
        sources.append(RagSource(doc_name=doc_name, snippet=snippet))
    
    return RagQueryResponse(
        answer=result.get("answer", ""),
        sources=sources
    )


@app.post("/summarise", response_model=SummariseResponse)
def summarise_text(
    request: SummariseRequest,
    summariser: SummariserService = Depends(get_summariser_service),
) -> SummariseResponse:
    """
    Summarise a piece of text and extract tags/keywords.

    Uses the summarisation service to generate a concise summary and
    a small set of descriptive tags.
    """
    result = summariser.summarise(request.text)
    
    summary = result.get("summary", "")
    tags = result.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    
    return SummariseResponse(summary=summary, tags=tags)


@app.post("/tickets/agent", response_model=TicketAgentResponse)
def process_ticket(
    request: TicketAgentRequest,
    db: Session = Depends(get_db),
    agent: TicketAgentService = Depends(get_ticket_agent_service),
) -> TicketAgentResponse:
    """
    Process a new support ticket using the ticket agent.

    Uses the ticket agent service to analyse the ticket, decide an action,
    optionally generate a reply, assign tags, and persist the ticket.
    """
    result = agent.process_ticket(db=db, text=request.ticket)
    
    return TicketAgentResponse(
        id=result["id"],
        action=result["action"],
        reply=result.get("reply"),
        reason=result.get("reason", ""),
        tags=result.get("tags", []),
    )


@app.post("/tickets/feedback", response_model=TicketRecord)
def submit_ticket_feedback(
    request: TicketFeedbackRequest,
    db: Session = Depends(get_db),
) -> TicketRecord:
    """
    Submit human feedback for an existing ticket.

    Updates the ticket record with human-provided labels or corrections.
    """
    ticket = crud.update_ticket_feedback(
        db=db,
        ticket_id=request.ticket_id,
        human_label=request.human_label,
    )
    
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return TicketRecord(
        id=ticket.id,
        text=ticket.text,
        action=ticket.action,
        reply=ticket.reply,
        tags=ticket.tags.split(",") if ticket.tags else [],
        reason=ticket.reason,
        created_at=ticket.created_at,
        human_label=ticket.human_label,
    )


@app.get("/tickets", response_model=List[TicketRecord])
def list_tickets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[TicketRecord]:
    """
    List support tickets with simple pagination.

    Returns a list of ticket records for monitoring or review.
    """
    tickets = crud.list_tickets(db=db, skip=skip, limit=limit)
    
    result = []
    for ticket in tickets:
        result.append(TicketRecord(
            id=ticket.id,
            text=ticket.text,
            action=ticket.action,
            reply=ticket.reply,
            tags=ticket.tags.split(",") if ticket.tags else [],
            reason=ticket.reason,
            created_at=ticket.created_at,
            human_label=ticket.human_label,
        ))
    
    return result
