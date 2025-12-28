"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import endpoints
from app.infrastructure.db.connection import init_db

app = FastAPI(
    title="AI Support Desk Assistant",
    description="API for RAG-based support, summarisation, and ticket triage.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only; lock down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database on application startup."""
    init_db()


# Include v1 router
app.include_router(endpoints.router, prefix="/api/v1", tags=["v1"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
