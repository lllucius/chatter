# Chatter Development Guide

This guide provides comprehensive information for developers working on or integrating with the Chatter API platform.

## Quick Development Setup

### Prerequisites
- Python 3.12+ 
- PostgreSQL 16+ with pgvector 0.6.2+ extension
- Node.js 18+ (for frontend and SDK generation)
- Redis (optional, for caching)

### Installation
```bash
# Clone and setup
git clone https://github.com/lllucius/chatter.git
cd chatter

# Install with dev dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -m alembic upgrade head

# Start development server
python -m uvicorn chatter.main:app --reload
```

## Project Architecture

### Core Components

**FastAPI Application** (`chatter/main.py`)
- ASGI application with async middleware
- Comprehensive error handling and logging
- Health checks and metrics endpoints

**API Routes** (`chatter/api/`)
- Modular router architecture
- RESTful endpoints with OpenAPI documentation
- Authentication and authorization layers

**Core Logic** (`chatter/core/`)
- Business logic and service orchestration
- Database operations and caching
- Integration with external services

**Database Layer** (`chatter/models/`)
- SQLAlchemy ORM models
- Migration management with Alembic
- PostgreSQL with pgvector for embeddings

### API Endpoints Overview

#### Core APIs
- **Authentication**: User management, JWT tokens, API keys
- **Conversations**: Chat management with streaming support
- **Documents**: Upload, processing, vector search with pgvector
- **Workflows**: LangGraph-based AI workflow execution
- **Profiles**: LLM configuration and parameter management
- **Prompts**: Template management and testing

#### Advanced APIs
- **Agents**: AI agent creation and execution
- **Analytics**: Usage metrics and performance monitoring  
- **A/B Testing**: Experiment management and analysis
- **Events**: Event system and notifications
- **Plugins**: Extension management
- **Jobs**: Background task processing
- **Data Management**: Export, backup, bulk operations
- **Model Registry**: LLM and embedding model configuration
- **Tool Servers**: MCP tool integration

## Development Workflow

### Code Quality
```bash
# Linting and formatting
ruff check --fix
black .
isort .

# Type checking
mypy chatter

# Security analysis
bandit -r chatter

# Run all checks
python scripts/lint_backend.py
```

### Testing
```bash
# Run all tests
pytest

# Run by category
pytest -m unit        # Unit tests
pytest -m integration # Integration tests
pytest -m "not slow"  # Exclude slow tests

# With coverage
pytest --cov=chatter --cov-report=html
```

### Database Operations
```bash
# Create migration
python -m alembic revision --autogenerate -m "Description"

# Apply migrations
python -m alembic upgrade head

# Rollback
python -m alembic downgrade -1

# Seed test data
python scripts/seed_database.py
```

### SDK Generation
```bash
# Generate both Python and TypeScript SDKs
python scripts/generate_sdks.py

# Generate specific SDK
python scripts/generate_sdks.py --python
python scripts/generate_sdks.py --typescript

# With verbose output
python scripts/generate_sdks.py --verbose
```

## API Development

### Adding New Endpoints

1. **Create API Route** (`chatter/api/your_module.py`):
```python
from fastapi import APIRouter, Depends
from chatter.api.dependencies import get_current_user
from chatter.schemas.your_schemas import YourRequest, YourResponse

router = APIRouter()

@router.post("/endpoint", response_model=YourResponse)
async def your_endpoint(
    request: YourRequest,
    current_user=Depends(get_current_user)
):
    # Implementation
    pass
```

2. **Add to Main App** (`chatter/main.py`):
```python
from chatter.api import your_module

app.include_router(
    your_module.router,
    prefix=f"{settings.api_prefix}/your-path",
    tags=["Your Module"],
)
```

3. **Create Schemas** (`chatter/schemas/your_schemas.py`):
```python
from pydantic import BaseModel
from typing import Optional

class YourRequest(BaseModel):
    field: str
    
class YourResponse(BaseModel):
    id: str
    result: str
```

4. **Add Database Model** (`chatter/models/your_model.py`):
```python
from sqlalchemy import Column, String
from chatter.models.base import BaseModel

class YourModel(BaseModel):
    __tablename__ = "your_table"
    
    name = Column(String, nullable=False)
```

