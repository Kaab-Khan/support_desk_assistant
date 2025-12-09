"""
Dependency injection helpers for FastAPI.
"""
from app.infrastructure.db.connection import get_db as _get_db
from app.core.workflows.ticket_workflow import get_ticket_agent_service
from app.core.services.rag_service import get_rag_service

# Re-export for convenience
get_db = _get_db
get_ticket_agent = get_ticket_agent_service
get_rag = get_rag_service
