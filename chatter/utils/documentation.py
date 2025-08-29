"""Enhanced API documentation and examples."""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from chatter.utils.versioning import version_manager


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
        description: str | None = None
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
            "response": response_example
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
                "deprecated_features": version.deprecated_features or [],
                "breaking_changes": version.breaking_changes or [],
                "new_features": version.new_features or []
            }
            for version in version_manager.get_all_versions()
        ]

        # Add correlation ID to all responses
        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if isinstance(operation, dict) and "responses" in operation:
                    for response in operation["responses"].values():
                        if "headers" not in response:
                            response["headers"] = {}
                        response["headers"]["x-correlation-id"] = {
                            "description": "Request correlation ID for tracing",
                            "schema": {"type": "string", "format": "uuid"}
                        }

                        # Add rate limiting headers
                        response["headers"].update({
                            "X-RateLimit-Limit-Minute": {
                                "description": "Requests allowed per minute",
                                "schema": {"type": "integer"}
                            },
                            "X-RateLimit-Limit-Hour": {
                                "description": "Requests allowed per hour",
                                "schema": {"type": "integer"}
                            },
                            "X-RateLimit-Remaining-Minute": {
                                "description": "Requests remaining this minute",
                                "schema": {"type": "integer"}
                            },
                            "X-RateLimit-Remaining-Hour": {
                                "description": "Requests remaining this hour",
                                "schema": {"type": "integer"}
                            }
                        })

        # Add examples to endpoints
        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue

                key = f"{method.upper()}:{path}"
                example_data = self.examples.get(key)

                if example_data:
                    # Add request example
                    if example_data["request"] and "requestBody" in operation:
                        content = operation["requestBody"].get("content", {})
                        for media_type in content.values():
                            media_type["example"] = example_data["request"]

                    # Add response example
                    if example_data["response"] and "responses" in operation:
                        for response in operation["responses"].values():
                            if "content" in response:
                                for media_type in response["content"].values():
                                    media_type["example"] = example_data["response"]

                # Add additional description
                description = self.descriptions.get(key)
                if description:
                    operation["description"] = operation.get("description", "") + f"\n\n{description}"

        return schema

    def generate_examples(self) -> None:
        """Generate common examples for standard endpoints."""

        # Authentication examples
        self.add_endpoint_example(
            "/api/v1/auth/login",
            "POST",
            request_example={
                "username": "user@example.com",
                "password": "secure_password"
            },
            response_example={
                "success": True,
                "data": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": {
                        "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                        "email": "user@example.com",
                        "username": "user",
                        "full_name": "John Doe"
                    }
                },
                "message": "Authentication successful",
                "metadata": {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "version": "0.1.0"
                }
            },
            description="Authenticate user and return access token with user information"
        )

        # Chat examples
        self.add_endpoint_example(
            "/api/v1/chat/conversations",
            "POST",
            request_example={
                "title": "Help with Python",
                "description": "Discussion about Python programming",
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.7,
                "system_prompt": "You are a helpful Python programming assistant."
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
                    "created_at": "2024-01-01T12:00:00Z"
                },
                "message": "Conversation created successfully",
                "metadata": {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "version": "0.1.0"
                }
            },
            description="Create a new conversation with specified configuration"
        )

        # Error response example
        self.add_endpoint_example(
            "/api/v1/chat/conversations/{conversation_id}/messages",
            "POST",
            request_example={
                "content": "What is Python?",
                "role": "user"
            },
            response_example={
                "success": False,
                "message": "Conversation not found",
                "errors": ["Conversation with ID '01ARZ3NDEKTSV4RRFFQ69G5FAV' does not exist"],
                "metadata": {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "version": "0.1.0"
                }
            },
            description="Example error response when conversation is not found"
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
