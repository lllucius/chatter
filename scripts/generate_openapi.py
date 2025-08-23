#!/usr/bin/env python3
"""
Script to generate and export OpenAPI documentation in various formats.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml
from fastapi.openapi.utils import get_openapi

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set required environment variables
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///test.db')
os.environ.setdefault('ENVIRONMENT', 'development')
os.environ.setdefault('OPENAI_API_KEY', 'fake-key-for-testing')

from chatter.config import settings  # noqa: E402
from chatter.main import app  # noqa: E402


def generate_openapi_spec() -> dict[str, Any]:
    """Generate OpenAPI specification from FastAPI app."""

    # Generate the OpenAPI spec with enhanced metadata
    openapi_spec = get_openapi(
        title=settings.api_title,
        version=settings.api_version,
        description=f"""
# {settings.api_description}

A comprehensive Python-based backend API platform for building advanced AI chatbots,
implemented with FastAPI, LangChain, LangGraph, Postgres, PGVector, and SQLAlchemy.

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
- **Multiple vector stores** (PGVector, Pinecone, Qdrant, ChromaDB)
- **Document processing** with unstructured data support
- **Semantic search** and retrieval-augmented generation (RAG)
- **Chunking strategies** for optimal retrieval
- **Embedding management** with multiple providers

### Data & Analytics
- **Comprehensive analytics** for conversations, usage, and performance
- **Cost tracking** and token usage monitoring
- **User behavior analytics** and system health metrics
- **Export capabilities** for reporting and analysis

## Authentication

All API endpoints (except health checks and documentation) require authentication.
Use the `/api/v1/auth/login` endpoint to obtain access tokens.

## Rate Limiting

API requests are rate-limited. Check response headers for current limits.

## SDK

A Python SDK is available for easy integration. See the SDK documentation for details.

## Support

- GitHub: https://github.com/lllucius/chatter
- Documentation: https://github.com/lllucius/chatter#readme
- Issues: https://github.com/lllucius/chatter/issues
        """.strip(),
        routes=app.routes,
    )

    # Add additional metadata manually
    openapi_spec["servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.chatter.ai", "description": "Production server"},
    ]

    openapi_spec["info"]["contact"] = {
        "name": "Chatter API Support",
        "url": "https://github.com/lllucius/chatter",
        "email": "support@chatter.ai",
    }

    openapi_spec["info"]["license"] = {"name": "MIT", "url": "https://github.com/lllucius/chatter/blob/main/LICENSE"}

    openapi_spec["externalDocs"] = {
        "description": "Chatter Documentation",
        "url": "https://github.com/lllucius/chatter#readme",
    }

    # Add custom extensions
    openapi_spec["x-logo"] = {"url": "https://github.com/lllucius/chatter/raw/main/docs/logo.png"}

    # Add API categories/tags descriptions
    openapi_spec["tags"] = [
        {"name": "Health", "description": "Health check and system status endpoints"},
        {"name": "Authentication", "description": "User authentication and authorization endpoints"},
        {"name": "Chat", "description": "Core chat and conversation endpoints with LLM integration"},
        {"name": "Documents", "description": "Document management and knowledge base endpoints"},
        {"name": "Profiles", "description": "LLM profile and prompt management endpoints"},
        {"name": "Analytics", "description": "Usage analytics and reporting endpoints"},
        {"name": "Tool Servers", "description": "MCP tool server management endpoints"},
    ]

    return openapi_spec


def export_openapi_json(spec: dict[str, Any], output_path: Path) -> None:
    """Export OpenAPI spec to JSON format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"✅ Exported OpenAPI JSON to: {output_path}")


def export_openapi_yaml(spec: dict[str, Any], output_path: Path) -> None:
    """Export OpenAPI spec to YAML format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"✅ Exported OpenAPI YAML to: {output_path}")


def main():
    """Main function to generate OpenAPI documentation."""
    print("🚀 Generating OpenAPI documentation...")

    # Create output directory
    output_dir = project_root / "docs" / "api"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate OpenAPI spec
    spec = generate_openapi_spec()

    # Export in different formats
    export_openapi_json(spec, output_dir / "openapi.json")
    export_openapi_yaml(spec, output_dir / "openapi.yaml")

    # Also create a versioned copy
    version = spec.get("info", {}).get("version", "unknown")
    export_openapi_json(spec, output_dir / f"openapi-v{version}.json")
    export_openapi_yaml(spec, output_dir / f"openapi-v{version}.yaml")

    print("📚 OpenAPI documentation generated successfully!")
    print(f"📁 Output directory: {output_dir}")
    print("🔗 Formats available: JSON, YAML")
    print(f"📊 Total endpoints: {len(list(spec.get('paths', {}).keys()))}")
    print(f"🏷️  Total schemas: {len(spec.get('components', {}).get('schemas', {}))}")


if __name__ == "__main__":
    main()
