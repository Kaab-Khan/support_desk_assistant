# 🏗️ Simple & Clean Project Structure

## 🎯 Philosophy: "Just Enough Structure"

**Goals:**
- ✅ Clear organization (not overwhelming)
- ✅ Easy to navigate
- ✅ Room to grow
- ❌ Not over-engineered
- ❌ Not too many nested folders

---

## 📁 Current vs Proposed

### **CURRENT (Flat - 11 files in one folder):**
```
app/
├── __init__.py
├── main.py              # Everything mixed
├── agent_service.py
├── rag_service.py
├── summariser.py
├── vectorstore.py
├── crud.py
├── db.py
├── models.py
├── schemas.py
└── config.py
```
**Issue:** Hard to find things as project grows

---

### **PROPOSED (Simple 3-Layer):**
```
support_desk_assistant/
│
├── 📁 app/
│   │
│   ├── 📁 api/                     # Layer 1: API (HTTP handling)
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI app + all endpoints (keep together)
│   │
│   ├── 📁 services/                # Layer 2: Business Logic
│   │   ├── __init__.py
│   │   ├── ticket_agent.py         # Orchestrates ticket processing
│   │   ├── rag.py                  # RAG logic
│   │   ├── summariser.py           # Summarization
│   │   └── vectorstore.py          # Pinecone client
│   │
│   ├── 📁 database/                # Layer 3: Database
│   │   ├── __init__.py
│   │   ├── connection.py           # DB setup
│   │   ├── models.py               # SQLAlchemy models
│   │   └── crud.py                 # CRUD operations
│   │
│   └── 📁 core/                    # Shared: Config & Schemas
│       ├── __init__.py
│       ├── config.py               # Settings
│       └── schemas.py              # Pydantic models
│
├── 📁 scripts/                     # Utility scripts
│   ├── __init__.py
│   └── ingest_docs.py             # Document ingestion
│
├── 📁 tests/                       # Tests (start simple)
│   ├── __init__.py
│   └── test_api.py                # Basic API tests
│
├── 📁 data/                        # Data files
│   ├── docs/                      # Knowledge base documents
│   └── database/                  # SQLite files
│       └── support.db
│
├── 📁 docs/                        # Documentation
│   ├── ARCHITECTURE.txt
│   └── END_TO_END_WORKFLOW.txt
│
├── .env.example
├── .env
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── Makefile
└── README.md
```

---

## 🎯 The 3-Layer Pattern

```
┌─────────────────────────────────────────┐
│  Layer 1: API (app/api/)                │
│  • Handles HTTP requests                │
│  • FastAPI endpoints                    │
│  • Keep all endpoints in main.py       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Layer 2: SERVICES (app/services/)      │
│  • Business logic                       │
│  • RAG, Summariser, Agent               │
│  • Vectorstore client                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Layer 3: DATABASE (app/database/)      │
│  • Database connection                  │
│  • ORM models                           │
│  • CRUD operations                      │
└─────────────────────────────────────────┘

         All layers use ↓
         
┌─────────────────────────────────────────┐
│  CORE (app/core/)                       │
│  • Config (settings)                    │
│  • Schemas (API contracts)              │
└─────────────────────────────────────────┘
```

---

## 📋 Migration Guide (Simple!)

### **Step 1: Create Folders**
```bash
cd /root/support_desk_assistant-1

# Create new structure
mkdir -p app/api
mkdir -p app/services
mkdir -p app/database
mkdir -p app/core
mkdir -p tests
mkdir -p docs
mkdir -p data/database
```

### **Step 2: Move Files (Easy Mapping)**

```bash
# API Layer (keep main.py as-is, just move it)
# No need to split endpoints yet!
mv app/main.py app/api/main.py

# Services Layer
mv app/agent_service.py app/services/ticket_agent.py
mv app/rag_service.py app/services/rag.py
mv app/summariser.py app/services/summariser.py
mv app/vectorstore.py app/services/vectorstore.py

# Database Layer
mv app/db.py app/database/connection.py
mv app/models.py app/database/models.py
mv app/crud.py app/database/crud.py

# Core Layer
mv app/config.py app/core/config.py
mv app/schemas.py app/core/schemas.py

# Documentation
mv ARCHITECTURE.txt docs/
mv END_TO_END_WORKFLOW.txt docs/
```

### **Step 3: Add __init__.py Files**
```bash
touch app/api/__init__.py
touch app/services/__init__.py
touch app/database/__init__.py
touch app/core/__init__.py
```

### **Step 4: Update Imports (Find & Replace)**

**In all files, replace:**

| Old Import | New Import |
|-----------|-----------|
| `from app.main` | `from app.api.main` |
| `from app.agent_service` | `from app.services.ticket_agent` |
| `from app.rag_service` | `from app.services.rag` |
| `from app.summariser` | `from app.services.summariser` |
| `from app.vectorstore` | `from app.services.vectorstore` |
| `from app.db` | `from app.database.connection` |
| `from app.models` | `from app.database.models` |
| `from app.crud` | `from app.database.crud` |
| `from app.config` | `from app.core.config` |
| `from app.schemas` | `from app.core.schemas` |

