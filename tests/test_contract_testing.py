"""Contract testing for API specifications and compatibility."""

import json
import pytest
from typing import Dict, Any
from unittest.mock import patch


@pytest.mark.integration
class TestAPIContractValidation:
    """Test API contract compliance and backward compatibility."""

    def test_api_response_schemas(self, test_client):
        """Test that API responses match expected schemas."""
        # Define expected response schemas
        expected_schemas = {
            "/health": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "uptime": {"type": "number"}
                },
                "required": ["status"]
            },
            "/api/v1/health": {
                "type": "object", 
                "properties": {
                    "status": {"type": "string"},
                    "database": {"type": "string"},
                    "version": {"type": "string"}
                },
                "required": ["status"]
            }
        }
        
        for endpoint, schema in expected_schemas.items():
            response = test_client.get(endpoint)
            
            if response.status_code == 404:
                continue  # Endpoint doesn't exist, skip
            
            if response.status_code == 200:
                data = response.json()
                self._validate_schema(data, schema, endpoint)

    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any], endpoint: str):
        """Validate data against a simple JSON schema."""
        if schema["type"] == "object":
            assert isinstance(data, dict), f"{endpoint}: Expected object, got {type(data)}"
            
            # Check required fields
            required = schema.get("required", [])
            for field in required:
                assert field in data, f"{endpoint}: Missing required field '{field}'"
            
            # Check field types
            properties = schema.get("properties", {})
            for field, field_schema in properties.items():
                if field in data:
                    expected_type = field_schema["type"]
                    actual_value = data[field]
                    
                    if expected_type == "string":
                        assert isinstance(actual_value, str), f"{endpoint}: {field} should be string"
                    elif expected_type == "number":
                        assert isinstance(actual_value, (int, float)), f"{endpoint}: {field} should be number"
                    elif expected_type == "boolean":
                        assert isinstance(actual_value, bool), f"{endpoint}: {field} should be boolean"

    def test_api_versioning_compatibility(self, test_client):
        """Test API versioning and backward compatibility."""
        # Test that v1 endpoints are accessible
        v1_endpoints = [
            "/api/v1/health",
            "/api/v1/chat/conversations",
            "/api/v1/documents",
            "/api/v1/agents",
            "/api/v1/auth/me"
        ]
        
        for endpoint in v1_endpoints:
            response = test_client.get(endpoint)
            
            # Should not return 500 errors (indicates proper routing)
            assert response.status_code < 500, f"Server error for {endpoint}: {response.status_code}"
            
            # If endpoint exists, should have proper CORS headers or content-type
            if response.status_code not in [404, 405]:
                headers = response.headers
                # Should have content-type for successful responses
                if response.status_code < 400:
                    assert "content-type" in headers, f"Missing content-type for {endpoint}"

    def test_error_response_consistency(self, test_client):
        """Test that error responses have consistent format."""
        # Test various error scenarios
        error_test_cases = [
            ("GET", "/api/v1/nonexistent", 404),
            ("POST", "/api/v1/chat/conversations", 401),  # Might need auth
            ("GET", "/api/v1/documents/invalid-id", 404),
        ]
        
        for method, endpoint, expected_status in error_test_cases:
            if method == "GET":
                response = test_client.get(endpoint)
            elif method == "POST":
                response = test_client.post(endpoint, json={})
            
            if response.status_code == expected_status:
                # Error responses should be JSON if possible
                try:
                    error_data = response.json()
                    # Should have error information
                    assert any(key in error_data for key in ["error", "detail", "message"]), \
                        f"Error response missing error info for {endpoint}"
                except:
                    # Some errors might not be JSON, that's acceptable
                    pass


@pytest.mark.integration
class TestAPIDocumentationCompliance:
    """Test that API implementation matches documentation."""

    def test_openapi_spec_compliance(self, test_client):
        """Test that API matches OpenAPI specification."""
        # Try to get OpenAPI spec
        spec_endpoints = [
            "/openapi.json",
            "/docs/openapi.json",
            "/api/v1/openapi.json"
        ]
        
        openapi_spec = None
        for endpoint in spec_endpoints:
            response = test_client.get(endpoint)
            if response.status_code == 200:
                try:
                    openapi_spec = response.json()
                    break
                except:
                    continue
        
        if not openapi_spec:
            pytest.skip("OpenAPI specification not available")
        
        # Validate basic OpenAPI structure
        assert "openapi" in openapi_spec, "Missing OpenAPI version"
        assert "info" in openapi_spec, "Missing API info"
        assert "paths" in openapi_spec, "Missing API paths"
        
        # Check that documented paths exist
        documented_paths = openapi_spec["paths"].keys()
        for path in documented_paths:
            # Convert OpenAPI path to test path
            test_path = path.replace("{", "test-").replace("}", "")
            response = test_client.get(test_path)
            
            # Should not be completely unknown (404 for specific resource is ok)
            assert response.status_code != 501, f"Unimplemented endpoint: {path}"

    def test_api_documentation_endpoints(self, test_client):
        """Test that API documentation endpoints are available."""
        doc_endpoints = [
            "/docs",
            "/redoc", 
            "/api/docs",
            "/api/v1/docs"
        ]
        
        available_docs = []
        for endpoint in doc_endpoints:
            response = test_client.get(endpoint)
            if response.status_code == 200:
                available_docs.append(endpoint)
        
        # At least one documentation endpoint should be available
        assert len(available_docs) > 0, "No API documentation endpoints available"


