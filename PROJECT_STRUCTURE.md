# 🏗️ Professional Project Structure - Senior Developer Guide

## 📋 Overview

This document outlines a **production-ready, enterprise-grade** folder structure following **Clean Architecture** and **Separation of Concerns** principles.

---

## 🎯 Current vs Proposed Structure

### **CURRENT (Flat Structure):**
```
support_desk_assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                 # API endpoints
│   ├── agent_service.py        # Business logic
│   ├── rag_service.py          # Business logic
│   ├── summariser.py           # Business logic
│   ├── vectorstore.py          # External service client
│   ├── crud.py                 # Database operations
│   ├── db.py                   # Database config
│   ├── models.py               # ORM models
│   ├── schemas.py              # Pydantic schemas
│   └── config.py               # Settings
├── scripts/
│   └── ingest_docs.py
└── data/
    └── docs/
```

**Issues:**
- ❌ All files in one folder (hard to navigate)
- ❌ No clear separation of layers
- ❌ Mixing concerns (API, business logic, data access)
- ❌ Hard to scale (adding features = more clutter)
- ❌ Difficult to test (tight coupling)

---

### **PROPOSED (Layered Architecture):**

```
support_desk_assistant/
│
├── 📁 frontend/                          # PRESENTATION LAYER (Frontend)
│   ├── streamlit_app.py                 # Streamlit UI
│   ├── components/
│   │   ├── __init__.py
│   │   ├── ticket_form.py               # Ticket submission component
│   │   ├── rag_search.py                # Knowledge base search component
│   │   └── analytics_dashboard.py       # Analytics visualization
│   └── utils/
│       ├── __init__.py
│       └── formatters.py                # Display formatters
│
├── 📁 api/                               # API LAYER (Controllers)
│   ├── __init__.py
│   ├── main.py                          # FastAPI app initialization
│   ├── dependencies.py                  # Dependency injection
│   ├── middleware.py                    # Custom middleware
│   ├── v1/                              # API version 1
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── tickets.py               # POST /tickets/agent, GET /tickets
│   │   │   ├── rag.py                   # POST /rag/query
│   │   │   ├── summarise.py             # POST /summarise
│   │   │   ├── feedback.py              # POST /tickets/feedback
│   │   │   └── health.py                # GET /health, /metrics
│   │   └── router.py                    # Aggregate routers
│   └── v2/                              # Future API version
│       └── __init__.py
│
├── 📁 domain/                            # DOMAIN LAYER (Core Business Logic)
│   ├── __init__.py
│   ├── entities/                        # Domain entities (business objects)
│   │   ├── __init__.py
│   │   ├── ticket.py                    # Ticket entity
│   │   ├── rag_result.py                # RAG result entity
│   │   └── summary.py                   # Summary entity
│   ├── value_objects/                   # Immutable value objects
│   │   ├── __init__.py
│   │   ├── ticket_action.py             # Enum: reply, escalate, close
│   │   └── feedback_label.py            # Enum: correct, incorrect, etc.
│   └── interfaces/                      # Abstract interfaces (ports)
│       ├── __init__.py
│       ├── i_rag_service.py             # RAG interface
│       ├── i_summariser_service.py      # Summariser interface
│       ├── i_vectorstore.py             # Vector store interface
│       └── i_ticket_repository.py       # Ticket repository interface
│
├── 📁 application/                       # APPLICATION LAYER (Use Cases/Services)
│   ├── __init__.py
│   ├── services/                        # Business logic services
│   │   ├── __init__.py
│   │   ├── ticket_agent_service.py      # Orchestrates ticket processing
│   │   ├── rag_service.py               # RAG logic
│   │   ├── summariser_service.py        # Summarization logic
│   │   └── analytics_service.py         # Analytics/reporting logic
│   ├── use_cases/                       # Specific use cases
│   │   ├── __init__.py
│   │   ├── process_ticket.py            # Use case: Process new ticket
│   │   ├── query_knowledge_base.py      # Use case: Query RAG
│   │   ├── submit_feedback.py           # Use case: Submit human feedback
│   │   └── generate_report.py           # Use case: Generate analytics
│   └── dto/                             # Data Transfer Objects
│       ├── __init__.py
│       ├── ticket_request.py
│       ├── ticket_response.py
│       └── rag_request.py
│
├── 📁 infrastructure/                    # INFRASTRUCTURE LAYER (External Services)
│   ├── __init__.py
│   ├── database/                        # Database implementations
│   │   ├── __init__.py
│   │   ├── connection.py                # Database connection (db.py)
│   │   ├── models/                      # ORM models
│   │   │   ├── __init__.py
│   │   │   ├── ticket_model.py          # SQLAlchemy Ticket model
│   │   │   └── base.py                  # Base model
│   │   └── repositories/                # Repository implementations
│   │       ├── __init__.py
│   │       ├── ticket_repository.py     # Ticket CRUD operations
│   │       └── base_repository.py       # Base repository pattern
│   ├── external_services/               # External API clients
│   │   ├── __init__.py
│   │   ├── openai_client.py             # OpenAI API wrapper
│   │   ├── pinecone_client.py           # Pinecone API wrapper
│   │   └── vectorstore_client.py        # Vector store implementation
│   ├── cache/                           # Caching layer
│   │   ├── __init__.py
│   │   ├── redis_cache.py               # Redis cache (future)
│   │   └── in_memory_cache.py           # In-memory cache
│   └── messaging/                       # Message queue (future)
│       ├── __init__.py
│       └── rabbitmq_client.py
│
├── 📁 shared/                            # SHARED LAYER (Common Utilities)
│   ├── __init__.py
│   ├── config/                          # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py                  # Application settings
│   │   └── logging_config.py            # Logging configuration
│   ├── schemas/                         # Pydantic schemas (API contracts)
│   │   ├── __init__.py
│   │   ├── requests/
│   │   │   ├── __init__.py
│   │   │   ├── rag_query_request.py
│   │   │   ├── ticket_request.py
│   │   │   └── feedback_request.py
│   │   └── responses/
│   │       ├── __init__.py
│   │       ├── rag_query_response.py
│   │       ├── ticket_response.py
│   │       └── error_response.py
│   ├── exceptions/                      # Custom exceptions
│   │   ├── __init__.py
│   │   ├── base_exceptions.py
│   │   ├── domain_exceptions.py
│   │   ├── repository_exceptions.py
│   │   └── service_exceptions.py
│   ├── utils/                           # Utility functions
│   │   ├── __init__.py
│   │   ├── text_processing.py           # Text utilities
│   │   ├── date_utils.py                # Date/time utilities
│   │   └── validators.py                # Custom validators
│   └── constants/                       # Application constants
│       ├── __init__.py
│       ├── actions.py                   # Action constants
│       └── error_codes.py               # Error code constants
│
├── 📁 tests/                             # TEST LAYER
│   ├── __init__.py
│   ├── unit/                            # Unit tests
│   │   ├── __init__.py
│   │   ├── test_services/
│   │   │   ├── __init__.py
│   │   │   ├── test_ticket_agent_service.py
│   │   │   ├── test_rag_service.py
│   │   │   └── test_summariser_service.py
│   │   ├── test_repositories/
│   │   │   ├── __init__.py
│   │   │   └── test_ticket_repository.py
│   │   └── test_utils/
│   │       ├── __init__.py
│   │       └── test_text_processing.py
│   ├── integration/                     # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   │   ├── __init__.py
│   │   │   ├── test_tickets_endpoint.py
│   │   │   └── test_rag_endpoint.py
│   │   └── test_database/
│   │       ├── __init__.py
│   │       └── test_ticket_repository.py
│   ├── e2e/                             # End-to-end tests
│   │   ├── __init__.py
│   │   └── test_ticket_workflow.py
│   ├── fixtures/                        # Test fixtures
│   │   ├── __init__.py
│   │   ├── mock_data.py
│   │   └── test_documents.py
│   └── conftest.py                      # Pytest configuration
│
├── 📁 scripts/                           # SCRIPTS & UTILITIES
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ingest_docs.py               # Document ingestion
│   │   ├── seed_database.py             # Database seeding
│   │   └── backup_database.py           # Database backup
│   ├── deployment/
│   │   ├── __init__.py
│   │   ├── migrate_db.py                # Database migrations
│   │   └── health_check.py              # Deployment health check
│   └── monitoring/
│       ├── __init__.py
│       └── performance_metrics.py       # Performance monitoring
│
├── 📁 migrations/                        # DATABASE MIGRATIONS (Alembic)
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── alembic.ini
│
├── 📁 docs/                              # DOCUMENTATION
│   ├── api/
│   │   ├── openapi.yaml                 # OpenAPI spec
│   │   └── endpoints.md                 # Endpoint documentation
│   ├── architecture/
│   │   ├── architecture_diagram.png
│   │   ├── ARCHITECTURE.txt
│   │   └── data_flow.md
│   ├── deployment/
│   │   ├── docker_setup.md
│   │   └── production_checklist.md
│   └── development/
│       ├── setup_guide.md
│       └── contribution_guide.md
│
├── 📁 data/                              # DATA STORAGE
│   ├── docs/                            # Knowledge base documents
│   ├── database/                        # SQLite database files
│   │   └── support.db
│   └── logs/                            # Application logs
│       └── app.log
│
├── 📁 docker/                            # DOCKER CONFIGURATION
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── 📄 .env.example                       # Environment variables template
├── 📄 .env                               # Environment variables (gitignored)
├── 📄 .gitignore                         # Git ignore rules
├── 📄 pyproject.toml                     # Python project config
├── 📄 requirements.txt                   # Production dependencies
├── 📄 requirements-dev.txt               # Development dependencies
├── 📄 Makefile                           # Common commands
├── 📄 README.md                          # Project overview
└── 📄 setup.py                           # Package setup
```

