# Chatter - Advanced AI Chatbot Backend API Platform

A comprehensive Python-based backend API platform for building advanced AI chatbots, implemented with FastAPI, LangChain, LangGraph, Postgres, PGVector, and SQLAlchemy.

## Features

### Core API Features
- **RESTful API** with FastAPI and OpenAPI/Swagger documentation
- **Async-first architecture** with uvloop and hypercorn
- **Streaming responses** for real-time LLM output
- **Authentication** with JWT/OAuth2 and session management
- **Rate limiting** and security validations
- **Health checks** with `/healthz` and `/readyz` endpoints
- **API versioning** with modular router architecture

### LLM & AI Features
- **LangChain integration** for LLM orchestration and chain management
- **LangGraph workflows** for advanced conversation logic
- **Multiple LLM providers** with pluggable architecture (OpenAI, Anthropic, etc.)
- **Prompt management** with storage and versioning
- **Tool calling** with MCP (Model Context Protocol) integration
- **Multi-turn context** management and conversation history
- **Profile management** for LLM parameters (temperature, top_k, etc.)

### Vector Store & Knowledge Base
- **PGVector integration** with Postgres for scalable vector storage
- **Multiple vector store support** (Pinecone, Qdrant, ChromaDB)
- **Document ingestion** with unstructured document processing
- **Hybrid search** combining vector and keyword search
- **Metadata filtering** and document versioning
- **Background processing** for document indexing

### Data & Analytics
- **PostgreSQL database** with async SQLAlchemy ORM
- **Conversation statistics** (token counts, performance metrics)
- **Usage analytics** for documents, prompts, and profiles
- **Document management** with version tracking
- **Persistent storage** for all chat history and knowledge base

### Developer Experience
- **Comprehensive documentation** with examples and diagrams
- **Type annotations** throughout the codebase
- **Structured logging** with configurable debug levels
- **Error handling** with detailed error responses
- **Testing suite** with unit and integration tests
- **Development tools** (linting, formatting, type checking)

## Quick Start

### Prerequisites
- Python 3.12 or higher
- PostgreSQL 16+ with pgvector 0.6.2+ extension
- Redis (optional, for caching and rate limiting)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lllucius/chatter.git
cd chatter
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python -m alembic upgrade head
```

5. Start the development server:
```bash
python -m chatter serve --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Frontend Setup

To run the React frontend in development mode:

1. Generate the TypeScript SDK:
```bash
python scripts/generate_sdks.py --typescript
```

2. Install and run the frontend:
```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`.

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

### Key Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/chatter
VECTOR_STORE_TYPE=pgvector

# LLM Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Authentication
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
DEBUG_HTTP_REQUESTS=false
```

## API Documentation

### Core Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user info

#### Conversations
- `POST /api/v1/conversations` - Create new conversation
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/conversations/{conversation_id}` - Get conversation
- `POST /api/v1/conversations/{conversation_id}/chat` - Send message (non-streaming)
- `POST /api/v1/conversations/{conversation_id}/streaming` - Send message (streaming)
- `DELETE /api/v1/conversations/{conversation_id}` - Delete conversation

#### Documents & Knowledge Base
- `POST /api/v1/documents` - Upload documents
- `GET /api/v1/documents` - List documents
- `POST /api/v1/documents/list` - Advanced document listing
- `POST /api/v1/documents/search` - Search documents
- `GET /api/v1/documents/{document_id}` - Get document details
- `PUT /api/v1/documents/{document_id}` - Update document
- `DELETE /api/v1/documents/{document_id}` - Delete document
- `GET /api/v1/documents/{document_id}/chunks` - Get document chunks
- `POST /api/v1/documents/{document_id}/reprocess` - Reprocess document

#### Workflows
- `GET /api/v1/workflows/definitions` - List workflow definitions
- `POST /api/v1/workflows/definitions` - Create workflow definition  
- `GET /api/v1/workflows/definitions/{definition_id}` - Get workflow definition
- `PUT /api/v1/workflows/definitions/{definition_id}` - Update workflow definition
- `DELETE /api/v1/workflows/definitions/{definition_id}` - Delete workflow definition
- `POST /api/v1/workflows/definitions/{definition_id}/execute` - Execute workflow
- `GET /api/v1/workflows/definitions/{definition_id}/executions` - List executions

#### Profiles & Prompts
- `GET /api/v1/profiles` - List LLM profiles
- `POST /api/v1/profiles` - Create LLM profile
- `GET /api/v1/profiles/{profile_id}` - Get profile details
- `PUT /api/v1/profiles/{profile_id}` - Update profile
- `DELETE /api/v1/profiles/{profile_id}` - Delete profile

- `GET /api/v1/prompts` - List prompts
- `POST /api/v1/prompts` - Create prompt
- `GET /api/v1/prompts/{prompt_id}` - Get prompt details
- `PUT /api/v1/prompts/{prompt_id}` - Update prompt
- `DELETE /api/v1/prompts/{prompt_id}` - Delete prompt
- `POST /api/v1/prompts/{prompt_id}/test` - Test prompt with variables
- `POST /api/v1/prompts/{prompt_id}/clone` - Clone prompt