**Quick way to do it:**
```bash
# Use sed to replace imports (backup first!)
find app -name "*.py" -exec sed -i.bak 's/from app.agent_service/from app.services.ticket_agent/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.rag_service/from app.services.rag/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.summariser/from app.services.summariser/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.vectorstore/from app.services.vectorstore/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.db/from app.database.connection/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.models/from app.database.models/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.crud/from app.database.crud/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.config/from app.core.config/g' {} +
find app -name "*.py" -exec sed -i.bak 's/from app.schemas/from app.core.schemas/g' {} +

# Remove backup files
find app -name "*.bak" -delete
```

### **Step 5: Update Run Command**
```bash
# Old
uvicorn app.main:app --reload

# New
uvicorn app.api.main:app --reload
```

---

## 📂 Detailed Structure

### **app/api/main.py** (API Layer)
```python
"""
FastAPI application with all endpoints.
Keep all 5 endpoints here - no need to split yet!
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.ticket_agent import get_ticket_agent_service
from app.services.rag import get_rag_service
from app.services.summariser import get_summariser_service
from app.core.schemas import (
    RagQueryRequest, RagQueryResponse,
    TicketAgentRequest, TicketAgentResponse,
    # ... etc
)

app = FastAPI(title="AI Support Desk Assistant", version="0.1.0")

# All your 5 endpoints stay here exactly as they are now!
@app.post("/rag/query")
def rag_query(...):
    pass

@app.post("/summarise")
def summarise_text(...):
    pass

@app.post("/tickets/agent")
def process_ticket(...):
    pass

@app.post("/tickets/feedback")
def submit_feedback(...):
    pass

@app.get("/tickets")
def list_tickets(...):
    pass
```

### **app/services/** (Business Logic)
- `ticket_agent.py` - Orchestrates ticket processing
- `rag.py` - RAG implementation
- `summariser.py` - Summarization logic
- `vectorstore.py` - Pinecone client

**No changes to code, just new location!**

### **app/database/** (Data Access)
- `connection.py` - Database setup (from db.py)
- `models.py` - SQLAlchemy models
- `crud.py` - CRUD operations

### **app/core/** (Shared)
- `config.py` - Application settings
- `schemas.py` - Pydantic models

---

## 🎯 Final Structure (Visual)

```
app/
├── api/
│   └── main.py              ← All 5 endpoints (80 lines)
│
├── services/
│   ├── ticket_agent.py      ← Orchestration (130 lines)
│   ├── rag.py               ← RAG logic (120 lines)
│   ├── summariser.py        ← Summarization (90 lines)
│   └── vectorstore.py       ← Pinecone client (180 lines)
│
├── database/
│   ├── connection.py        ← DB setup (45 lines)
│   ├── models.py            ← ORM models (40 lines)
│   └── crud.py              ← CRUD ops (150 lines)
│
└── core/
    ├── config.py            ← Settings (35 lines)
    └── schemas.py           ← Pydantic (150 lines)
```

**Total:** 4 folders, 11 files (same as before, just organized!)

---

## ✅ Benefits

### **Before:**
```
app/
└── 11 files mixed together
    ❌ Hard to find "where is database code?"
    ❌ Hard to find "where is API code?"
    ❌ Everything looks the same
```

### **After:**
```
app/
├── api/       → "All API stuff here" ✅
├── services/  → "All business logic here" ✅
├── database/  → "All database stuff here" ✅
└── core/      → "All shared stuff here" ✅
```

**Advantages:**
1. ✅ **Clear organization** without being complex
2. ✅ **Easy to navigate** (4 folders vs 1)
3. ✅ **Professional** but not over-engineered
4. ✅ **Room to grow** (can split endpoints later if needed)
5. ✅ **Quick migration** (30 minutes max)

---

## 🚀 Quick Commands

Create a simple `Makefile`:

```makefile
.PHONY: run test ingest

run:
	uvicorn app.api.main:app --reload --port 8000

test:
	pytest tests/ -v

ingest:
	python scripts/ingest_docs.py

install:
	pip install -r requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

**Usage:**
```bash
make run      # Start server
make test     # Run tests
make ingest   # Load documents
```

---

## 📝 .gitignore (Update)

```
# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/

# Environment
.env
.venv
venv/

# Data
data/database/*.db
data/logs/*.log

# IDE
.vscode/
.idea/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

---

## 🎓 Summary

**This structure is:**
- ✅ **Simple** - Only 4 folders (api, services, database, core)
- ✅ **Clear** - Easy to find anything
- ✅ **Standard** - Industry-recognized pattern
- ✅ **Scalable** - Can grow when needed
- ✅ **Quick to implement** - 30 minutes

**Perfect for:**
- ✅ Projects with 5-20 files
- ✅ Teams of 1-5 developers
- ✅ MVP to production transition
- ✅ Learning good practices without overwhelm

**Migration time:** 30-60 minutes (careful work)

**Bottom line:** Professional structure that doesn't slow you down! 🚀