---

## 🏛️ Architecture Layers Explained

### **1. 📱 PRESENTATION LAYER (frontend/)**
**Purpose:** User Interface / User Experience

**Contents:**
- Streamlit UI components
- React/Vue components (if applicable)
- CLI interfaces
- Display formatting logic

**Rules:**
- ✅ Only handles UI rendering
- ✅ Calls API layer (never business logic directly)
- ❌ No business logic
- ❌ No database access

**Example:**
```python
# frontend/components/ticket_form.py
import streamlit as st
import requests

def render_ticket_form():
    """Render ticket submission form."""
    with st.form("ticket_form"):
        ticket_text = st.text_area("Describe your issue")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            # Call API (not business logic directly!)
            response = requests.post(
                "http://localhost:8000/api/v1/tickets/agent",
                json={"ticket": ticket_text}
            )
            st.success(f"Ticket #{response.json()['id']} created!")
```

---

### **2. 🌐 API LAYER (api/)**
**Purpose:** HTTP Request/Response Handling

**Contents:**
- FastAPI endpoints (controllers)
- Request validation
- Response formatting
- API versioning (v1, v2)

**Rules:**
- ✅ Thin layer (no business logic)
- ✅ Validates input (using schemas)
- ✅ Calls application services
- ✅ Handles HTTP concerns (status codes, headers)
- ❌ No business logic
- ❌ No direct database access

