"""
SQLAlchemy ORM models for database tables.

Defines the database schema for support tickets and related entities.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.infrastructure.db.connection import Base


class Ticket(Base):
    """
    ORM model for support tickets.

    Attributes:
        id: Primary key identifier
        text: The support ticket text content
        action: The action taken (e.g., 'auto_reply', 'escalate')
        reply: The reply text, if any
        tags: Tags assigned to the ticket (stored as JSON or comma-separated)
        reason: Explanation for the action taken
        created_at: Timestamp when the ticket was created
        human_label: Human feedback label (e.g., 'correct', 'wrong_action', 'wrong_reply')
    """

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    action = Column(String, nullable=False)
    reply = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    human_label = Column(String, nullable=True)
