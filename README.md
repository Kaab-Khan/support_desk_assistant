# AI Support Desk Assistant

An enterprise-grade FastAPI application that automates support ticket triage using RAG (Retrieval-Augmented Generation), LLM-powered decision making, and vector similarity search.

## Features

- 🤖 **Automated Ticket Processing** - AI-powered triage with intelligent action recommendations
- 📚 **RAG-Based Knowledge Base** - Vector similarity search using Pinecone
- 🏷️ **Smart Tag Extraction** - Automatic categorization integrated into RAG workflow
- 💬 **Intelligent Actions** - Reply, escalate, or close tickets based on context
- 🔄 **Human Feedback Loop** - Continuous improvement through feedback integration
- ✅ **Production Ready** - Comprehensive test suite with 78 tests (77 passed)
- 🏗️ **Clean Architecture** - Layered design with dependency injection

## Technology Stack

- **Backend**: FastAPI 0.115.5
- **Language**: Python 3.10.12 (see `runtime.txt`)
- **Database**: SQLite with SQLAlchemy 2.0.23
- **Vector Store**: Pinecone (Serverless AWS us-east-1)
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-ada-002 (1536 dimensions)
- **Server**: Uvicorn ASGI
- **Testing**: pytest (78 tests)

## Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Pinecone API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd support_desk_assistant-1
   ```

2. **Create virtual environment**
   ```bash
   make ensure-venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   make requirements
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   Required variables:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `PINECONE_API_KEY` - Your Pinecone API key
   - `PINECONE_INDEX_NAME` - Pinecone index name (default: support-desk-assistant-docs)

5. **Ingest documentation** (optional, if you have docs to index)
   ```bash
   make run-ingest
   ```

6. **Run the API server**
   ```bash
   make run-api
   ```

   The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /health
```

### RAG Query
```bash
POST /api/v1/rag/query
Content-Type: application/json

{
  "query": "How do I reset my password?"
}
```

**Response:**
```json
{
  "answer": "To reset your password...",
  "sources": [
    {
      "doc_name": "user_guide.txt",
      "snippet": "Password reset instructions..."
    }
  ]
}
```

### Process Ticket
```bash
POST /api/v1/tickets/agent
Content-Type: application/json

{
  "ticket": "I can't log into my account"
}
```

**Response:**
```json
{
  "id": 1,
  "action": "reply",
  "reply": "Here's how to reset your password...",
  "reason": "User needs password reset assistance",
  "tags": ["authentication", "password-reset"]
}
```

### Submit Feedback
```bash
POST /api/v1/tickets/feedback
Content-Type: application/json

{
  "ticket_id": 1,
  "human_label": "correct"
}
```

### List Tickets
```bash
GET /api/v1/tickets
```

## Project Structure

```
support_desk_assistant-1/
├── app/
│   ├── api/              # API layer
│   │   └── v1/          # Version 1 endpoints
│   ├── config/          # Configuration management
│   ├── core/            # Business logic
│   │   ├── services/    # RAG service
│   │   └── workflows/   # Ticket workflow
│   ├── infrastructure/  # External integrations
│   │   ├── clients/     # OpenAI client
│   │   ├── db/          # Database models
│   │   ├── repositories/ # Data access layer
│   │   └── vectorstores/ # Pinecone client
│   └── schemas/         # Request/response models
├── data/
│   ├── docs/            # Documentation files for ingestion
│   └── vectorstore/     # Local vector store cache
├── scripts/
│   ├── ingest_docs.py   # Documentation ingestion script
│   └── convert_docx_to_txt.py
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── .env.example         # Environment template
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── Makefile            # Build and run commands
└── README.md
```

## Development

### Install Development Dependencies

```bash
make requirements-dev
```

### Run Tests

```bash
pytest
```

**Test Coverage:**
- 78 total tests
- 77 passed, 1 skipped
- Unit tests for all services and components
- Integration tests for API endpoints and external services

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Clean Python caches
make clean
```

## Architecture