**Example:**
```python
# api/v1/endpoints/tickets.py
from fastapi import APIRouter, Depends, HTTPException
from application.use_cases.process_ticket import ProcessTicketUseCase
from shared.schemas.requests import TicketRequest
from shared.schemas.responses import TicketResponse

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/agent", response_model=TicketResponse)
async def process_ticket(
    request: TicketRequest,
    use_case: ProcessTicketUseCase = Depends()
):
    """Process a new support ticket."""
    try:
        result = use_case.execute(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### **3. 💼 APPLICATION LAYER (application/)**
**Purpose:** Business Logic / Use Cases / Orchestration

**Contents:**
- Services (orchestrate multiple operations)
- Use cases (specific business scenarios)
- DTOs (data transfer objects)

**Rules:**
- ✅ Contains business logic
- ✅ Orchestrates domain entities
- ✅ Calls repositories for data
- ✅ Calls external services
- ❌ No HTTP concerns
- ❌ No UI logic
- ❌ No SQL queries

**Example:**
```python
# application/use_cases/process_ticket.py
from domain.interfaces import ITicketRepository, IRagService
from domain.entities import Ticket
from domain.value_objects import TicketAction

class ProcessTicketUseCase:
    """Use case: Process a new support ticket."""
    
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        rag_service: IRagService
    ):
        self._ticket_repo = ticket_repo
        self._rag_service = rag_service
    
    def execute(self, request):
        """Execute the use case."""
        # Business logic here
        rag_result = self._rag_service.answer(request.ticket)
        
        # Decide action
        action = (
            TicketAction.REPLY if rag_result.answer 
            else TicketAction.ESCALATE
        )
        
        # Create ticket entity
        ticket = Ticket(
            text=request.ticket,
            action=action,
            reply=rag_result.answer
        )
        
        # Save via repository
        saved_ticket = self._ticket_repo.save(ticket)
        
        return saved_ticket
