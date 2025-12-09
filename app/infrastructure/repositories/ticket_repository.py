"""
CRUD operations for the Ticket model.

Provides functions to create, read, update, and delete support tickets
in the database using SQLAlchemy ORM.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.infrastructure.db.models import Ticket


def create_ticket(
    db: Session,
    text: str,
    action: Optional[str] = None,
    reply: Optional[str] = None,
    tags: Optional[List[str]] = None,
    reason: Optional[str] = None,
    human_label: Optional[str] = None,
) -> Ticket:
    """
    Create and persist a new Ticket in the database.

    Args:
        db: SQLAlchemy database session.
        text: Raw ticket text content.
        action: Optional action taken or recommended for the ticket.
        reply: Optional reply text.
        tags: Optional list of tags to attach (will be stored as string).
        reason: Optional explanation for the chosen action.
        human_label: Optional human feedback label.

    Returns:
        The newly created Ticket ORM instance.
    """
    tags_str = ",".join(tags) if tags is not None else None

    ticket = Ticket(
        text=text,
        action=action,
        reply=reply,
        tags=tags_str,
        reason=reason,
        human_label=human_label,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
    """
    Retrieve a single Ticket by its ID.

    Args:
        db: SQLAlchemy database session.
        ticket_id: Primary key of the ticket.

    Returns:
        The Ticket instance if found, otherwise None.
    """
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def list_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> List[Ticket]:
    """
    Retrieve a list of tickets with pagination.

    Args:
        db: SQLAlchemy database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        List of Ticket instances.
    """
    return db.query(Ticket).offset(skip).limit(limit).all()


def update_ticket_agent_result(
    db: Session,
    ticket_id: int,
    action: str,
    reply: Optional[str],
    tags: Optional[List[str]] = None,
    reason: Optional[str] = None,
) -> Optional[Ticket]:
    """
    Update a ticket with the result produced by the ticket agent.

    Args:
        db: SQLAlchemy database session.
        ticket_id: ID of the ticket to update.
        action: Agent-recommended action (e.g., 'reply', 'escalate', 'close').
        reply: Suggested reply content, if any.
        tags: Optional list of tags assigned by the agent.
        reason: Optional explanation of why this action was chosen.

    Returns:
        The updated Ticket instance if found, otherwise None.
    """
    ticket = get_ticket(db, ticket_id)

    if ticket is None:
        return None

    ticket.action = action
    ticket.reply = reply
    ticket.reason = reason

    if tags is not None:
        ticket.tags = ",".join(tags)

    db.commit()
    db.refresh(ticket)

    return ticket


def update_ticket_feedback(
    db: Session,
    ticket_id: int,
    human_label: str,
) -> Optional[Ticket]:
    """
    Update a ticket with human feedback on the agent's classification.

    Args:
        db: SQLAlchemy database session.
        ticket_id: ID of the ticket to update.
        human_label: Human-provided label/feedback.

    Returns:
        The updated Ticket instance if found, otherwise None.
    """
    ticket = get_ticket(db, ticket_id)

    if ticket is None:
        return None

    ticket.human_label = human_label

    db.commit()
    db.refresh(ticket)

    return ticket
