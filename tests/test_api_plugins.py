"""Tests for plugin management API endpoints."""

from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.main import app
from chatter.models.user import User
from chatter.services.plugins import PluginError


@pytest.mark.unit
class TestPluginEndpoints:
    """Test plugin management API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_install_plugin_success(self):
        """Test successful plugin installation."""
        # Arrange
        install_data = {
            "source": "github",
            "repository": "owner/plugin-repo",
            "version": "1.0.0",
            "auto_enable": True,
            "config": {
                "api_key": "test-key",
                "endpoint": "https://api.example.com"
            }
        }

        mock_installed_plugin = {
            "id": "plugin-123",
            "name": "Test Plugin",
            "description": "A test plugin for API testing",
            "version": "1.0.0",
            "source": "github",
            "repository": "owner/plugin-repo",
            "status": "installed",
            "is_enabled": True,
            "config": {
                "api_key": "***",  # Masked in response
                "endpoint": "https://api.example.com"
            },
            "installed_at": "2024-01-01T00:00:00Z",
            "installed_by": self.mock_user.id,
            "capabilities": ["llm_integration", "data_processing"],
            "metadata": {
                "author": "Plugin Author",
                "license": "MIT"
            }
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.install_plugin.return_value = mock_installed_plugin

            # Act
            response = self.client.post("/plugins/install", json=install_data)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "plugin-123"
            assert data["name"] == "Test Plugin"
            assert data["version"] == "1.0.0"
            assert data["status"] == "installed"
            assert data["is_enabled"] is True
            assert data["installed_by"] == self.mock_user.id
            mock_manager.install_plugin.assert_called_once()

    def test_install_plugin_from_file(self):
        """Test plugin installation from uploaded file."""
        # Arrange
        install_data = {
            "source": "file",
            "file_path": "/tmp/uploaded_plugin.zip",
            "auto_enable": False,
            "verify_signature": True
        }

        mock_installed_plugin = {
            "id": "file-plugin-456",
            "name": "File Plugin",
            "version": "2.0.0",
            "source": "file",
            "status": "installed",
            "is_enabled": False,  # auto_enable was False
            "installed_by": self.mock_user.id
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.install_plugin.return_value = mock_installed_plugin

            # Act
            response = self.client.post("/plugins/install", json=install_data)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "file-plugin-456"
            assert data["source"] == "file"
            assert data["is_enabled"] is False

    def test_install_plugin_validation_error(self):
        """Test plugin installation with validation errors."""
        # Arrange
        invalid_install_data = {
            "source": "invalid_source",  # Should be 'github', 'file', 'registry', etc.
            "repository": "",  # Empty repository
            "version": "not-a-version"  # Invalid version format
        }

        # Act
        response = self.client.post("/plugins/install", json=invalid_install_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_install_plugin_already_exists(self):
        """Test plugin installation when plugin already exists."""
        # Arrange
        install_data = {
            "source": "github",
            "repository": "owner/existing-plugin"
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.install_plugin.side_effect = PluginError("Plugin already exists")

            # Act
            response = self.client.post("/plugins/install", json=install_data)

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in response.json()["detail"]

    def test_list_plugins_success(self):
        """Test successful plugin listing."""
        # Arrange
        mock_plugins = [
            {
                "id": "plugin-1",
                "name": "Plugin 1",
                "description": "First test plugin",
                "version": "1.0.0",
                "status": "installed",
                "is_enabled": True,
                "capabilities": ["llm_integration"],
                "installed_by": self.mock_user.id
            },
            {
                "id": "plugin-2",
                "name": "Plugin 2",
                "description": "Second test plugin",
                "version": "2.1.0",
                "status": "installed",
                "is_enabled": False,
                "capabilities": ["data_processing", "analytics"],
                "installed_by": "other-user-id"
            }
        ]
        mock_total = 2

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.list_plugins.return_value = (mock_plugins, mock_total)

            # Act
            response = self.client.get("/plugins/?page=1&per_page=10")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["plugins"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 10
            assert data["plugins"][0]["name"] == "Plugin 1"
            assert data["plugins"][1]["is_enabled"] is False

    def test_list_plugins_with_filters(self):
        """Test plugin listing with filters."""
        # Arrange
        mock_enabled_plugins = [
            {
                "id": "enabled-plugin",
                "name": "Enabled Plugin",
                "status": "installed",
                "is_enabled": True,
                "capabilities": ["llm_integration"]
            }
        ]

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.list_plugins.return_value = (mock_enabled_plugins, 1)

            # Act
            response = self.client.get("/plugins/?enabled=true&capability=llm_integration")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["plugins"]) == 1
            assert data["plugins"][0]["is_enabled"] is True
            assert "llm_integration" in data["plugins"][0]["capabilities"]

    def test_get_plugin_success(self):
        """Test successful plugin retrieval."""
        # Arrange
        plugin_id = "plugin-123"
        mock_plugin = {
            "id": plugin_id,
            "name": "Test Plugin",
            "description": "A detailed test plugin",
            "version": "1.2.0",
            "source": "github",
            "repository": "owner/test-plugin",
            "status": "installed",
            "is_enabled": True,
            "config": {
                "api_endpoint": "https://api.test.com",
                "timeout": 30
            },
            "capabilities": ["llm_integration", "data_processing"],
            "metadata": {
                "author": "Test Author",
                "license": "MIT",
                "documentation": "https://docs.test.com"
            },
            "installed_at": "2024-01-01T00:00:00Z",
            "installed_by": self.mock_user.id,
            "last_updated": "2024-01-15T00:00:00Z"
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.get_plugin.return_value = mock_plugin

            # Act
            response = self.client.get(f"/plugins/{plugin_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == plugin_id
            assert data["name"] == "Test Plugin"
            assert data["version"] == "1.2.0"
            assert len(data["capabilities"]) == 2
            assert data["metadata"]["author"] == "Test Author"

    def test_get_plugin_not_found(self):
        """Test plugin retrieval when plugin doesn't exist."""
        # Arrange
        plugin_id = "nonexistent-plugin"

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.get_plugin.side_effect = PluginError("Plugin not found")

            # Act
            response = self.client.get(f"/plugins/{plugin_id}")

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_plugin_success(self):
        """Test successful plugin update."""
        # Arrange
        plugin_id = "plugin-update-123"
        update_data = {
            "version": "2.0.0",
            "config": {
                "api_endpoint": "https://api.updated.com",
                "new_setting": "value"
            },
            "auto_restart": True
        }

        mock_updated_plugin = {
            "id": plugin_id,
            "name": "Updated Plugin",
            "version": "2.0.0",
            "status": "installed",
            "config": {
                "api_endpoint": "https://api.updated.com",
                "new_setting": "value"
            },
            "last_updated": "2024-01-20T00:00:00Z"
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.update_plugin.return_value = mock_updated_plugin

            # Act
            response = self.client.put(f"/plugins/{plugin_id}", json=update_data)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["version"] == "2.0.0"
            assert data["config"]["api_endpoint"] == "https://api.updated.com"
            assert data["config"]["new_setting"] == "value"

    def test_delete_plugin_success(self):
        """Test successful plugin deletion."""
        # Arrange
        plugin_id = "plugin-delete-123"

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.uninstall_plugin.return_value = True

            # Act
            response = self.client.delete(f"/plugins/{plugin_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["plugin_id"] == plugin_id

    def test_delete_plugin_in_use(self):
        """Test plugin deletion when plugin is in use."""
        # Arrange
        plugin_id = "plugin-in-use-123"

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.uninstall_plugin.side_effect = PluginError("Plugin is currently in use")

            # Act
            response = self.client.delete(f"/plugins/{plugin_id}")

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "in use" in response.json()["detail"]

    def test_enable_plugin_success(self):
        """Test successful plugin enabling."""
        # Arrange
        plugin_id = "plugin-enable-123"

        mock_result = {
            "success": True,
            "plugin_id": plugin_id,
            "action": "enabled",
            "message": "Plugin enabled successfully"
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.enable_plugin.return_value = mock_result

            # Act
            response = self.client.post(f"/plugins/{plugin_id}/enable")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["action"] == "enabled"
            assert data["plugin_id"] == plugin_id

    def test_enable_plugin_already_enabled(self):
        """Test enabling plugin that's already enabled."""
        # Arrange
        plugin_id = "plugin-already-enabled"

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.enable_plugin.side_effect = PluginError("Plugin is already enabled")

            # Act
            response = self.client.post(f"/plugins/{plugin_id}/enable")

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "already enabled" in response.json()["detail"]

    def test_disable_plugin_success(self):
        """Test successful plugin disabling."""
        # Arrange
        plugin_id = "plugin-disable-123"

        mock_result = {
            "success": True,
            "plugin_id": plugin_id,
            "action": "disabled",
            "message": "Plugin disabled successfully"
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.disable_plugin.return_value = mock_result

            # Act
            response = self.client.post(f"/plugins/{plugin_id}/disable")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["action"] == "disabled"
            assert data["plugin_id"] == plugin_id

    def test_disable_plugin_has_dependencies(self):
        """Test disabling plugin that has active dependencies."""
        # Arrange
        plugin_id = "plugin-with-deps"

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.disable_plugin.side_effect = PluginError(
                "Cannot disable plugin: other plugins depend on it"
            )

            # Act
            response = self.client.post(f"/plugins/{plugin_id}/disable")

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "depend on it" in response.json()["detail"]


@pytest.mark.unit
class TestPluginValidation:
    """Test plugin validation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )

        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_install_plugin_missing_source(self):
        """Test plugin installation missing source field."""
        # Arrange
        install_data = {
            "repository": "owner/plugin-repo",
            "version": "1.0.0"
            # Missing 'source' field
        }

        # Act
        response = self.client.post("/plugins/install", json=install_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        source_error = next((e for e in errors if "source" in e["loc"]), None)
        assert source_error is not None

    def test_install_plugin_invalid_version_format(self):
        """Test plugin installation with invalid version format."""
        # Arrange
        install_data = {
            "source": "github",
            "repository": "owner/plugin-repo",
            "version": "not.a.version"  # Invalid semantic version
        }

        # Act
        response = self.client.post("/plugins/install", json=install_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_plugin_invalid_config(self):
        """Test plugin update with invalid configuration."""
        # Arrange
        plugin_id = "plugin-123"
        update_data = {
            "config": "not an object"  # Should be a dict/object
        }

        # Act
        response = self.client.put(f"/plugins/{plugin_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestPluginIntegration:
    """Integration tests for plugin workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="integration-user-id",
            email="integration@example.com",
            username="integrationuser",
            is_active=True
        )

        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_plugin_lifecycle_workflow(self):
        """Test complete plugin lifecycle: install, enable, configure, disable, uninstall."""
        # Step 1: Install plugin
        install_data = {
            "source": "github",
            "repository": "test/example-plugin",
            "version": "1.0.0",
            "auto_enable": False
        }

        mock_installed_plugin = {
            "id": "lifecycle-plugin-123",
            "name": "Lifecycle Test Plugin",
            "version": "1.0.0",
            "status": "installed",
            "is_enabled": False
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.install_plugin.return_value = mock_installed_plugin

            install_response = self.client.post("/plugins/install", json=install_data)
            assert install_response.status_code == status.HTTP_201_CREATED
            plugin_id = install_response.json()["id"]

        # Step 2: Enable plugin
        mock_enable_result = {
            "success": True,
            "plugin_id": plugin_id,
            "action": "enabled"
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.enable_plugin.return_value = mock_enable_result

            enable_response = self.client.post(f"/plugins/{plugin_id}/enable")
            assert enable_response.status_code == status.HTTP_200_OK
            assert enable_response.json()["success"] is True

        # Step 3: Configure plugin
        config_data = {
            "config": {
                "api_key": "new-api-key",
                "timeout": 60
            }
        }

        mock_updated_plugin = {
            "id": plugin_id,
            "name": "Lifecycle Test Plugin",
            "version": "1.0.0",
            "is_enabled": True,
            "config": {
                "api_key": "***",  # Masked
                "timeout": 60
            }
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.update_plugin.return_value = mock_updated_plugin

            update_response = self.client.put(f"/plugins/{plugin_id}", json=config_data)
            assert update_response.status_code == status.HTTP_200_OK
            assert update_response.json()["config"]["timeout"] == 60

        # Step 4: Disable plugin
        mock_disable_result = {
            "success": True,
            "plugin_id": plugin_id,
            "action": "disabled"
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.disable_plugin.return_value = mock_disable_result

            disable_response = self.client.post(f"/plugins/{plugin_id}/disable")
            assert disable_response.status_code == status.HTTP_200_OK
            assert disable_response.json()["action"] == "disabled"

        # Step 5: Uninstall plugin
        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.uninstall_plugin.return_value = True

            delete_response = self.client.delete(f"/plugins/{plugin_id}")
            assert delete_response.status_code == status.HTTP_200_OK
            assert delete_response.json()["deleted"] is True

    def test_plugin_dependency_workflow(self):
        """Test plugin dependency management workflow."""
        # Step 1: Install base plugin (dependency)
        base_plugin_data = {
            "source": "github",
            "repository": "test/base-plugin",
            "version": "1.0.0"
        }

        mock_base_plugin = {
            "id": "base-plugin-123",
            "name": "Base Plugin",
            "capabilities": ["core_functionality"]
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.install_plugin.return_value = mock_base_plugin

            base_response = self.client.post("/plugins/install", json=base_plugin_data)
            base_plugin_id = base_response.json()["id"]

        # Step 2: Install dependent plugin
        dependent_plugin_data = {
            "source": "github",
            "repository": "test/dependent-plugin",
            "version": "1.0.0",
            "dependencies": [base_plugin_id]
        }

        mock_dependent_plugin = {
            "id": "dependent-plugin-456",
            "name": "Dependent Plugin",
            "dependencies": [base_plugin_id],
            "capabilities": ["extended_functionality"]
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.install_plugin.return_value = mock_dependent_plugin

            dependent_response = self.client.post("/plugins/install", json=dependent_plugin_data)
            dependent_plugin_id = dependent_response.json()["id"]

        # Step 3: Try to disable base plugin (should fail due to dependency)
        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.disable_plugin.side_effect = PluginError(
                f"Cannot disable plugin: {dependent_plugin_id} depends on it"
            )

            disable_response = self.client.post(f"/plugins/{base_plugin_id}/disable")
            assert disable_response.status_code == status.HTTP_400_BAD_REQUEST
            assert "depends on it" in disable_response.json()["detail"]

        # Step 4: Disable dependent plugin first
        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.disable_plugin.return_value = {
                "success": True,
                "plugin_id": dependent_plugin_id,
                "action": "disabled"
            }

            disable_dependent_response = self.client.post(f"/plugins/{dependent_plugin_id}/disable")
            assert disable_dependent_response.status_code == status.HTTP_200_OK

        # Step 5: Now disable base plugin (should succeed)
        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.disable_plugin.return_value = {
                "success": True,
                "plugin_id": base_plugin_id,
                "action": "disabled"
            }

            disable_base_response = self.client.post(f"/plugins/{base_plugin_id}/disable")
            assert disable_base_response.status_code == status.HTTP_200_OK

    def test_plugin_marketplace_workflow(self):
        """Test plugin marketplace browsing and installation workflow."""
        # Step 1: List available plugins (simulating marketplace)
        mock_available_plugins = [
            {
                "id": "marketplace-plugin-1",
                "name": "Analytics Plugin",
                "description": "Advanced analytics capabilities",
                "version": "2.1.0",
                "status": "available",
                "is_enabled": False,
                "capabilities": ["analytics", "reporting"],
                "rating": 4.5,
                "downloads": 1500
            },
            {
                "id": "marketplace-plugin-2",
                "name": "Integration Plugin",
                "description": "Third-party service integrations",
                "version": "1.3.0",
                "status": "available",
                "is_enabled": False,
                "capabilities": ["integrations", "webhooks"],
                "rating": 4.2,
                "downloads": 800
            }
        ]

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.list_plugins.return_value = (mock_available_plugins, 2)

            marketplace_response = self.client.get("/plugins/?status=available")
            assert marketplace_response.status_code == status.HTTP_200_OK
            plugins = marketplace_response.json()["plugins"]
            assert len(plugins) == 2
            assert all(p["status"] == "available" for p in plugins)

        # Step 2: Get detailed information about a specific plugin
        plugin_details = {
            "id": "marketplace-plugin-1",
            "name": "Analytics Plugin",
            "description": "Advanced analytics capabilities with detailed reporting",
            "version": "2.1.0",
            "capabilities": ["analytics", "reporting", "visualization"],
            "metadata": {
                "author": "Analytics Corp",
                "license": "MIT",
                "documentation": "https://docs.analytics.com",
                "repository": "https://github.com/analytics/plugin"
            },
            "requirements": {
                "min_chatter_version": "1.0.0",
                "python_packages": ["pandas", "matplotlib"]
            },
            "changelog": {
                "2.1.0": "Added new visualization features",
                "2.0.0": "Major rewrite with performance improvements"
            }
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.get_plugin.return_value = plugin_details

            details_response = self.client.get("/plugins/marketplace-plugin-1")
            assert details_response.status_code == status.HTTP_200_OK
            data = details_response.json()
            assert data["name"] == "Analytics Plugin"
            assert "visualization" in data["capabilities"]
            assert "documentation" in data["metadata"]

        # Step 3: Install the selected plugin
        install_data = {
            "source": "marketplace",
            "plugin_id": "marketplace-plugin-1",
            "version": "2.1.0",
            "auto_enable": True
        }

        mock_installed_plugin = {
            "id": "marketplace-plugin-1",
            "name": "Analytics Plugin",
            "status": "installed",
            "is_enabled": True,
            "installed_by": self.mock_user.id
        }

        with patch('chatter.services.plugins.plugin_manager') as mock_manager:
            mock_manager.install_plugin.return_value = mock_installed_plugin

            install_response = self.client.post("/plugins/install", json=install_data)
            assert install_response.status_code == status.HTTP_201_CREATED
            assert install_response.json()["status"] == "installed"
            assert install_response.json()["is_enabled"] is True
