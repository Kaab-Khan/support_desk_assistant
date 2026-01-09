"""
Dependency injection helpers for FastAPI.
"""
from app.infrastructure.db.connection import get_db as _get_db
from app.core.workflows.ticket_workflow import get_ticket_agent_service
from app.core.services.rag_service import get_rag_service
from app.config.settings import get_settings
from fastapi import Header, HTTPException
from typing import Optional
import time

# Re-export for convenience
get_db = _get_db
get_ticket_agent = get_ticket_agent_service
get_rag = get_rag_service

# In-memory session usage tracking
#Format: {session_id: {count": int, "first_message_timestamp": float}}
SESSION_USAGE= {}

def check_rate_limit(
    session_id: str,
    x_owner_key: Optional[str] = Header(default=None),
    ) -> None:
    """
    Check and enforce rate limits based on session ID.

    Args:
        session_id (str): The session identifier from the client request
        x_owner_key (Optional[str]): Owner key header for bypassing limits

    Raises:
        HTTPException: If the rate limit is exceeded
    """
    settings = get_settings()

    # DEV MODE: No Limits
    if settings.APP_MODE == "dev":
        return
    
    # PROD MODE: Check owner bypass
    is_owner = bool(settings.OWNER_KEY) and (x_owner_key == settings.OWNER_KEY)
    if is_owner:
        return  # Owner has unlimited access
    
    # PROD MODE: Check if rate limiting is enabled
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    # Check session usage
    now = time.time()
    usage = SESSION_USAGE.get(session_id)
    
    if usage is None:
        # New session - create record
        SESSION_USAGE[session_id] = {"count": 1, "start_time": now}
        return
    
    # Check if window has expired
    window_duration = settings.SESSION_WINDOW_SECONDS
    
    if now - usage["start_time"] > window_duration:
        # Window expired - reset counter
        usage["count"] = 1
        usage["start_time"] = now
        return
    
    # Check if limit exceeded
    if usage["count"] >= settings.MAX_MESSAGES_PER_SESSION:
        time_until_reset = (usage["start_time"] + window_duration) - now
        hours_remaining = int(time_until_reset // 3600)
        minutes_remaining = int((time_until_reset % 3600) // 60)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Demo limit reached ({settings.MAX_MESSAGES_PER_SESSION} messages per {settings.SESSION_WINDOW_SECONDS // 3600} hours). "
                          f"Try again in {hours_remaining}h {minutes_remaining}m. "
                          f"For extended access, contact the developer.",
                "limit": settings.MAX_MESSAGES_PER_SESSION,
                "window_seconds": settings.SESSION_WINDOW_SECONDS,
                "time_until_reset_seconds": int(time_until_reset)
            }
        )
    
    # Increment counter
    usage["count"] += 1