```

---

### **4. 🏢 DOMAIN LAYER (domain/)**
**Purpose:** Core Business Entities & Interfaces

**Contents:**
- Entities (business objects with identity)
- Value objects (immutable values)
- Domain interfaces (contracts/ports)
- Domain exceptions

**Rules:**
- ✅ Pure business logic (no frameworks)
- ✅ Framework-agnostic
- ✅ Defines contracts (interfaces)
- ❌ No dependencies on other layers
- ❌ No database code
- ❌ No external service calls

**Example:**
```python
# domain/entities/ticket.py
from dataclasses import dataclass
from datetime import datetime
from domain.value_objects import TicketAction

@dataclass
class Ticket:
    """Core business entity: Support Ticket."""
    id: int | None = None
    text: str
    action: TicketAction
    reply: str | None = None
    tags: list[str] = None
    created_at: datetime = None
    
    def can_auto_reply(self) -> bool:
        """Business rule: Can this ticket be auto-replied?"""
        return self.action == TicketAction.REPLY and self.reply is not None
    
    def mark_escalated(self, reason: str):
        """Business rule: Escalate ticket."""
        self.action = TicketAction.ESCALATE
        self.reply = None
```

```python
# domain/interfaces/i_ticket_repository.py
from abc import ABC, abstractmethod
from domain.entities import Ticket

class ITicketRepository(ABC):
    """Interface: Ticket repository contract."""
    
    @abstractmethod
    def save(self, ticket: Ticket) -> Ticket:
        """Save a ticket."""
        pass
    
    @abstractmethod
    def find_by_id(self, ticket_id: int) -> Ticket | None:
        """Find ticket by ID."""
        pass
    
    @abstractmethod
    def list_all(self, skip: int, limit: int) -> list[Ticket]:
        """List all tickets."""
        pass
```

---

### **5. 🔧 INFRASTRUCTURE LAYER (infrastructure/)**
**Purpose:** Technical Implementations & External Services

**Contents:**
- Database implementations (SQLAlchemy)
- Repository implementations
- External API clients (OpenAI, Pinecone)
- Caching implementations
- Message queues

**Rules:**
- ✅ Implements domain interfaces
- ✅ Handles technical details (SQL, HTTP, etc.)
- ✅ Framework-specific code here
- ❌ No business logic

**Example:**
```python
# infrastructure/database/repositories/ticket_repository.py
from sqlalchemy.orm import Session
from domain.interfaces import ITicketRepository
from domain.entities import Ticket
from infrastructure.database.models import TicketModel

class TicketRepository(ITicketRepository):
    """SQLAlchemy implementation of ticket repository."""
    
    def __init__(self, db: Session):
        self._db = db
    
    def save(self, ticket: Ticket) -> Ticket:
        """Save ticket to database."""
        db_ticket = TicketModel(
            text=ticket.text,
            action=ticket.action.value,
            reply=ticket.reply,
            tags=",".join(ticket.tags or [])
        )
        self._db.add(db_ticket)
        self._db.commit()
        self._db.refresh(db_ticket)
        
        # Convert back to domain entity
        return self._to_entity(db_ticket)
    
    def find_by_id(self, ticket_id: int) -> Ticket | None:
        """Find ticket by ID."""
        db_ticket = self._db.query(TicketModel).filter(
            TicketModel.id == ticket_id
        ).first()
        
        return self._to_entity(db_ticket) if db_ticket else None
    
    def _to_entity(self, db_ticket: TicketModel) -> Ticket:
        """Convert ORM model to domain entity."""
        return Ticket(
            id=db_ticket.id,
            text=db_ticket.text,
            action=TicketAction(db_ticket.action),
            reply=db_ticket.reply,
            tags=db_ticket.tags.split(",") if db_ticket.tags else [],
            created_at=db_ticket.created_at
        )
```

---

### **6. 🔀 SHARED LAYER (shared/)**
**Purpose:** Common Code Used Across Layers

**Contents:**
- Configuration
- Pydantic schemas (API contracts)
- Custom exceptions
- Utility functions
- Constants

**Rules:**
- ✅ Reusable across all layers
- ✅ No business logic
- ✅ Pure functions preferred

**Example:**
```python
# shared/exceptions/service_exceptions.py
class ServiceException(Exception):
    """Base exception for service errors."""
    pass