The project follows Clean Architecture principles with clear separation of concerns:

**API Layer** (`app/api/`)
- HTTP request/response handling
- Input validation with Pydantic schemas
- Dependency injection

**Core Layer** (`app/core/`)
- Business logic and workflows
- Service orchestration (RAG service)
- Workflow coordination (Ticket workflow)

**Infrastructure Layer** (`app/infrastructure/`)
- Database connections and models
- External API clients (OpenAI, Pinecone)
- Repository pattern for data access

**Configuration** (`app/config/`)
- Environment settings management
- API keys and secrets handling

## Database Schema

The application uses SQLite with the following schema:

**tickets**
- `id` - Primary key
- `text` - Original ticket text
- `predicted_action` - AI recommendation (reply/escalate/close)
- `suggested_reply` - Generated response (if applicable)
- `predicted_reason` - Reasoning for the action
- `predicted_tags` - Extracted tags (JSON)
- `human_label` - Human feedback (correct/incorrect/null)
- `created_at` - Timestamp

## Environment Variables

See `.env.example` for all configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_INDEX_NAME` | Pinecone index name | support-desk-assistant-docs |
| `DB_URL` | Database connection URL | sqlite:///data/support.db |
| `DOCS_DIR` | Documentation directory | data/docs |
| `VECTORSTORE_DIR` | Vector store directory | data/vectorstore |

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment

### Docker Deployment

The application includes a production-ready `Dockerfile` that uses Python 3.10.12 and Gunicorn with Uvicorn workers.

#### Build and Run Locally

```bash
# Build the Docker image
docker build -t support-desk-assistant .

# Run the container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  -e PINECONE_INDEX_NAME=support-desk-assistant-docs \
  support-desk-assistant
```

### Deploying to Render

Render provides a straightforward platform for deploying FastAPI applications with automatic HTTPS, environment variables, and PostgreSQL support. You can deploy using either Docker or native Python.

#### Prerequisites

1. Create a [Render account](https://render.com/)
2. Push your code to GitHub
3. Obtain OpenAI and Pinecone API keys

#### Step 1: Create a PostgreSQL Database (Recommended)

1. Go to your Render dashboard
2. Click **New +** → **PostgreSQL**
3. Configure your database:
   - **Name**: `support-desk-db`
   - **Database**: `support_desk`
   - **User**: `support_desk_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free or paid tier
4. Click **Create Database**
5. Copy the **Internal Database URL** (starts with `postgresql://`)

#### Step 2: Create a Web Service

1. Go to your Render dashboard
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure your service:

**Deployment Method:**

Choose one of the following:

**Option A: Docker (Recommended)**
- **Environment**: `Docker`
- **Dockerfile Path**: `Dockerfile` (default)
- Render will automatically detect and use the Dockerfile

**Option B: Native Python**
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`

**Basic Settings:**
- **Name**: `ai-support-desk-assistant`
- **Region**: Same as your database
- **Branch**: `main`

**Environment Variables:**

Click **Advanced** → **Add Environment Variable** and add:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `your_openai_api_key_here` |
| `PINECONE_API_KEY` | `your_pinecone_api_key_here` |
| `PINECONE_INDEX_NAME` | `support-desk-assistant-docs` |
| `DB_URL` | `postgresql://user:password@host:5432/database` (from Step 1) |
| `DOCS_DIR` | `data/docs` |
| `VECTORSTORE_DIR` | `data/vectorstore` |

**Instance Type:**
- **Free** - For testing (spins down after inactivity)
- **Starter ($7/month)** - For production use

5. Click **Create Web Service**

#### Step 3: Monitor Deployment

Render will automatically:
- Install dependencies from `requirements.txt`
- Run database migrations (SQLAlchemy auto-creates tables)
- Start your FastAPI application
- Provide HTTPS endpoint: `https://your-app-name.onrender.com`

Watch the deploy logs for any errors.

#### Step 4: Verify Deployment

