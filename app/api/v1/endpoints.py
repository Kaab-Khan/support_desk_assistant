"""
API v1 endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_ticket_agent, get_rag, check_rate_limit
from app.schemas.requests import (
    RagQueryRequest,
    TicketAgentRequest,
    TicketFeedbackRequest,
)
from app.schemas.responses import (
    RagQueryResponse,
    RagSource,
    TicketAgentResponse,
    TicketRecord,
)
from app.infrastructure.repositories import ticket_repository
from app.core.workflows.ticket_workflow import TicketAgentService
from app.core.services.rag_service import RagService

router = APIRouter()


@router.post("/rag/query", response_model=RagQueryResponse)
def rag_query(
    request: RagQueryRequest,
    rag_service: RagService = Depends(get_rag),
    x_owner_key: Optional[str] = Header(default=None), #Add 
) -> RagQueryResponse:
    """Run a RAG query with optional conversation history."""
    result = rag_service.answer(
        query=request.query,
        conversation_history=request.conversation_history
    )

    sources = []
    for match in result.get("sources", []):
        metadata = match.get("metadata", {})
        doc_name = metadata.get("source", match.get("id", "unknown"))
        snippet = metadata.get("text", "")
        sources.append(RagSource(doc_name=doc_name, snippet=snippet))

    return RagQueryResponse(answer=result.get("answer", ""), sources=sources)


@router.post("/tickets/agent", response_model=TicketAgentResponse)
def process_ticket(
    request: TicketAgentRequest,
    db: Session = Depends(get_db),
    agent: TicketAgentService = Depends(get_ticket_agent),
) -> TicketAgentResponse:
    """Process a support ticket."""
    result = agent.process_ticket(db=db, text=request.ticket)

    return TicketAgentResponse(
        id=result["id"],
        action=result["action"],
        reply=result.get("reply"),
        reason=result.get("reason", ""),
        tags=result.get("tags", []),
    )


@router.post("/tickets/feedback", response_model=TicketRecord)
def submit_ticket_feedback(
    request: TicketFeedbackRequest,
    db: Session = Depends(get_db),
) -> TicketRecord:
    """Submit human feedback for a ticket."""
    ticket = ticket_repository.update_ticket_feedback(
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


@router.get("/tickets", response_model=List[TicketRecord])
def list_tickets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[TicketRecord]:
    """List tickets with pagination."""
    tickets = ticket_repository.list_tickets(db=db, skip=skip, limit=limit)

    result = []
    for ticket in tickets:
        result.append(
            TicketRecord(
                id=ticket.id,
                text=ticket.text,
                action=ticket.action,
                reply=ticket.reply,
                tags=ticket.tags.split(",") if ticket.tags else [],
                reason=ticket.reason,
                created_at=ticket.created_at,
                human_label=ticket.human_label,
            )
        )

    return result
