"""
Ticket Agent service.

Defines a high-level ticket agent service that orchestrates RAG, summarisation,
and CRUD operations to process support tickets and recommend actions.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.services.rag_service import RagService, get_rag_service
from app.infrastructure.repositories import ticket_repository


# Module-level cache for TicketAgentService singleton
_ticket_agent_service: Optional["TicketAgentService"] = None


class TicketAgentService:
    """
    Service for processing support tickets using AI-powered triage.

    Orchestrates RAG and CRUD operations to analyze tickets,
    recommend actions, and persist decisions.
    """

    def __init__(
        self,
        rag_service: RagService,
    ) -> None:
        """
        Initialize the ticket agent service.

        Args:
            rag_service: RAG service used for knowledge-base grounded answers and tag extraction.

        - Store the service instance for later use.
        - Configure any agent-level defaults (e.g., action types).
        """
        self._rag_service = rag_service
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
        # Use RAG to get answer AND tags in a single call
        rag_result = self._rag_service.answer(text)

        # Extract results from RAG (now includes tags!)
        answer = rag_result.get("answer", "")
        tags = rag_result.get("tags", [])
        confidence = rag_result.get("confidence", "low")
        
        # Ensure tags is a list
        if not isinstance(tags, list):
            tags = []
        
        # Check if RAG returned valid answer or insufficient context marker
        if answer and answer.strip() and "INSUFFICIENT_CONTEXT" not in answer:
            action = "reply"
            reason = "Generated reply using knowledge base context via RAG."
        else:
            action = "escalate"
            if "INSUFFICIENT_CONTEXT" in answer:
                reason = "Knowledge base lacks sufficient information; escalating to human agent."
            else:
                reason = "Could not generate automated reply; escalating to human agent."

        # Persist ticket to database
        ticket = ticket_repository.create_ticket(
            db=db,
            text=text,
            action=action,
            reply=answer if action == "reply" else None,
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

    Initializes the service on first call using shared RagService
    instance, and caches it for subsequent calls.

    Returns:
        TicketAgentService: The singleton ticket agent service.
    """
    global _ticket_agent_service

    if _ticket_agent_service is None:
        rag_service = get_rag_service()
        _ticket_agent_service = TicketAgentService(
            rag_service=rag_service,
        )

    return _ticket_agent_service