Test your endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# View API docs
https://your-app-name.onrender.com/docs
```

#### Step 5: Ingest Documentation (Optional)

If you need to populate Pinecone with documentation:

**Option A: One-time Job**
1. Go to your service in Render
2. Click **Shell** tab
3. Run: `python scripts/ingest_docs.py`

**Option B: Background Worker**
1. Create a new **Background Worker** service
2. Use same repository and environment variables
3. **Start Command**: `python scripts/ingest_docs.py`

#### Additional Configuration

**Docker-Specific Notes:**
- The Dockerfile uses Python 3.10.12 (as specified in `runtime.txt`)
- Gunicorn with Uvicorn workers for better production performance
- Health checks included for automatic monitoring
- The `$PORT` environment variable is automatically set by Render

**Custom Domain:**
1. Go to service **Settings**
2. Click **Custom Domain**
3. Add your domain and configure DNS

**Auto-Deploy:**
- Enabled by default - deploys on every push to main branch
- Disable in **Settings** → **Auto-Deploy** if needed

**Scaling:**
- Upgrade instance type for better performance
- Horizontal scaling available on paid plans

**Health Checks:**
- Default: HTTP GET to `/`
- Customize in **Settings** → **Health Check Path**: `/health`

**Logs & Monitoring:**
- View real-time logs in dashboard
- Configure log drains for external monitoring (Datadog, etc.)

#### Important Notes

**Free Tier Limitations:**
- Services spin down after 15 minutes of inactivity
- Cold start takes 30-60 seconds on first request
- 750 hours/month free tier (shared across all services)
- Use Starter plan or higher for production

**Database Connection:**
- Use **Internal Database URL** (faster, free)
- Format: `postgresql://user:password@internal-host:5432/dbname`
- SQLAlchemy auto-creates tables on startup

**Environment Variables:**
- Never commit `.env` to repository
- Update variables in Render dashboard without redeploying
- Changes to build command require new deploy

**CORS Configuration:**
- Currently set to allow all origins (`allow_origins=["*"]`)
- For production, update `app/main.py` to restrict origins:
  ```python
  allow_origins=[
      "https://yourdomain.com",
      "https://app.yourdomain.com"
  ]
  ```

#### Troubleshooting Render Deployment

**Build Failures:**
```bash
# Verify requirements.txt is in root directory
# Check Python version compatibility (3.10+)
# Ensure all dependencies are listed
```

**Service Won't Start:**
- Check logs: Service → **Logs** tab
- Verify start command includes `--port $PORT`
- Ensure environment variables are set correctly

**Database Connection Errors:**
```bash
# Use Internal Database URL (not External)
# Format: postgresql://user:password@host:5432/dbname
# Verify database is in same region as web service
```

**Slow Cold Starts (Free Tier):**
- Upgrade to Starter plan ($7/month) for always-on service
- Or use cron-job.org to ping `/health` every 10 minutes

**Pinecone Connection Issues:**
- Verify PINECONE_API_KEY is correct
- Check PINECONE_INDEX_NAME matches your index
- Ensure index exists in Pinecone dashboard

### Alternative Deployment Options

**Using Docker:**
- **AWS ECS/Fargate**: Use the Dockerfile for containerized deployment
- **Google Cloud Run**: Deploy directly from Dockerfile
- **Azure Container Instances**: Build and deploy with Docker
- **DigitalOcean App Platform**: Supports Docker deployments

**Native Python:**
- **Railway**: Similar to Render with PostgreSQL support
- **Fly.io**: Edge deployment for low latency
- **Heroku**: Use Procfile with Gunicorn
- **Self-hosted**: Use nginx + Gunicorn + systemd

## Troubleshooting

**Database locked error:**
```bash
python close_db.py
```

**Pinecone connection issues:**
- Verify API key is correct
- Check index name matches configuration
- Ensure index exists in Pinecone dashboard

**OpenAI API errors:**
- Verify API key has sufficient credits
- Check rate limits
- Review API error messages in logs

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please open an issue on GitHub.
