"""Enhanced API documentation and examples."""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from chatter.utils.logging import get_logger
from chatter.utils.versioning import version_manager

logger = get_logger(__name__)

# API Constants
API_V1_PREFIX = "/api/v1"
EXAMPLE_TIMESTAMP = "2025-01-09T00:00:00Z"

# Chat endpoint documentation template
CHAT_ENDPOINT_DOCS = """
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools
"""

# Common response headers for all endpoints
STANDARD_RESPONSE_HEADERS = {
    "x-correlation-id": {
        "description": "Request correlation ID for tracing",
        "schema": {"type": "string", "format": "uuid"},
    },
    "X-RateLimit-Limit-Minute": {
        "description": "Requests allowed per minute",
        "schema": {"type": "integer"},
    },
    "X-RateLimit-Limit-Hour": {
        "description": "Requests allowed per hour",
        "schema": {"type": "integer"},
    },
    "X-RateLimit-Remaining-Minute": {
        "description": "Requests remaining this minute",
        "schema": {"type": "integer"},
    },
    "X-RateLimit-Remaining-Hour": {
        "description": "Requests remaining this hour",
        "schema": {"type": "integer"},
    },
}


class APIDocumentationEnhancer:
    """Enhanced API documentation generator."""

    def __init__(self, app: FastAPI):
        """Initialize the documentation enhancer.

        Args:
            app: FastAPI application instance
        """
        self.app = app
        self.examples: dict[str, dict[str, Any]] = {}
        self.descriptions: dict[str, str] = {}

    def add_endpoint_example(
        self,
        path: str,
        method: str,
        request_example: dict[str, Any] | None = None,
        response_example: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> None:
        """Add examples for an endpoint.

        Args:
            path: Endpoint path
            method: HTTP method
            request_example: Example request body
            response_example: Example response body
            description: Additional description
        """
        key = f"{method.upper()}:{path}"
        self.examples[key] = {
            "request": request_example,
            "response": response_example,
        }

        if description:
            self.descriptions[key] = description

    def enhance_openapi_schema(self) -> dict[str, Any]:
        """Generate enhanced OpenAPI schema with examples.

        Returns:
            Enhanced OpenAPI schema
        """
        schema = get_openapi(
            title=self.app.title,
            version=self.app.version,
            description=self.app.description,
            routes=self.app.routes,
        )

        # Add version information
        schema["info"]["x-api-versions"] = [
            {
                "version": version.version.value,
                "status": version.status.value,
                "release_date": version.release_date,
                "documentation_url": version.documentation_url,
                "breaking_changes": version.breaking_changes or [],
                "new_features": version.new_features or [],
            }
            for version in version_manager.get_all_versions()
        ]

        # Add server configuration
        from chatter.config import settings

        schema["servers"] = [
            {
                "url": settings.api_base_url,
                "description": "Main server",
            }
        ]

        # Add standard headers to all responses
        self._add_standard_headers(schema)

        # Add examples to endpoints
        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue

                key = f"{method.upper()}:{path}"
                example_data = self.examples.get(key)

                if example_data:
                    # Add request example
                    if (
                        example_data["request"]
                        and "requestBody" in operation
                    ):
                        content = operation["requestBody"].get(
                            "content", {}
                        )
                        for media_type in content.values():
                            media_type["example"] = example_data[
                                "request"
                            ]

                    # Add response example
                    if (
                        example_data["response"]
                        and "responses" in operation
                    ):
                        for response in operation["responses"].values():
                            if "content" in response:
                                for media_type in response[
                                    "content"
                                ].values():
                                    media_type["example"] = (
                                        example_data["response"]
                                    )

                # Add additional description
                description = self.descriptions.get(key)
                if description:
                    operation["description"] = (
                        operation.get("description", "")
                        + f"\n\n{description}"
                    )

                # Add workflow-specific documentation
                if "/chat" in path and method.upper() == "POST":
                    self._enhance_chat_endpoint_docs(operation)

        return schema

    def _add_standard_headers(self, schema: dict[str, Any]) -> None:
        """Add standard response headers to all endpoints.

        Args:
            schema: OpenAPI schema to modify
        """
        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if (
                    isinstance(operation, dict)
                    and "responses" in operation
                ):
                    for response in operation["responses"].values():
                        if "headers" not in response:
                            response["headers"] = {}
                        response["headers"].update(
                            STANDARD_RESPONSE_HEADERS
                        )

    def _enhance_chat_endpoint_docs(self, operation: dict) -> None:
        """Enhance chat endpoint documentation with workflow examples."""
        current_desc = operation.get("description", "")
        operation["description"] = current_desc + CHAT_ENDPOINT_DOCS

    def generate_examples(self) -> None:
        """Generate common examples for standard endpoints."""
        self._add_auth_examples()
        self._add_chat_examples()
        self._add_document_examples()
        self._add_profile_examples()
        self._add_health_examples()
        self._add_conversation_examples()

        logger.debug(
            "Enhanced documentation examples loaded successfully"
        )

    def _add_auth_examples(self) -> None:
        """Add authentication endpoint examples."""
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/auth/login",
            "POST",
            request_example={
                "username": "user@example.com",
                "password": "secure_password",
            },
            response_example={
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            },
        )

        self.add_endpoint_example(
            f"{API_V1_PREFIX}/auth/register",
            "POST",
            request_example={
                "username": "developer123",
                "email": "developer@example.com",
                "password": "SecurePassword123!",
                "full_name": "John Developer",
            },
            response_example={
                "id": "usr_abc123",
                "username": "developer123",
                "email": "developer@example.com",
                "full_name": "John Developer",
                "is_active": True,
                "created_at": EXAMPLE_TIMESTAMP,
            },
        )

    def _add_chat_examples(self) -> None:
        """Add chat endpoint examples."""
        # Basic chat workflow
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/chat/chat",
            "POST",
            request_example={
                "message": "What are the latest customer satisfaction metrics?",
                "workflow": "rag",
                "enable_retrieval": True,
                "stream": False,
            },
            response_example={
                "conversation_id": "conv_123",
                "message_id": "msg_456",
                "content": "Based on the latest data from our customer feedback system...",
                "usage": {"tokens": 150, "response_time_ms": 1200},
            },
        )

        # Streaming chat example
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/chat/chat",
            "POST",
            request_example={
                "message": "Write a Python function to calculate fibonacci numbers",
                "workflow": "tools",
                "stream": True,
            },
            response_example={
                "event": "token",
                "data": {
                    "type": "token",
                    "content": "Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```",
                },
            },
        )

        # Template-based chat example
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/chat/template",
            "POST",
            request_example={
                "message": "I'm having trouble with my recent order",
                "workflow_template": "customer_support",
                "stream": False,
            },
            response_example={
                "conversation_id": "conv_789",
                "template_used": "customer_support",
                "content": "I understand you're having trouble with your order. Let me help you with that...",
                "tools_used": ["search_kb", "create_ticket"],
            },
        )

        # Workflow templates list example
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/chat/templates",
            "GET",
            request_example=None,
            response_example={
                "templates": {
                    "customer_support": {
                        "name": "customer_support",
                        "workflow_type": "full",
                        "description": "Customer support with knowledge base and tools",
                        "required_tools": [
                            "search_kb",
                            "create_ticket",
                            "escalate",
                        ],
                        "required_retrievers": ["support_docs"],
                    },
                    "code_assistant": {
                        "name": "code_assistant",
                        "workflow_type": "tools",
                        "description": "Programming assistant with code tools",
                        "required_tools": [
                            "execute_code",
                            "search_docs",
                            "generate_tests",
                        ],
                    },
                }
            },
        )

        # Conversation management
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/chat/conversations",
            "POST",
            request_example={
                "title": "Help with Python",
                "description": "Discussion about Python programming",
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.7,
                "system_prompt": "You are a helpful Python programming assistant.",
            },
            response_example={
                "success": True,
                "data": {
                    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                    "title": "Help with Python",
                    "description": "Discussion about Python programming",
                    "status": "active",
                    "llm_provider": "openai",
                    "llm_model": "gpt-4",
                    "temperature": 0.7,
                    "message_count": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "created_at": EXAMPLE_TIMESTAMP,
                },
                "message": "Conversation created successfully",
                "metadata": {
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "version": "0.1.0",
                },
            },
            description="Create a new conversation with specified configuration",
        )

        # Error response example
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/chat/conversations/{{conversation_id}}/messages",
            "POST",
            request_example={
                "content": "What is Python?",
                "role": "user",
            },
            response_example={
                "success": False,
                "message": "Conversation not found",
                "errors": [
                    "Conversation with ID '01ARZ3NDEKTSV4RRFFQ69G5FAV' does not exist"
                ],
                "metadata": {
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "version": "0.1.0",
                },
            },
            description="Example error response when conversation is not found",
        )

    def _add_document_examples(self) -> None:
        """Add document endpoint examples."""
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/documents",
            "POST",
            request_example={
                "title": "Project Documentation",
                "description": "Comprehensive guide for the AI platform",
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "is_public": False,
            },
            response_example={
                "id": "doc_xyz789",
                "title": "Project Documentation",
                "filename": "project-docs.pdf",
                "file_size": 2048576,
                "document_type": "pdf",
                "status": "processing",
                "chunk_count": 0,
                "created_at": EXAMPLE_TIMESTAMP,
            },
        )

    def _add_conversation_examples(self) -> None:
        """Add conversation endpoint examples."""
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/conversations",
            "GET",
            request_example=None,
            response_example={
                "conversations": [
                    {
                        "id": "conv_123",
                        "title": "API Development Help",
                        "message_count": 8,
                        "total_tokens": 1542,
                        "created_at": EXAMPLE_TIMESTAMP,
                        "updated_at": EXAMPLE_TIMESTAMP,
                    }
                ],
                "total_count": 15,
                "has_next": True,
                "has_previous": False,
            },
        )

    def _add_profile_examples(self) -> None:
        """Add profile endpoint examples."""
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/profiles",
            "POST",
            request_example={
                "name": "Code Assistant",
                "description": "Helpful assistant for programming tasks",
                "provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 2000,
                "system_prompt": "You are a helpful programming assistant. Provide clear, concise code examples and explanations.",
            },
            response_example={
                "id": "prof_abc456",
                "name": "Code Assistant",
                "provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 2000,
                "is_default": False,
                "created_at": EXAMPLE_TIMESTAMP,
            },
        )

    def _add_health_examples(self) -> None:
        """Add health endpoint examples."""
        self.add_endpoint_example(
            f"{API_V1_PREFIX}/health",
            "GET",
            request_example=None,
            response_example={
                "status": "healthy",
                "timestamp": EXAMPLE_TIMESTAMP,
                "version": "0.1.0",
                "services": {
                    "database": {
                        "status": "healthy",
                        "response_time_ms": 12,
                    },
                    "cache": {
                        "status": "healthy",
                        "response_time_ms": 3,
                    },
                    "llm_providers": {
                        "status": "healthy",
                        "response_time_ms": 89,
                    },
                },
                "system_info": {
                    "python_version": "3.12.0",
                    "total_conversations": 1247,
                    "total_users": 45,
                },
            },
        )


def setup_enhanced_docs(app: FastAPI) -> APIDocumentationEnhancer:
    """Setup enhanced documentation for the application.

    Args:
        app: FastAPI application

    Returns:
        Documentation enhancer instance
    """
    enhancer = APIDocumentationEnhancer(app)
    enhancer.generate_examples()

    # Override the default OpenAPI schema generator
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        app.openapi_schema = enhancer.enhance_openapi_schema()
        return app.openapi_schema

    app.openapi = custom_openapi
    return enhancer
