# 🚀 Migration Guide: Flat → Professional Structure

## 📋 Overview

**Goal:** Transform your flat structure into a production-ready, scalable architecture.

**Time Required:** 2-3 hours (careful work)

**Risk Level:** Low (we'll backup first)

---

## 🎯 Before & After

### **BEFORE (Current):**
```
app/
├── __init__.py
├── main.py              # 165 lines - All endpoints
├── agent_service.py     # 134 lines - Orchestrator
├── rag_service.py       # 138 lines - RAG logic
├── summariser.py        # 109 lines - Summarization
├── vectorstore.py       # 193 lines - Pinecone client
├── crud.py              # 157 lines - CRUD operations
├── db.py                # 47 lines - DB connection
├── models.py            # 40 lines - SQLAlchemy models
├── schemas.py           # 150 lines - Pydantic schemas
└── config.py            # 44 lines - Settings
```
**Total:** 11 files in one folder ❌

---

### **AFTER (Professional):**
```
app/
├── api/
│   ├── dependencies.py
│   └── v1/
│       └── endpoints.py
│
├── core/
│   ├── services/
│   │   ├── rag_service.py
│   │   └── summariser_service.py
│   ├── workflows/
│   │   └── ticket_workflow.py
│   └── llm/
│       └── prompts.py
│
├── infrastructure/
│   ├── db/
│   │   ├── connection.py
│   │   └── models.py
│   ├── repositories/
│   │   └── ticket_repository.py
│   ├── vectorstores/
│   │   └── pinecone_client.py
│   └── clients/
│       └── openai_client.py
│
├── config/
│   └── settings.py
│
├── schemas/
│   ├── requests.py
│   └── responses.py
│
└── main.py
```
**Total:** 7 folders, 15 files (organized by purpose) ✅

---

## 🛡️ Step 0: Backup Everything

```bash
cd /root/support_desk_assistant-1

# Create backup
cp -r app app_backup_$(date +%Y%m%d_%H%M%S)

# Verify backup exists
ls -la | grep app_backup
```

**Important:** Don't proceed until backup is confirmed! ✅

---

## 📁 Step 1: Create New Folder Structure

```bash
cd /root/support_desk_assistant-1

# Create API layer
mkdir -p app/api/v1

# Create Core layer
mkdir -p app/core/services
mkdir -p app/core/workflows
mkdir -p app/core/llm

# Create Infrastructure layer
mkdir -p app/infrastructure/db
mkdir -p app/infrastructure/repositories
mkdir -p app/infrastructure/vectorstores
mkdir -p app/infrastructure/clients

# Create Config layer
mkdir -p app/config

# Create Schemas layer
mkdir -p app/schemas

# Create test structure
mkdir -p tests/unit/services
mkdir -p tests/unit/workflows
mkdir -p tests/integration

# Create data folders
mkdir -p data/docs
mkdir -p data/database
mkdir -p data/logs

# Move documentation
mkdir -p docs
```

---

## 🔄 Step 2: Move Files (Carefully!)

### **2.1: Move API Layer**
```bash
# We'll split main.py in Step 4, for now just note it
# main.py will become:
#   - app/main.py (FastAPI app init)
#   - app/api/v1/endpoints.py (all endpoints)
#   - app/api/dependencies.py (dependency injection)
```

### **2.2: Move Core Layer (Business Logic)**
```bash
# Move orchestrator (agent_service)
cp app/agent_service.py app/core/workflows/ticket_workflow.py

# Move workers (services)
cp app/rag_service.py app/core/services/rag_service.py
cp app/summariser.py app/core/services/summariser_service.py
```

### **2.3: Move Infrastructure Layer**
```bash
# Database
cp app/db.py app/infrastructure/db/connection.py
cp app/models.py app/infrastructure/db/models.py

# Repositories
cp app/crud.py app/infrastructure/repositories/ticket_repository.py

# Vector stores
cp app/vectorstore.py app/infrastructure/vectorstores/pinecone_client.py
```

### **2.4: Move Config & Schemas**
```bash
# Config
cp app/config.py app/config/settings.py

# Schemas (we'll split in Step 4)
# For now just copy
cp app/schemas.py app/schemas/models.py
```

---

## 📝 Step 3: Create __init__.py Files

```bash
# Create all __init__.py files
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/core/__init__.py
touch app/core/services/__init__.py
touch app/core/workflows/__init__.py
touch app/core/llm/__init__.py
touch app/infrastructure/__init__.py
touch app/infrastructure/db/__init__.py
touch app/infrastructure/repositories/__init__.py
touch app/infrastructure/vectorstores/__init__.py
touch app/infrastructure/clients/__init__.py
touch app/config/__init__.py
touch app/schemas/__init__.py
```

---

## ✏️ Step 4: Update Imports in Moved Files

### **4.1: Update app/core/workflows/ticket_workflow.py**

**Find and replace in this file:**
```python
# OLD IMPORTS
from app.rag_service import RagService, get_rag_service
from app.summariser import SummariserService, get_summariser_service
from app import crud

# NEW IMPORTS
from app.core.services.rag_service import RagService, get_rag_service
from app.core.services.summariser_service import SummariserService, get_summariser_service
from app.infrastructure.repositories import ticket_repository
```

**Quick command:**
```bash
sed -i 's/from app.rag_service/from app.core.services.rag_service/g' app/core/workflows/ticket_workflow.py
sed -i 's/from app.summariser/from app.core.services.summariser_service/g' app/core/workflows/ticket_workflow.py
sed -i 's/from app import crud/from app.infrastructure.repositories import ticket_repository/g' app/core/workflows/ticket_workflow.py
```

---

### **4.2: Update app/core/services/rag_service.py**

**Find and replace:**
```python
# OLD IMPORTS
from app.config import get_settings
from app.vectorstore import VectorStoreClient, get_vectorstore_client

# NEW IMPORTS
from app.config.settings import get_settings
from app.infrastructure.vectorstores.pinecone_client import VectorStoreClient, get_vectorstore_client
```

**Quick command:**
```bash
sed -i 's/from app.config/from app.config.settings/g' app/core/services/rag_service.py
sed -i 's/from app.vectorstore/from app.infrastructure.vectorstores.pinecone_client/g' app/core/services/rag_service.py
```

---

### **4.3: Update app/core/services/summariser_service.py**

**Find and replace:**
```python
# OLD IMPORTS
from app.config import get_settings

# NEW IMPORTS
from app.config.settings import get_settings
```

**Quick command:**
```bash
sed -i 's/from app.config/from app.config.settings/g' app/core/services/summariser_service.py
```

---

### **4.4: Update app/infrastructure/db/connection.py**

**Find and replace:**
```python
# OLD IMPORTS
from app.config import get_settings

# NEW IMPORTS
from app.config.settings import get_settings
```

**Quick command:**
```bash
sed -i 's/from app.config/from app.config.settings/g' app/infrastructure/db/connection.py
```

---

### **4.5: Update app/infrastructure/db/models.py**

**Find and replace:**
```python
# OLD IMPORTS
from app.db import Base

# NEW IMPORTS
from app.infrastructure.db.connection import Base
```

**Quick command:**
```bash
sed -i 's/from app.db/from app.infrastructure.db.connection/g' app/infrastructure/db/models.py
```

---

### **4.6: Update app/infrastructure/repositories/ticket_repository.py**

**Find and replace:**
```python
# OLD IMPORTS
from app.models import Ticket

# NEW IMPORTS
from app.infrastructure.db.models import Ticket
```

**Quick command:**
```bash
sed -i 's/from app.models/from app.infrastructure.db.models/g' app/infrastructure/repositories/ticket_repository.py
```

---

### **4.7: Update app/infrastructure/vectorstores/pinecone_client.py**

**Find and replace:**
```python
# OLD IMPORTS
from app.config import get_settings

# NEW IMPORTS
from app.config.settings import get_settings
```

**Quick command:**
```bash
sed -i 's/from app.config/from app.config.settings/g' app/infrastructure/vectorstores/pinecone_client.py
```

---

## 🔧 Step 5: Split app/main.py into Multiple Files

### **5.1: Create app/api/dependencies.py**

```python
"""
Dependency injection helpers for FastAPI.
"""
from typing import Generator
from sqlalchemy.orm import Session

from app.infrastructure.db.connection import get_db as _get_db
from app.core.workflows.ticket_workflow import get_ticket_agent_service
from app.core.services.rag_service import get_rag_service
from app.core.services.summariser_service import get_summariser_service

# Re-export for convenience
get_db = _get_db
get_ticket_agent = get_ticket_agent_service
get_rag = get_rag_service
get_summariser = get_summariser_service
```

---

### **5.2: Create app/api/v1/endpoints.py**

```python
"""
API v1 endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_ticket_agent, get_rag, get_summariser
from app.schemas.requests import (
    RagQueryRequest,
    SummariseRequest,
    TicketAgentRequest,
    TicketFeedbackRequest,
)
from app.schemas.responses import (
    RagQueryResponse,
    RagSource,
    SummariseResponse,
    TicketAgentResponse,
    TicketRecord,
)
from app.infrastructure.repositories import ticket_repository
from app.core.workflows.ticket_workflow import TicketAgentService
from app.core.services.rag_service import RagService
from app.core.services.summariser_service import SummariserService

router = APIRouter()


@router.post("/rag/query", response_model=RagQueryResponse)
def rag_query(
    request: RagQueryRequest,
    rag_service: RagService = Depends(get_rag),
) -> RagQueryResponse:
    """Run a RAG query."""
    result = rag_service.answer(request.query)
    
    sources = []
    for match in result.get("sources", []):
        metadata = match.get("metadata", {})
        doc_name = metadata.get("source", match.get("id", "unknown"))
        snippet = metadata.get("text", "")
        sources.append(RagSource(doc_name=doc_name, snippet=snippet))
    
    return RagQueryResponse(answer=result.get("answer", ""), sources=sources)


@router.post("/summarise", response_model=SummariseResponse)
def summarise_text(
    request: SummariseRequest,
    summariser: SummariserService = Depends(get_summariser),
) -> SummariseResponse:
    """Summarise text and extract tags."""
    result = summariser.summarise(request.text)
    
    summary = result.get("summary", "")
    tags = result.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    
    return SummariseResponse(summary=summary, tags=tags)


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
```

---

### **5.3: Create new app/main.py**

```python
"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from app.api.v1 import endpoints

app = FastAPI(
    title="AI Support Desk Assistant",
    description="API for RAG-based support, summarisation, and ticket triage.",
    version="0.1.0",
)

# Include v1 router
app.include_router(endpoints.router, prefix="/api/v1", tags=["v1"])

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
```

---

## 📦 Step 6: Split schemas.py

### **6.1: Create app/schemas/requests.py**

```python
"""
Request schemas (Pydantic models for API inputs).
"""
from pydantic import BaseModel


class RagQueryRequest(BaseModel):
    """Request for RAG query."""
    query: str


class SummariseRequest(BaseModel):
    """Request for text summarization."""
    text: str


class TicketAgentRequest(BaseModel):
    """Request for ticket processing."""
    ticket: str


class TicketFeedbackRequest(BaseModel):
    """Request for ticket feedback."""
    ticket_id: int
    human_label: str
```

---

### **6.2: Create app/schemas/responses.py**

```python
"""
Response schemas (Pydantic models for API outputs).
"""
from datetime import datetime
from pydantic import BaseModel


class RagSource(BaseModel):
    """Source document in RAG response."""
    doc_name: str
    snippet: str


class RagQueryResponse(BaseModel):
    """Response for RAG query."""
    answer: str
    sources: list[RagSource]


class SummariseResponse(BaseModel):
    """Response for text summarization."""
    summary: str
    tags: list[str]


class TicketAgentResponse(BaseModel):
    """Response for ticket processing."""
    id: int
    action: str
    reply: str | None
    reason: str
    tags: list[str]


class TicketRecord(BaseModel):
    """Complete ticket record."""
    id: int
    text: str
    action: str
    reply: str | None
    tags: list[str] | None
    reason: str | None
    created_at: datetime
    human_label: str | None
```

---

### **6.3: Create app/schemas/__init__.py**

```python
"""
Schemas package.
"""
from app.schemas.requests import (
    RagQueryRequest,
    SummariseRequest,
    TicketAgentRequest,
    TicketFeedbackRequest,
)
from app.schemas.responses import (
    RagQueryResponse,
    RagSource,
    SummariseResponse,
    TicketAgentResponse,
    TicketRecord,
)

__all__ = [
    # Requests
    "RagQueryRequest",
    "SummariseRequest",
    "TicketAgentRequest",
    "TicketFeedbackRequest",
    # Responses
    "RagQueryResponse",
    "RagSource",
    "SummariseResponse",
    "TicketAgentResponse",
    "TicketRecord",
]
```

---

## 🧪 Step 7: Update scripts/ingest_docs.py

```python
# OLD IMPORTS
from app.config import get_settings
from app.vectorstore import get_vectorstore_client

# NEW IMPORTS
from app.config.settings import get_settings
from app.infrastructure.vectorstores.pinecone_client import get_vectorstore_client
```

**Quick command:**
```bash
sed -i 's/from app.config import/from app.config.settings import/g' scripts/ingest_docs.py
sed -i 's/from app.vectorstore import/from app.infrastructure.vectorstores.pinecone_client import/g' scripts/ingest_docs.py
```

---

## 🗑️ Step 8: Clean Up Old Files

**After verifying everything works:**

```bash
# Remove old files from app/ root
rm app/agent_service.py
rm app/rag_service.py
rm app/summariser.py
rm app/vectorstore.py
rm app/crud.py
rm app/db.py
rm app/models.py
rm app/config.py
rm app/schemas.py
# Keep app/main.py (we replaced its content)
```

---

## ✅ Step 9: Verify Everything Works

### **9.1: Check imports**
```bash
# Run Python to check for import errors
python -c "from app.main import app; print('✅ Imports OK')"
```

### **9.2: Start the server**
```bash
uvicorn app.main:app --reload --port 8000
```

### **9.3: Test endpoints**
```bash
# Test health check
curl http://localhost:8000/health

# Test RAG endpoint
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I reset my password?"}'

# Open API docs
# Visit: http://localhost:8000/docs
```

---

## 📋 Step 10: Update Documentation

### **10.1: Move docs**
```bash
mv ARCHITECTURE.txt docs/
mv END_TO_END_WORKFLOW.txt docs/
```

### **10.2: Update README.md**

Add to README:
```markdown
## Project Structure

```
app/
├── api/              # API endpoints (FastAPI)
├── core/             # Business logic
│   ├── services/     # Domain services
│   ├── workflows/    # Orchestrators
│   └── llm/          # LLM configs
├── infrastructure/   # External systems
│   ├── db/           # Database
│   ├── repositories/ # Data access
│   ├── vectorstores/ # Vector stores
│   └── clients/      # API clients
├── config/           # Settings
└── schemas/          # API contracts
```

## Running the Application

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Ingest documents
python scripts/ingest_docs.py

# Run tests
pytest tests/
```
```

---

## 🎯 Final Checklist

- [ ] Backup created
- [ ] All folders created
- [ ] Files copied to new locations
- [ ] Imports updated in all files
- [ ] main.py split into multiple files
- [ ] schemas.py split into requests/responses
- [ ] Old files removed
- [ ] Server starts without errors
- [ ] API docs accessible at /docs
- [ ] Test endpoint works
- [ ] Documentation updated
- [ ] .gitignore updated
- [ ] Backup deleted (after confirming everything works)

---

## 🚨 Troubleshooting

### **Import Error: "No module named 'app.xyz'"**
```bash
# Check if __init__.py exists in all folders
find app -type d -exec test -f {}/__init__.py \; -print
```

### **Server won't start**
```bash
# Check syntax errors
python -m py_compile app/main.py
python -m py_compile app/api/v1/endpoints.py
```

### **Tests failing**
```bash
# Update test imports
find tests -name "*.py" -exec sed -i 's/from app\./from app./g' {} +
```

---

## 🎉 Success!

Your project now has:
- ✅ Professional structure
- ✅ Clear separation of concerns
- ✅ Scalable architecture
- ✅ Easy to test
- ✅ Team-friendly
- ✅ Production-ready

**Next steps:**
1. Add more tests in `tests/`
2. Add API versioning docs
3. Set up CI/CD pipeline
4. Add monitoring/logging
5. Create Docker configuration

---

## 📚 Additional Resources

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Clean Architecture in Python](https://www.cosmicpython.com/)
- [Testing FastAPI Applications](https://fastapi.tiangolo.com/tutorial/testing/)

**Time to celebrate! 🎊 Your codebase is now enterprise-grade!**
