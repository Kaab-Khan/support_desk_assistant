"""
Ticket Agent service.

Defines a high-level ticket agent service that orchestrates RAG, summarisation,
and CRUD operations to process support tickets and recommend actions.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.rag_service import RagService, get_rag_service
from app.summariser import SummariserService, get_summariser_service
from app import crud


# Module-level cache for TicketAgentService singleton
_ticket_agent_service: Optional["TicketAgentService"] = None


class TicketAgentService:
    """
    Service for processing support tickets using AI-powered triage.
    
    Orchestrates RAG, summarisation, and CRUD operations to analyze tickets,
    recommend actions, and persist decisions.
    """
    
    def __init__(
        self,
        rag_service: RagService,
        summariser_service: SummariserService,
    ) -> None:
        """
        Initialize the ticket agent service.

        Args:
            rag_service: RAG service used for knowledge-base grounded answers.
            summariser_service: Service used for summarisation/tagging helpers.

        - Store the service instances for later use.
        - Configure any agent-level defaults (e.g., action types).
        """
        self._rag_service = rag_service
        self._summariser = summariser_service
        self._default_actions = ["reply", "escalate", "close"]
    
    def process_ticket(
        self,
        db: Session,
        text: str,
    ) -> Dict[str, Any]:
        """
        Process a new ticket and return the agent's decision.

        Args:
            db: SQLAlchemy database session.
            text: Raw support ticket text.

        Returns:
            Dictionary containing fields such as:
                - "id": int                - Ticket ID in the database
                - "action": str            - Recommended action ('reply', 'escalate', 'close', etc.)
                - "reply": Optional[str]   - Suggested reply content, if applicable
                - "tags": List[str]        - Tags/categories for the ticket
                - "reason": Optional[str]  - Explanation of the decision

        - Use RAG and/or summarisation to interpret the ticket.
        - Decide an action and generate a reply/reason.
        - Persist the ticket via CRUD (create_ticket / update_ticket_agent_result).
        """
        # Use RAG to propose a reply grounded in knowledge base
        rag_result = self._rag_service.answer(text)
        
        # Use summariser to get tags
        summary_result = self._summariser.summarise(text)
        
        # Extract tags from summary result
        tags = summary_result.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        
        # Decide action based on RAG result
        answer = rag_result.get("answer", "")
        if answer and answer.strip():
            action = "reply"
            reason = "Generated reply using knowledge base context via RAG."
        else:
            action = "escalate"
            reason = "Could not generate automated reply; escalating to human agent."
        
        # Persist ticket to database
        ticket = crud.create_ticket(
            db=db,
            text=text,
            action=action,
            reply=answer if answer else None,
            tags=tags,
            reason=reason,
            human_label=None,
        )
        
        # Build and return response
        return {
            "id": ticket.id,
            "action": ticket.action,
            "reply": ticket.reply,
            "tags": tags,
            "reason": ticket.reason,
        }


def get_ticket_agent_service() -> TicketAgentService:
    """
    Return a singleton instance of TicketAgentService.

    Initializes the service on first call using shared RagService and
    SummariserService instances, and caches it for subsequent calls.

    Returns:
        TicketAgentService: The singleton ticket agent service.
    """
    global _ticket_agent_service
    
    if _ticket_agent_service is None:
        rag_service = get_rag_service()
        summariser_service = get_summariser_service()
        _ticket_agent_service = TicketAgentService(
            rag_service=rag_service,
            summariser_service=summariser_service,
        )
    
    return _ticket_agent_service