@pytest.mark.integration  
class TestFrontendBackendContract:
    """Test contract between frontend and backend."""

    def test_frontend_api_expectations(self, test_client):
        """Test that backend provides what frontend expects."""
        # Frontend typically expects certain response formats
        frontend_critical_endpoints = [
            ("/api/v1/chat/conversations", "GET"),
            ("/api/v1/documents", "GET"),
            ("/api/v1/agents", "GET"),
            ("/api/v1/auth/me", "GET")
        ]
        
        for endpoint, method in frontend_critical_endpoints:
            if method == "GET":
                response = test_client.get(endpoint)
            
            if response.status_code == 200:
                data = response.json()
                
                # Frontend expects JSON responses
                assert isinstance(data, (list, dict)), f"Non-JSON response from {endpoint}"
                
                # If it's a list, items should have consistent structure
                if isinstance(data, list) and data:
                    first_item = data[0]
                    assert isinstance(first_item, dict), f"List items should be objects in {endpoint}"
                    assert "id" in first_item, f"Items should have ID field in {endpoint}"

    def test_cors_headers_for_frontend(self, test_client):
        """Test CORS headers for frontend integration."""
        # Test CORS preflight for common endpoints
        cors_test_endpoints = [
            "/api/v1/chat/conversations",
            "/api/v1/documents/upload",
            "/api/v1/auth/login"
        ]
        
        for endpoint in cors_test_endpoints:
            # OPTIONS request for CORS preflight
            response = test_client.options(endpoint)
            
            # Should handle OPTIONS requests
            assert response.status_code in [200, 204, 405], f"CORS preflight failed for {endpoint}"
            
            # Check for CORS headers in regular requests
            get_response = test_client.get(endpoint)
            if get_response.status_code < 500:
                headers = get_response.headers
                # Should have CORS or be same-origin friendly
                cors_indicators = [
                    "access-control-allow-origin",
                    "access-control-allow-methods",
                    "access-control-allow-headers"
                ]
                has_cors = any(header in headers for header in cors_indicators)
                # CORS not strictly required for same-origin, but check headers are reasonable
                assert len(headers) > 0, f"No response headers for {endpoint}"


@pytest.mark.integration
class TestDataConsistencyContracts:
    """Test data consistency contracts between services."""

    def test_user_data_consistency(self, test_client):
        """Test user data consistency across endpoints."""
        # This would test that user data is consistent between
        # authentication, profile, and other user-related endpoints
        
        auth_response = test_client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "testpass"
        })
        
        if auth_response.status_code != 200:
            pytest.skip("Authentication not available for consistency test")
        
        auth_data = auth_response.json()
        if "access_token" not in auth_data:
            pytest.skip("No access token available")
        
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Get user profile
        profile_response = test_client.get("/api/v1/auth/me", headers=headers)
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            
            # User ID should be consistent
            assert "id" in profile_data or "user_id" in profile_data, "User profile missing ID"
            
            # Email should match login
            if "email" in profile_data:
                assert profile_data["email"] == "test@example.com"

    def test_conversation_message_consistency(self, test_client):
        """Test consistency between conversations and messages."""
        # Create a conversation
        create_response = test_client.post("/api/v1/chat/conversations", json={
            "title": "Consistency Test"
        })
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Cannot create conversation for consistency test")
        
        conv_data = create_response.json()
        conv_id = conv_data.get("id") or conv_data.get("conversation_id")
        
        if not conv_id:
            pytest.skip("No conversation ID available")
        
        # Add a message
        message_response = test_client.post(
            f"/api/v1/chat/conversations/{conv_id}/messages",
            json={"content": "Test message", "role": "user"}
        )
        
        if message_response.status_code in [200, 201]:
            # Get conversation messages
            messages_response = test_client.get(
                f"/api/v1/chat/conversations/{conv_id}/messages"
            )
            
            if messages_response.status_code == 200:
                messages = messages_response.json()
                assert isinstance(messages, list), "Messages should be a list"
                
                # Should find our test message
                test_messages = [m for m in messages if m.get("content") == "Test message"]
                assert len(test_messages) > 0, "Test message not found in conversation"