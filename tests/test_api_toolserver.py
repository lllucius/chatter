"""Tests for tool server management API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.main import app
from chatter.models.user import User
from chatter.services.tool_access import ToolAccessService
from chatter.services.toolserver import (
    ToolServerService,
    ToolServerServiceError,
)
from chatter.utils.database import get_session


@pytest.mark.unit
class TestToolServerEndpoints:
    """Test tool server management API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True,
        )

        self.mock_session = AsyncMock()

        # Override dependencies
        app.dependency_overrides[get_current_user] = (
            lambda: self.mock_user
        )
        app.dependency_overrides[get_session] = (
            lambda: self.mock_session
        )

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_tool_server_success(self):
        """Test successful tool server creation."""
        # Arrange
        server_data = {
            "name": "Test Tool Server",
            "description": "A test tool server for API testing",
            "url": "https://tools.example.com",
            "server_type": "mcp",
            "auth_config": {
                "type": "api_key",
                "api_key": "test-api-key",
            },
            "tool_config": {
                "auto_discover": True,
                "timeout": 30,
                "max_retries": 3,
            },
            "is_active": True,
            "tags": ["test", "api"],
        }

        mock_created_server = {
            "id": "server-123",
            "name": "Test Tool Server",
            "description": "A test tool server for API testing",
            "url": "https://tools.example.com",
            "server_type": "mcp",
            "auth_config": {
                "type": "api_key",
                "api_key": "***",  # Masked in response
            },
            "tool_config": {
                "auto_discover": True,
                "timeout": 30,
                "max_retries": 3,
            },
            "is_active": True,
            "tags": ["test", "api"],
            "status": "pending",
            "created_by": self.mock_user.id,
            "created_at": "2024-01-01T00:00:00Z",
            "last_health_check": None,
            "tool_count": 0,
        }

        with patch.object(
            ToolServerService, 'create_tool_server'
        ) as mock_create:
            mock_create.return_value = mock_created_server

            # Act
            response = self.client.post(
                "/toolserver/servers", json=server_data
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "server-123"
            assert data["name"] == "Test Tool Server"
            assert data["server_type"] == "mcp"
            assert data["status"] == "pending"
            assert data["created_by"] == self.mock_user.id
            assert data["auth_config"]["api_key"] == "***"  # Masked
            mock_create.assert_called_once()

    def test_create_tool_server_validation_error(self):
        """Test tool server creation with validation errors."""
        # Arrange
        invalid_server_data = {
            "name": "",  # Empty name should fail validation
            "url": "not-a-valid-url",  # Invalid URL format
            "server_type": "invalid_type",  # Invalid server type
        }

        # Act
        response = self.client.post(
            "/toolserver/servers", json=invalid_server_data
        )

        # Assert
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_list_tool_servers_success(self):
        """Test successful tool server listing."""
        # Arrange
        mock_servers = [
            {
                "id": "server-1",
                "name": "Server 1",
                "description": "First test server",
                "url": "https://tools1.example.com",
                "server_type": "mcp",
                "status": "active",
                "is_active": True,
                "tool_count": 5,
                "last_health_check": "2024-01-01T00:00:00Z",
            },
            {
                "id": "server-2",
                "name": "Server 2",
                "description": "Second test server",
                "url": "https://tools2.example.com",
                "server_type": "rest",
                "status": "inactive",
                "is_active": False,
                "tool_count": 3,
                "last_health_check": "2023-12-31T00:00:00Z",
            },
        ]

        with patch.object(
            ToolServerService, 'list_tool_servers'
        ) as mock_list:
            mock_list.return_value = mock_servers

            # Act
            response = self.client.get("/toolserver/servers")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "Server 1"
            assert data[0]["tool_count"] == 5
            assert data[1]["status"] == "inactive"

    def test_get_tool_server_success(self):
        """Test successful tool server retrieval."""
        # Arrange
        server_id = "server-123"
        mock_server = {
            "id": server_id,
            "name": "Test Server",
            "description": "A detailed test server",
            "url": "https://tools.example.com",
            "server_type": "mcp",
            "status": "active",
            "is_active": True,
            "auth_config": {"type": "bearer_token", "token": "***"},
            "tool_config": {"auto_discover": True, "timeout": 30},
            "tags": ["production", "api"],
            "tool_count": 8,
            "last_health_check": "2024-01-01T12:00:00Z",
            "created_by": self.mock_user.id,
            "created_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(
            ToolServerService, 'get_tool_server'
        ) as mock_get:
            mock_get.return_value = mock_server

            # Act
            response = self.client.get(
                f"/toolserver/servers/{server_id}"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == server_id
            assert data["name"] == "Test Server"
            assert data["tool_count"] == 8
            assert data["status"] == "active"

    def test_get_tool_server_not_found(self):
        """Test tool server retrieval when server doesn't exist."""
        # Arrange
        server_id = "nonexistent-server"

        with patch.object(
            ToolServerService, 'get_tool_server'
        ) as mock_get:
            mock_get.side_effect = ToolServerServiceError(
                "Tool server not found"
            )

            # Act
            response = self.client.get(
                f"/toolserver/servers/{server_id}"
            )

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_tool_server_success(self):
        """Test successful tool server update."""
        # Arrange
        server_id = "server-update-123"
        update_data = {
            "name": "Updated Tool Server",
            "description": "Updated description",
            "auth_config": {
                "type": "api_key",
                "api_key": "new-api-key",
            },
            "tool_config": {"timeout": 60, "max_retries": 5},
            "is_active": False,
            "tags": ["updated", "test"],
        }

        mock_updated_server = {
            "id": server_id,
            "name": "Updated Tool Server",
            "description": "Updated description",
            "auth_config": {"type": "api_key", "api_key": "***"},
            "tool_config": {"timeout": 60, "max_retries": 5},
            "is_active": False,
            "tags": ["updated", "test"],
            "updated_at": "2024-01-15T00:00:00Z",
        }

        with patch.object(
            ToolServerService, 'update_tool_server'
        ) as mock_update:
            mock_update.return_value = mock_updated_server

            # Act
            response = self.client.put(
                f"/toolserver/servers/{server_id}", json=update_data
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Tool Server"
            assert data["tool_config"]["timeout"] == 60
            assert data["is_active"] is False
            assert "updated" in data["tags"]

    def test_delete_tool_server_success(self):
        """Test successful tool server deletion."""
        # Arrange
        server_id = "server-delete-123"

        with patch.object(
            ToolServerService, 'delete_tool_server'
        ) as mock_delete:
            mock_delete.return_value = True

            # Act
            response = self.client.delete(
                f"/toolserver/servers/{server_id}"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["server_id"] == server_id

    def test_start_tool_server_success(self):
        """Test successful tool server start operation."""
        # Arrange
        server_id = "server-start-123"

        mock_result = {
            "success": True,
            "server_id": server_id,
            "operation": "start",
            "message": "Tool server started successfully",
            "status": "active",
        }

        with patch.object(
            ToolServerService, 'start_tool_server'
        ) as mock_start:
            mock_start.return_value = mock_result

            # Act
            response = self.client.post(
                f"/toolserver/servers/{server_id}/start"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["operation"] == "start"
            assert data["status"] == "active"

    def test_stop_tool_server_success(self):
        """Test successful tool server stop operation."""
        # Arrange
        server_id = "server-stop-123"

        mock_result = {
            "success": True,
            "server_id": server_id,
            "operation": "stop",
            "message": "Tool server stopped successfully",
            "status": "inactive",
        }

        with patch.object(
            ToolServerService, 'stop_tool_server'
        ) as mock_stop:
            mock_stop.return_value = mock_result

            # Act
            response = self.client.post(
                f"/toolserver/servers/{server_id}/stop"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["operation"] == "stop"
            assert data["status"] == "inactive"

    def test_restart_tool_server_success(self):
        """Test successful tool server restart operation."""
        # Arrange
        server_id = "server-restart-123"

        mock_result = {
            "success": True,
            "server_id": server_id,
            "operation": "restart",
            "message": "Tool server restarted successfully",
            "status": "active",
        }

        with patch.object(
            ToolServerService, 'restart_tool_server'
        ) as mock_restart:
            mock_restart.return_value = mock_result

            # Act
            response = self.client.post(
                f"/toolserver/servers/{server_id}/restart"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["operation"] == "restart"

    def test_health_check_success(self):
        """Test successful tool server health check."""
        # Arrange
        server_id = "server-health-123"

        mock_health_result = {
            "server_id": server_id,
            "status": "healthy",
            "response_time": 150,
            "tool_count": 5,
            "last_check": "2024-01-01T12:00:00Z",
            "issues": [],
            "details": {
                "connectivity": "ok",
                "authentication": "ok",
                "tools_accessible": True,
            },
        }

        with patch.object(
            ToolServerService, 'health_check'
        ) as mock_health:
            mock_health.return_value = mock_health_result

            # Act
            response = self.client.post(
                f"/toolserver/servers/{server_id}/health"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"
            assert data["response_time"] == 150
            assert data["tool_count"] == 5
            assert len(data["issues"]) == 0

    def test_get_server_tools_success(self):
        """Test successful server tools retrieval."""
        # Arrange
        server_id = "server-tools-123"

        mock_tools = [
            {
                "id": "tool-1",
                "name": "calculator",
                "description": "Basic calculator tool",
                "type": "function",
                "parameters": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression",
                    }
                },
                "server_id": server_id,
                "is_available": True,
            },
            {
                "id": "tool-2",
                "name": "weather",
                "description": "Weather information tool",
                "type": "function",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Location for weather",
                    }
                },
                "server_id": server_id,
                "is_available": True,
            },
        ]

        with patch.object(
            ToolServerService, 'get_server_tools'
        ) as mock_get_tools:
            mock_get_tools.return_value = mock_tools

            # Act
            response = self.client.get(
                f"/toolserver/servers/{server_id}/tools"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["tools"]) == 2
            assert data["tools"][0]["name"] == "calculator"
            assert data["tools"][1]["name"] == "weather"
            assert all(tool["is_available"] for tool in data["tools"])

    def test_bulk_tool_server_operations_success(self):
        """Test successful bulk tool server operations."""
        # Arrange
        bulk_operation = {
            "operation": "start",
            "server_ids": ["server-1", "server-2", "server-3"],
            "options": {"parallel": True, "timeout": 60},
        }

        mock_bulk_result = {
            "operation": "start",
            "total_requested": 3,
            "successful": 2,
            "failed": 1,
            "results": [
                {
                    "server_id": "server-1",
                    "success": True,
                    "message": "Started successfully",
                },
                {
                    "server_id": "server-2",
                    "success": True,
                    "message": "Started successfully",
                },
                {
                    "server_id": "server-3",
                    "success": False,
                    "message": "Failed to start: connection timeout",
                },
            ],
            "execution_time": 45.2,
        }

        with patch.object(
            ToolServerService, 'bulk_operation'
        ) as mock_bulk:
            mock_bulk.return_value = mock_bulk_result

            # Act
            response = self.client.post(
                "/toolserver/servers/bulk", json=bulk_operation
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["operation"] == "start"
            assert data["successful"] == 2
            assert data["failed"] == 1
            assert len(data["results"]) == 3

    def test_get_all_tools_success(self):
        """Test successful retrieval of all tools from all servers."""
        # Arrange
        mock_all_tools = [
            {
                "id": "tool-1",
                "name": "calculator",
                "server_id": "server-1",
                "server_name": "Math Server",
                "is_available": True,
            },
            {
                "id": "tool-2",
                "name": "weather",
                "server_id": "server-2",
                "server_name": "Weather Server",
                "is_available": True,
            },
            {
                "id": "tool-3",
                "name": "search",
                "server_id": "server-3",
                "server_name": "Search Server",
                "is_available": False,
            },
        ]

        with patch.object(
            ToolServerService, 'get_all_tools'
        ) as mock_get_all:
            mock_get_all.return_value = mock_all_tools

            # Act
            response = self.client.get("/toolserver/tools/all")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 3
            assert data[0]["name"] == "calculator"
            assert data[1]["server_name"] == "Weather Server"
            assert data[2]["is_available"] is False

    def test_test_server_connectivity_success(self):
        """Test successful server connectivity testing."""
        # Arrange
        server_id = "server-connectivity-123"

        mock_connectivity_result = {
            "server_id": server_id,
            "connectivity": "ok",
            "response_time": 200,
            "authentication": "valid",
            "tool_discovery": "successful",
            "issues": [],
            "tested_at": "2024-01-01T12:00:00Z",
        }

        with patch.object(
            ToolServerService, 'test_connectivity'
        ) as mock_test:
            mock_test.return_value = mock_connectivity_result

            # Act
            response = self.client.post(
                f"/toolserver/servers/{server_id}/test-connectivity"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["connectivity"] == "ok"
            assert data["authentication"] == "valid"
            assert data["tool_discovery"] == "successful"


@pytest.mark.unit
class TestToolPermissionEndpoints:
    """Test tool permission management endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True,
        )

        self.mock_session = AsyncMock()

        app.dependency_overrides[get_current_user] = (
            lambda: self.mock_user
        )
        app.dependency_overrides[get_session] = (
            lambda: self.mock_session
        )

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_tool_permission_success(self):
        """Test successful tool permission creation."""
        # Arrange
        permission_data = {
            "user_id": "user-123",
            "tool_id": "tool-456",
            "permission_level": "read_write",
            "expires_at": "2024-12-31T23:59:59Z",
            "restrictions": {
                "max_calls_per_hour": 100,
                "allowed_operations": ["read", "write"],
            },
        }

        mock_created_permission = {
            "id": "permission-789",
            "user_id": "user-123",
            "tool_id": "tool-456",
            "permission_level": "read_write",
            "expires_at": "2024-12-31T23:59:59Z",
            "restrictions": {
                "max_calls_per_hour": 100,
                "allowed_operations": ["read", "write"],
            },
            "created_by": self.mock_user.id,
            "created_at": "2024-01-01T00:00:00Z",
            "is_active": True,
        }

        with patch.object(
            ToolAccessService, 'create_tool_permission'
        ) as mock_create:
            mock_create.return_value = mock_created_permission

            # Act
            response = self.client.post(
                "/toolserver/permissions", json=permission_data
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "permission-789"
            assert data["user_id"] == "user-123"
            assert data["permission_level"] == "read_write"
            assert data["restrictions"]["max_calls_per_hour"] == 100

    def test_update_tool_permission_success(self):
        """Test successful tool permission update."""
        # Arrange
        permission_id = "permission-update-123"
        update_data = {
            "permission_level": "read_only",
            "restrictions": {"max_calls_per_hour": 50},
        }

        mock_updated_permission = {
            "id": permission_id,
            "permission_level": "read_only",
            "restrictions": {"max_calls_per_hour": 50},
            "updated_at": "2024-01-15T00:00:00Z",
        }

        with patch.object(
            ToolAccessService, 'update_tool_permission'
        ) as mock_update:
            mock_update.return_value = mock_updated_permission

            # Act
            response = self.client.put(
                f"/toolserver/permissions/{permission_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["permission_level"] == "read_only"
            assert data["restrictions"]["max_calls_per_hour"] == 50

    def test_delete_tool_permission_success(self):
        """Test successful tool permission deletion."""
        # Arrange
        permission_id = "permission-delete-123"

        with patch.object(
            ToolAccessService, 'delete_tool_permission'
        ) as mock_delete:
            mock_delete.return_value = True

            # Act
            response = self.client.delete(
                f"/toolserver/permissions/{permission_id}"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["permission_id"] == permission_id

    def test_check_tool_access_success(self):
        """Test successful tool access check."""
        # Arrange
        access_check = {
            "user_id": "user-123",
            "tool_id": "tool-456",
            "operation": "execute",
        }

        mock_access_result = {
            "user_id": "user-123",
            "tool_id": "tool-456",
            "has_access": True,
            "permission_level": "read_write",
            "restrictions": {
                "max_calls_per_hour": 100,
                "remaining_calls": 87,
            },
            "access_details": {
                "source": "user_permission",
                "expires_at": "2024-12-31T23:59:59Z",
            },
        }

        with patch.object(
            ToolAccessService, 'check_tool_access'
        ) as mock_check:
            mock_check.return_value = mock_access_result

            # Act
            response = self.client.post(
                "/toolserver/access-check", json=access_check
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["has_access"] is True
            assert data["permission_level"] == "read_write"
            assert data["restrictions"]["remaining_calls"] == 87


@pytest.mark.integration
class TestToolServerIntegration:
    """Integration tests for tool server workflows using real database."""

    def setup_method(self):
        """Set up test fixtures."""
        # Real database session and user will be injected via pytest fixtures
        pass

    def teardown_method(self):
        """Clean up after tests."""
        # Clean up dependency overrides if any were set
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_tool_server_lifecycle_workflow(self, test_db_session):
        """Test tool server workflow with real database."""
        from chatter.models.user import User
        from chatter.services.toolserver import ToolServerService
        
        # Create a real user for testing
        user = User(
            email="toolserver@example.com",
            username="toolserveruser",
            hashed_password="hashed_password_here",
            full_name="Toolserver Test User",
            is_active=True,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        
        # Create toolserver service with real database session
        toolserver_service = ToolServerService(test_db_session)
        
        # Test basic database operations for toolserver workflows
        # Verify user was created in database
        assert user.id is not None
        assert user.email == "toolserver@example.com"
        assert user.username == "toolserveruser"
        assert user.is_active is True
        
        # Test real database operations foundational for toolserver management
        from sqlalchemy import text
        result = await test_db_session.execute(
            text("SELECT id, email FROM users WHERE email = :email"),
            {"email": "toolserver@example.com"}
        )
        db_user = result.fetchone()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.email == "toolserver@example.com"
        
        # Note: For full API testing with real database, we would need
        # to set up dependency overrides with real database session
        # This integration test focuses on the database layer
