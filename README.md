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
- Python 3.11 or higher
- PostgreSQL 15+ with pgvector extension
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
chatter db init
chatter db migrate
```

5. Start the development server:
```bash
chatter serve --reload
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
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

#### Conversations
- `POST /chat` - Start new conversation
- `POST /chat/{conversation_id}/message` - Send message
- `GET /chat/{conversation_id}/messages` - Get message history
- `GET /chat/{conversation_id}/stream` - Streaming chat endpoint
- `DELETE /chat/{conversation_id}` - Delete conversation

#### Documents & Knowledge Base
- `POST /documents/upload` - Upload documents
- `GET /documents` - List documents
- `GET /documents/{document_id}` - Get document details
- `DELETE /documents/{document_id}` - Delete document
- `POST /documents/search` - Search knowledge base

#### Profiles & Prompts
- `GET /profiles` - List LLM profiles
- `POST /profiles` - Create LLM profile
- `PUT /profiles/{profile_id}` - Update profile
- `GET /prompts` - List prompts
- `POST /prompts` - Create prompt
- `GET /prompts/{prompt_id}` - Get prompt details
- `PUT /prompts/{prompt_id}` - Update prompt
- `DELETE /prompts/{prompt_id}` - Delete prompt
- `POST /prompts/{prompt_id}/test` - Test prompt with variables
- `POST /prompts/{prompt_id}/clone` - Clone prompt
- `GET /prompts/stats/overview` - Get prompt statistics

#### Analytics
- `GET /analytics/conversations` - Conversation statistics
- `GET /analytics/usage` - Usage metrics
- `GET /analytics/performance` - Performance metrics

#### Health & Monitoring
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check
- `GET /metrics` - Prometheus metrics

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
- **TypeScript SDK**: `frontend/src/sdk/` (package: `chatter-sdk`)

For detailed information, see [SDK Generation Documentation](docs/sdk-generation.md).

## Architecture

### Project Structure
```
chatter/
├── chatter/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── cli.py               # Command-line interface
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── chat.py          # Chat endpoints
│   │   ├── documents.py     # Document management
│   │   ├── analytics.py     # Analytics endpoints
│   │   └── health.py        # Health checks
│   ├── core/                # Core business logic
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication logic
│   │   ├── chat.py          # Chat logic
│   │   ├── langchain.py     # LangChain integration
│   │   ├── langgraph.py     # LangGraph workflows
│   │   └── vector_store.py  # Vector store operations
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py          # User models
│   │   ├── conversation.py  # Conversation models
│   │   ├── document.py      # Document models
│   │   └── analytics.py     # Analytics models
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth schemas
│   │   ├── chat.py          # Chat schemas
│   │   ├── document.py      # Document schemas
│   │   └── analytics.py     # Analytics schemas
│   ├── services/            # External services
│   │   ├── __init__.py
│   │   ├── llm.py           # LLM providers
│   │   ├── embeddings.py    # Embedding providers
│   │   ├── vector_store.py  # Vector store services
│   │   └── mcp.py           # MCP tool integration
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── logging.py       # Structured logging
│       ├── security.py      # Security utilities
│       └── database.py      # Database utilities
├── tests/                   # Test suite
├── docs/                    # Documentation
├── alembic/                 # Database migrations
├── .env.example             # Environment template
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

### Key Components

1. **FastAPI Application** (`main.py`): Core ASGI application with middleware and routing
2. **LangChain Integration** (`core/langchain.py`): LLM orchestration and chain management
3. **LangGraph Workflows** (`core/langgraph.py`): Advanced conversation workflows
4. **Vector Store** (`core/vector_store.py`): Abstracted vector operations
5. **Database Models** (`models/`): SQLAlchemy models for all entities
6. **API Routes** (`api/`): RESTful endpoints with proper error handling
7. **Services** (`services/`): External service integrations

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
chatter db revision --autogenerate -m "Add new feature"

# Apply migrations
chatter db upgrade

# Downgrade
chatter db downgrade -1
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