#### Advanced Features
- `GET /api/v1/agents` - List AI agents
- `POST /api/v1/agents` - Create AI agent
- `GET /api/v1/ab-tests` - A/B testing endpoints
- `GET /api/v1/events` - Event management
- `GET /api/v1/plugins` - Plugin management  
- `GET /api/v1/jobs` - Background job management
- `GET /api/v1/data` - Data management and export
- `GET /api/v1/models` - Model registry management
- `GET /api/v1/toolservers` - Tool server integration

#### Analytics & Monitoring
- `GET /api/v1/analytics/conversations` - Conversation analytics
- `GET /api/v1/analytics/usage` - Usage metrics
- `GET /api/v1/analytics/performance` - Performance metrics
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check

## SDK Generation

Chatter provides automatically generated SDKs for both Python and TypeScript to make it easy to integrate with the API.

### Regenerating SDKs

To regenerate both SDKs from the latest OpenAPI specification:

```bash
python scripts/generate_sdks.py
```

### Available Options

```bash
# Generate both SDKs (default)
python scripts/generate_sdks.py

# Generate Python SDK only
python scripts/generate_sdks.py --python

# Generate TypeScript SDK only  
python scripts/generate_sdks.py --typescript

# Verbose output
python scripts/generate_sdks.py --verbose
```

### SDK Locations

- **Python SDK**: `sdk/python/` (package: `chatter_sdk`)
- **TypeScript SDK**: `sdk/typescript/` (package: `chatter-sdk`)

For detailed information, see [SDK Generation Documentation](docs/sdk-generation.md).

## Architecture

### Project Structure
```
chatter/
├── chatter/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── api_cli.py           # Command-line interface
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── conversations.py # Conversation management
│   │   ├── new_documents.py # Document management
│   │   ├── workflows.py     # LangGraph workflow execution
│   │   ├── profiles.py      # LLM profile management
│   │   ├── prompts.py       # Prompt management
│   │   ├── analytics.py     # Analytics endpoints
│   │   ├── agents.py        # AI agent management
│   │   ├── ab_testing.py    # A/B testing framework
│   │   ├── events.py        # Event system
│   │   ├── plugins.py       # Plugin management
│   │   ├── jobs.py          # Background job management
│   │   ├── data_management.py # Data export/import
│   │   ├── model_registry.py # Model registry
│   │   ├── toolserver.py    # Tool server integration
│   │   └── health.py        # Health checks
│   ├── commands/            # CLI command modules
│   ├── core/                # Core business logic
│   ├── models/              # Database models (SQLAlchemy)
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # External service integrations
│   ├── utils/               # Shared utilities
│   └── middleware/          # Custom middleware
├── tests/                   # Comprehensive test suite
├── docs/                    # Documentation
│   ├── api/                 # OpenAPI specifications
│   ├── sdk-generation.md    # SDK generation guide
│   └── message_rating.md    # Feature documentation
├── sdk/                     # Generated SDKs
│   ├── python/              # Python SDK
│   └── typescript/          # TypeScript SDK
├── frontend/                # React frontend application
├── scripts/                 # Build and utility scripts
├── alembic/                 # Database migrations
├── .env.example             # Environment template
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

### Key Components

1. **FastAPI Application** (`main.py`): Core ASGI application with middleware and routing
2. **LangGraph Workflows** (`workflows.py`): Advanced conversation workflows and execution
3. **Document Management** (`new_documents.py`): Document processing and vector storage 
4. **Conversation System** (`conversations.py`): Chat management with streaming support
5. **AI Agents** (`agents.py`): Intelligent agent creation and management
6. **A/B Testing Framework** (`ab_testing.py`): Experimentation and optimization
7. **Analytics Engine** (`analytics.py`): Comprehensive usage and performance analytics
8. **Plugin System** (`plugins.py`): Extensible plugin architecture
9. **Model Registry** (`model_registry.py`): LLM and embedding model management
10. **Tool Integration** (`toolserver.py`): MCP tool server integration

## Development

### Setting up Development Environment

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

4. Code formatting and linting:
```bash
ruff check --fix
black .
mypy chatter
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chatter

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Database Migrations

```bash
# Create new migration
python -m alembic revision --autogenerate -m "Add new feature"

# Apply migrations
python -m alembic upgrade head

# Downgrade
python -m alembic downgrade -1
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper tests
4. Run the test suite (`pytest`)
5. Check code quality (`ruff check`, `black --check`, `mypy`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [GitHub README](https://github.com/lllucius/chatter#readme)
- Issues: [GitHub Issues](https://github.com/lllucius/chatter/issues)
- Discussions: [GitHub Discussions](https://github.com/lllucius/chatter/discussions)
