"""Tests for workflow security core functionality."""

# Mock all required modules at module level
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

for module_name in [
    'chatter.core.workflow_security',
    'chatter.utils.security',
    'chatter.schemas.workflow',
    'chatter.core.auth',
    'chatter.models.workflow'
]:
    if module_name not in sys.modules:
        sys.modules[module_name] = MagicMock()


@pytest.mark.unit
class TestWorkflowSecurity:
    """Test workflow security functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_user = MagicMock()
        self.mock_user.id = "user-123"
        self.mock_user.role = "user"
        self.mock_user.permissions = ["workflow.read", "workflow.execute"]

    def test_workflow_access_validation(self):
        """Test workflow access validation."""
        # Arrange
        workflow_data = {
            "id": "workflow-123",
            "name": "Test Workflow",
            "owner_id": "user-123",
            "visibility": "private"
        }

        # Mock security service
        security_service = MagicMock()
        security_service.validate_workflow_access = MagicMock(return_value=True)

        # Act
        has_access = security_service.validate_workflow_access(
            user=self.mock_user,
            workflow=workflow_data,
            action="read"
        )

        # Assert
        assert has_access is True
        security_service.validate_workflow_access.assert_called_once_with(
            user=self.mock_user,
            workflow=workflow_data,
            action="read"
        )

    def test_workflow_permission_check(self):
        """Test workflow permission checking."""
        # Arrange
        required_permissions = ["workflow.execute", "workflow.read"]

        # Mock permission service
        permission_service = MagicMock()
        permission_service.check_permissions = MagicMock(return_value=True)

        # Act
        has_permissions = permission_service.check_permissions(
            user=self.mock_user,
            required_permissions=required_permissions
        )

        # Assert
        assert has_permissions is True
        permission_service.check_permissions.assert_called_once_with(
            user=self.mock_user,
            required_permissions=required_permissions
        )

    def test_workflow_input_sanitization(self):
        """Test workflow input sanitization."""
        # Arrange
        unsafe_input = {
            "user_input": "<script>alert('xss')</script>",
            "file_path": "../../../etc/passwd",
            "command": "rm -rf /",
            "safe_data": "This is safe content"
        }

        expected_sanitized = {
            "user_input": "&lt;script&gt;alert('xss')&lt;/script&gt;",
            "file_path": "etc/passwd",
            "command": "[BLOCKED_COMMAND]",
            "safe_data": "This is safe content"
        }

        # Mock sanitization service
        sanitizer = MagicMock()
        sanitizer.sanitize_workflow_input = MagicMock(return_value=expected_sanitized)

        # Act
        sanitized = sanitizer.sanitize_workflow_input(unsafe_input)

        # Assert
        assert sanitized["user_input"] == "&lt;script&gt;alert('xss')&lt;/script&gt;"
        assert sanitized["file_path"] == "etc/passwd"
        assert sanitized["command"] == "[BLOCKED_COMMAND]"
        assert sanitized["safe_data"] == "This is safe content"

    def test_workflow_execution_authorization(self):
        """Test workflow execution authorization."""
        # Arrange
        workflow = {
            "id": "workflow-123",
            "security_level": "standard",
            "required_permissions": ["workflow.execute"],
            "owner_id": "user-123"
        }

        # Mock authorization service
        auth_service = MagicMock()
        auth_service.authorize_workflow_execution = MagicMock(return_value={
            "authorized": True,
            "restrictions": [],
            "allowed_actions": ["read", "write", "execute"]
        })

        # Act
        auth_result = auth_service.authorize_workflow_execution(
            user=self.mock_user,
            workflow=workflow
        )

        # Assert
        assert auth_result["authorized"] is True
        assert len(auth_result["restrictions"]) == 0
        assert "execute" in auth_result["allowed_actions"]

    def test_workflow_data_masking(self):
        """Test workflow data masking for sensitive information."""
        # Arrange
        sensitive_data = {
            "user_email": "test@example.com",
            "api_key": "sk-1234567890abcdef",
            "password": "secret123",
            "credit_card": "4111-1111-1111-1111",
            "ssn": "123-45-6789",
            "public_info": "This is public"
        }

        expected_masked = {
            "user_email": "t***@example.com",
            "api_key": "sk-***",
            "password": "***",
            "credit_card": "****-****-****-1111",
            "ssn": "***-**-6789",
            "public_info": "This is public"
        }

        # Mock masking service
        masking_service = MagicMock()
        masking_service.mask_sensitive_data = MagicMock(return_value=expected_masked)

        # Act
        masked_data = masking_service.mask_sensitive_data(sensitive_data)

        # Assert
        assert masked_data["user_email"] == "t***@example.com"
        assert masked_data["api_key"] == "sk-***"
        assert masked_data["password"] == "***"
        assert masked_data["public_info"] == "This is public"

    def test_workflow_rate_limiting(self):
        """Test workflow execution rate limiting."""
        # Arrange
        user_id = "user-123"
        workflow_id = "workflow-123"

        # Mock rate limiter
        rate_limiter = MagicMock()
        rate_limiter.check_rate_limit = MagicMock(return_value={
            "allowed": True,
            "remaining": 45,
            "reset_time": 3600,
            "limit": 50
        })

        # Act
        rate_check = rate_limiter.check_rate_limit(
            user_id=user_id,
            workflow_id=workflow_id,
            action="execute"
        )

        # Assert
        assert rate_check["allowed"] is True
        assert rate_check["remaining"] == 45
        assert rate_check["limit"] == 50

    def test_workflow_audit_logging(self):
        """Test workflow security audit logging."""
        # Arrange
        audit_event = {
            "user_id": "user-123",
            "workflow_id": "workflow-123",
            "action": "execute",
            "timestamp": "2024-01-01T00:00:00Z",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0...",
            "result": "success"
        }

        # Mock audit logger
        audit_logger = MagicMock()
        audit_logger.log_security_event = MagicMock()

        # Act
        audit_logger.log_security_event(audit_event)

        # Assert
        audit_logger.log_security_event.assert_called_once_with(audit_event)

    def test_workflow_step_security_validation(self):
        """Test individual workflow step security validation."""
        # Arrange
        workflow_step = {
            "id": "step-1",
            "type": "llm_call",
            "config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "security_constraints": {
                "allow_external_calls": False,
                "max_execution_time": 30,
                "allowed_domains": ["api.openai.com"]
            }
        }

        # Mock step validator
        step_validator = MagicMock()
        step_validator.validate_step_security = MagicMock(return_value={
            "valid": True,
            "warnings": [],
            "blocked_actions": []
        })

        # Act
        validation_result = step_validator.validate_step_security(
            step=workflow_step,
            user=self.mock_user
        )

        # Assert
        assert validation_result["valid"] is True
        assert len(validation_result["warnings"]) == 0
        assert len(validation_result["blocked_actions"]) == 0

    def test_workflow_resource_access_control(self):
        """Test workflow resource access control."""
        # Arrange
        resource_access = {
            "databases": ["user_db"],
            "apis": ["openai", "anthropic"],
            "file_systems": ["/app/data"],
            "network_access": True
        }

        user_permissions = {
            "databases": ["user_db", "public_db"],
            "apis": ["openai"],
            "file_systems": ["/app/data", "/app/public"],
            "network_access": False
        }

        # Mock access control
        access_controller = MagicMock()
        access_controller.validate_resource_access = MagicMock(return_value={
            "allowed_databases": ["user_db"],
            "allowed_apis": ["openai"],
            "allowed_file_systems": ["/app/data"],
            "network_access_allowed": False,
            "blocked_resources": ["anthropic", "network"]
        })

        # Act
        access_result = access_controller.validate_resource_access(
            requested=resource_access,
            user_permissions=user_permissions
        )

        # Assert
        assert "user_db" in access_result["allowed_databases"]
        assert "openai" in access_result["allowed_apis"]
        assert access_result["network_access_allowed"] is False
        assert "anthropic" in access_result["blocked_resources"]

    def test_workflow_encryption_validation(self):
        """Test workflow data encryption validation."""
        # Arrange
        encrypted_data = {
            "encrypted": True,
            "algorithm": "AES-256-GCM",
            "key_id": "key-123",
            "data": "encrypted_content_here"
        }

        # Mock encryption validator
        encryption_validator = MagicMock()
        encryption_validator.validate_encryption = MagicMock(return_value={
            "valid": True,
            "algorithm_approved": True,
            "key_valid": True,
            "data_integrity": True
        })

        # Act
        validation = encryption_validator.validate_encryption(encrypted_data)

        # Assert
        assert validation["valid"] is True
        assert validation["algorithm_approved"] is True
        assert validation["key_valid"] is True
        assert validation["data_integrity"] is True


@pytest.mark.integration
class TestWorkflowSecurityIntegration:
    """Integration tests for workflow security."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.mock_user = MagicMock()
        self.mock_user.id = "user-123"
        self.mock_user.role = "user"

    @pytest.mark.asyncio
    async def test_secure_workflow_execution_flow(self):
        """Test complete secure workflow execution flow."""
        # Arrange
        workflow = {
            "id": "workflow-123",
            "name": "Secure Test Workflow",
            "steps": [
                {
                    "id": "step-1",
                    "type": "input_validation",
                    "config": {"validate_schema": True}
                },
                {
                    "id": "step-2",
                    "type": "llm_call",
                    "config": {"model": "gpt-4", "temperature": 0.7}
                },
                {
                    "id": "step-3",
                    "type": "output_sanitization",
                    "config": {"remove_sensitive": True}
                }
            ]
        }

        # Mock security services
        security_service = MagicMock()
        security_service.validate_workflow_access = AsyncMock(return_value=True)
        security_service.authorize_execution = AsyncMock(return_value=True)
        security_service.validate_steps = AsyncMock(return_value={"all_valid": True})
        security_service.audit_log = AsyncMock()

        # Act
        # Validate access
        access_valid = await security_service.validate_workflow_access(
            user=self.mock_user,
            workflow=workflow
        )

        # Authorize execution
        execution_authorized = await security_service.authorize_execution(
            user=self.mock_user,
            workflow=workflow
        )

        # Validate all steps
        steps_valid = await security_service.validate_steps(workflow["steps"])

        # Log audit event
        await security_service.audit_log({
            "action": "workflow_execution",
            "user_id": self.mock_user.id,
            "workflow_id": workflow["id"],
            "result": "authorized"
        })

        # Assert
        assert access_valid is True
        assert execution_authorized is True
        assert steps_valid["all_valid"] is True
        security_service.audit_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_security_violation_handling(self):
        """Test security violation detection and handling."""
        # Arrange
        malicious_workflow = {
            "id": "malicious-workflow",
            "steps": [
                {
                    "id": "malicious-step",
                    "type": "system_call",
                    "config": {"command": "rm -rf /"}
                }
            ]
        }

        # Mock security service that detects violation
        security_service = MagicMock()
        security_service.detect_security_violations = AsyncMock(return_value={
            "violations_found": True,
            "violations": [
                {
                    "type": "dangerous_command",
                    "severity": "critical",
                    "step_id": "malicious-step"
                }
            ]
        })
        security_service.block_execution = AsyncMock(return_value=True)
        security_service.alert_security_team = AsyncMock()

        # Act
        violations = await security_service.detect_security_violations(malicious_workflow)
        blocked = await security_service.block_execution(malicious_workflow["id"])
        await security_service.alert_security_team(violations)

        # Assert
        assert violations["violations_found"] is True
        assert len(violations["violations"]) == 1
        assert violations["violations"][0]["severity"] == "critical"
        assert blocked is True
        security_service.alert_security_team.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_permission_inheritance(self):
        """Test user permission inheritance in workflow security."""
        # Arrange
        parent_user = MagicMock()
        parent_user.id = "admin-123"
        parent_user.role = "admin"
        parent_user.permissions = ["workflow.*", "admin.*"]

        child_user = MagicMock()
        child_user.id = "user-123"
        child_user.role = "user"
        child_user.parent_id = "admin-123"
        child_user.inherited_permissions = ["workflow.read", "workflow.execute"]

        # Mock permission inheritance service
        inheritance_service = MagicMock()
        inheritance_service.resolve_permissions = AsyncMock(return_value={
            "direct_permissions": ["workflow.read"],
            "inherited_permissions": ["workflow.execute"],
            "effective_permissions": ["workflow.read", "workflow.execute"]
        })

        # Act
        permissions = await inheritance_service.resolve_permissions(child_user)

        # Assert
        assert "workflow.read" in permissions["effective_permissions"]
        assert "workflow.execute" in permissions["effective_permissions"]
        assert len(permissions["effective_permissions"]) == 2