### Authentication & Authorization

```python
# Require authentication
from chatter.api.dependencies import get_current_user

async def protected_endpoint(current_user=Depends(get_current_user)):
    pass

# Require admin role
from chatter.api.dependencies import require_admin

async def admin_endpoint(current_user=Depends(require_admin)):
    pass

# Optional authentication
from chatter.api.dependencies import get_current_user_optional

async def optional_auth_endpoint(current_user=Depends(get_current_user_optional)):
    pass
```

### Error Handling

```python
from chatter.utils.problem import BadRequestProblem, NotFoundProblem

# Raise standardized errors
if not item:
    raise NotFoundProblem("Item not found")
    
if invalid_data:
    raise BadRequestProblem("Invalid input data")
```

## Testing Guidelines

### Test Structure
```
tests/
├── test_module_unit.py         # Fast, isolated tests
├── test_module_integration.py  # Database + API tests
├── conftest.py                 # Shared fixtures
└── API_TESTS_README.md         # Testing documentation
```

### Writing Tests
```python
import pytest
from httpx import AsyncClient

class TestYourAPI:
    @pytest.mark.unit
    async def test_endpoint_validation(self, client: AsyncClient):
        response = await client.post("/api/v1/endpoint", json={})
        assert response.status_code == 422
    
    @pytest.mark.integration  
    async def test_full_workflow(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/endpoint", 
            json={"field": "value"},
            headers=auth_headers
        )
        assert response.status_code == 201
```

## Configuration Management

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/chatter
REDIS_URL=redis://localhost:6379

# LLM Providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Authentication
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Features
ENABLE_TOOLS=true
ENABLE_RETRIEVAL=true
CACHE_DISABLE_ALL=false

# Development
DEBUG=true
LOG_LEVEL=DEBUG
DEBUG_HTTP_REQUESTS=true
```

### Settings Usage
```python
from chatter.config import settings

# Access configuration
if settings.debug:
    print("Debug mode enabled")

# Database URL
engine = create_async_engine(settings.database_url)
```

## Monitoring & Observability

### Health Checks
- `GET /healthz` - Basic health status
- `GET /readyz` - Readiness for traffic
- `GET /api/v1/health/detailed` - Comprehensive health info

### Logging
```python
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

logger.info("Operation completed", user_id=user.id, duration=elapsed)
logger.error("Operation failed", error=str(e), context={"key": "value"})
```

### Analytics Integration
```python
from chatter.core.analytics import track_event

# Track custom events
await track_event(
    event_type="document_processed",
    user_id=user.id,
    metadata={"document_id": doc_id, "duration": elapsed}
)
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=false` 
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up PostgreSQL with pgvector
- [ ] Configure Redis for caching
- [ ] Set up reverse proxy (nginx)
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and logging
- [ ] Run database migrations
- [ ] Configure backup strategy

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "-m", "uvicorn", "chatter.main:app", "--host", "0.0.0.0"]
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure project is installed in development mode
pip install -e .

# Check Python path
python -c "import chatter; print(chatter.__file__)"
```

**Database Connection**
```bash
# Test database connection
python -c "from chatter.utils.database import test_connection; test_connection()"

# Check migrations
python -m alembic current
python -m alembic upgrade head
```

**SDK Generation Fails**
```bash
# Install Node.js dependencies
npm install -g @openapitools/openapi-generator-cli

# Check OpenAPI spec
python scripts/generate_openapi.py
```

### Debug Mode
```python
# Enable detailed HTTP request logging
export DEBUG_HTTP_REQUESTS=true

# Enable SQL query logging
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes with proper tests
4. Run quality checks: `python scripts/lint_backend.py`
5. Run test suite: `pytest`
6. Commit changes: `git commit -m 'Add feature'`
7. Push branch: `git push origin feature/your-feature`
8. Open Pull Request

## Resources

- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Python SDK Documentation](sdk/python/README.md)
- [TypeScript SDK Documentation](sdk/typescript/README.md)
- [Message Rating Feature](message_rating.md)
- [SDK Generation Guide](sdk-generation.md)
- [Test Suite Documentation](../tests/API_TESTS_README.md)