class RagServiceException(ServiceException):
    """Exception raised by RAG service."""
    pass

class VectorStoreException(ServiceException):
    """Exception raised by vector store."""
    pass
```

---

## 🎯 Benefits of This Structure

### **1. Separation of Concerns**
- Each layer has ONE responsibility
- Easy to understand and maintain

### **2. Testability**
```python
# Easy to mock dependencies
def test_process_ticket_use_case():
    # Mock repository
    mock_repo = Mock(spec=ITicketRepository)
    # Mock RAG service
    mock_rag = Mock(spec=IRagService)
    
    # Test use case in isolation
    use_case = ProcessTicketUseCase(mock_repo, mock_rag)
    result = use_case.execute(request)
    
    assert result.action == TicketAction.REPLY
```

### **3. Flexibility**
- Swap implementations without changing business logic
- Example: Switch from SQLite to PostgreSQL
  - Only change `infrastructure/database/repositories/`
  - No changes to `application/` or `domain/`

### **4. Scalability**
- Add new features without touching existing code
- Add API v2 without affecting v1
- Add new endpoints easily

### **5. Team Collaboration**
- Frontend team works on `frontend/`
- Backend team works on `api/`
- Business logic team works on `application/`
- Clear boundaries = less conflicts

---

## 📊 Dependency Flow (Dependency Inversion)

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│                      (frontend/)                         │
│                           │                              │
│                           ▼                              │
│                     API LAYER                            │
│                      (api/)                              │
│                           │                              │
│                           ▼                              │
│                  APPLICATION LAYER                       │
│              (application/services/)                     │
│                           │                              │
│                  ┌────────┴────────┐                     │
│                  ▼                 ▼                     │
│            DOMAIN LAYER    INFRASTRUCTURE LAYER          │
│            (domain/)          (infrastructure/)          │
│           [Interfaces]        [Implementations]          │
│                                                           │
│  All layers can use ──────► SHARED LAYER (shared/)       │
└─────────────────────────────────────────────────────────┘

Dependency Rule: Inner layers DON'T know about outer layers
```

---

## 🚀 Migration Strategy

### **Phase 1: Create Structure**
```bash
mkdir -p api/v1/endpoints
mkdir -p application/{services,use_cases,dto}
mkdir -p domain/{entities,value_objects,interfaces}
mkdir -p infrastructure/{database,external_services}
mkdir -p shared/{config,schemas,exceptions,utils}
mkdir -p tests/{unit,integration,e2e}
```

### **Phase 2: Move Files**
```
app/main.py              → api/main.py
app/agent_service.py     → application/services/ticket_agent_service.py
app/rag_service.py       → application/services/rag_service.py
app/summariser.py        → application/services/summariser_service.py
app/crud.py              → infrastructure/database/repositories/ticket_repository.py
app/models.py            → infrastructure/database/models/ticket_model.py
app/db.py                → infrastructure/database/connection.py
app/schemas.py           → shared/schemas/*
app/config.py            → shared/config/settings.py
app/vectorstore.py       → infrastructure/external_services/vectorstore_client.py
```

### **Phase 3: Refactor Imports**
Update all imports to reflect new structure.

### **Phase 4: Add Tests**
Create comprehensive test suite in `tests/`.

---

## 📝 File Naming Conventions

- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case()`
- **Constants:** `UPPER_SNAKE_CASE`
- **Test files:** `test_*.py`
- **Interfaces:** `I*.py` (e.g., `i_repository.py`)

---

## ✅ Best Practices

1. **Keep layers independent**
   - Domain layer has NO dependencies on other layers
   - Infrastructure implements domain interfaces

2. **Use dependency injection**
   - Services receive dependencies via constructor
   - Easy to mock for testing

3. **One class per file** (exceptions for related classes)

4. **Group by feature, not by type** (when possible)

5. **Write tests for each layer**

6. **Document public APIs**

7. **Use type hints everywhere**

---

## 🎓 Summary

This structure follows **Clean Architecture** principles:
- ✅ Independent of frameworks
- ✅ Testable
- ✅ Independent of UI
- ✅ Independent of database
- ✅ Independent of external services

**Result:** Maintainable, scalable, production-ready codebase! 🚀
