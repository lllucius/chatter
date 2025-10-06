"""Tests for unified workflow validator.

Phase 5: Validation Unification
Tests for the WorkflowValidator orchestrator that consolidates all validation layers.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.core.validation import ValidationResult
from chatter.core.workflow_validator import WorkflowValidator


@pytest.fixture
def sample_workflow():
    """Sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow",
        "nodes": [
            {
                "id": "node1",
                "type": "model",
                "config": {"model": "gpt-4"},
            },
            {
                "id": "node2",
                "type": "tool",
                "config": {"tool": "search"},
            },
        ],
        "edges": [
            {
                "source": "node1",
                "target": "node2",
            },
        ],
        "metadata": {},
    }


@pytest.fixture
def sample_template():
    """Sample template data for testing."""
    return {
        "name": "Test Template",
        "description": "A test template",
        "nodes": [
            {
                "id": "node1",
                "type": "model",
                "config": {"model": "gpt-4"},
            },
        ],
        "edges": [],
        "metadata": {},
    }


class TestWorkflowValidator:
    """Tests for WorkflowValidator class."""

    def test_init(self):
        """Test validator initialization."""
        validator = WorkflowValidator()
        assert validator.security_manager is not None
        assert validator.capability_checker is not None

    def test_init_with_custom_managers(self):
        """Test validator initialization with custom managers."""
        security_manager = MagicMock()
        capability_checker = MagicMock()
        
        validator = WorkflowValidator(
            security_manager=security_manager,
            capability_checker=capability_checker,
        )
        
        assert validator.security_manager == security_manager
        assert validator.capability_checker == capability_checker

    @pytest.mark.asyncio
    async def test_validate_success(self, sample_workflow):
        """Test successful validation."""
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)
            
            validator = WorkflowValidator()
            
            # Mock security and capability checks
            validator.security_manager.check_workflow_security = AsyncMock(
                return_value={"allowed": True}
            )
            validator.capability_checker.check_workflow_capabilities = AsyncMock(
                return_value={}
            )
            
            result = await validator.validate(
                workflow_data=sample_workflow,
                user_id="user123",
            )
            
            assert result.is_valid
            assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_structure_failure(self, sample_workflow):
        """Test validation failure in structure validation."""
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["Invalid structure"],
            )
            
            validator = WorkflowValidator()
            
            result = await validator.validate(
                workflow_data=sample_workflow,
                user_id="user123",
            )
            
            assert not result.is_valid
            assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_validate_security_failure(self, sample_workflow):
        """Test validation failure in security validation."""
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)
            
            validator = WorkflowValidator()
            
            # Mock security check to fail
            validator.security_manager.check_workflow_security = AsyncMock(
                return_value={
                    "allowed": False,
                    "reason": "Security policy violation",
                }
            )
            validator.capability_checker.check_workflow_capabilities = AsyncMock(
                return_value={}
            )
            
            result = await validator.validate(
                workflow_data=sample_workflow,
                user_id="user123",
            )
            
            assert not result.is_valid
            assert any("Security policy violation" in str(e) for e in result.errors)

    @pytest.mark.asyncio
    async def test_validate_capability_failure(self, sample_workflow):
        """Test validation failure in capability validation."""
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)
            
            validator = WorkflowValidator()
            
            validator.security_manager.check_workflow_security = AsyncMock(
                return_value={"allowed": True}
            )
            # Mock capability check to fail
            validator.capability_checker.check_workflow_capabilities = AsyncMock(
                return_value={
                    "unsupported_features": ["advanced_loop"],
                }
            )
            
            result = await validator.validate(
                workflow_data=sample_workflow,
                user_id="user123",
            )
            
            assert not result.is_valid
            assert any("Unsupported feature" in str(e) for e in result.errors)

    @pytest.mark.asyncio
    async def test_validate_resource_failure_too_many_nodes(self):
        """Test validation failure for too many nodes."""
        # Create workflow with many nodes
        large_workflow = {
            "name": "Large Workflow",
            "nodes": [{"id": f"node{i}", "type": "model"} for i in range(200)],
            "edges": [],
        }
        
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)
            
            validator = WorkflowValidator()
            
            validator.security_manager.check_workflow_security = AsyncMock(
                return_value={"allowed": True}
            )
            validator.capability_checker.check_workflow_capabilities = AsyncMock(
                return_value={}
            )
            
            result = await validator.validate(
                workflow_data=large_workflow,
                user_id="user123",
            )
            
            # Should fail due to node count
            assert not result.is_valid
            assert any("Too many nodes" in str(e) for e in result.errors)

    @pytest.mark.asyncio
    async def test_validate_with_warnings(self, sample_workflow):
        """Test validation with warnings."""
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)
            
            validator = WorkflowValidator()
            
            validator.security_manager.check_workflow_security = AsyncMock(
                return_value={
                    "allowed": True,
                    "warnings": ["Consider adding rate limiting"],
                }
            )
            validator.capability_checker.check_workflow_capabilities = AsyncMock(
                return_value={
                    "deprecated_features": ["old_node_type"],
                }
            )
            
            result = await validator.validate(
                workflow_data=sample_workflow,
                user_id="user123",
            )
            
            assert result.is_valid
            assert len(result.warnings) > 0

    @pytest.mark.asyncio
    async def test_validate_template_success(self, sample_template):
        """Test successful template validation."""
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)
            
            validator = WorkflowValidator()
            
            validator.security_manager.check_workflow_security = AsyncMock(
                return_value={"allowed": True}
            )
            validator.capability_checker.check_workflow_capabilities = AsyncMock(
                return_value={}
            )
            
            result = await validator.validate_template(
                template_data=sample_template,
                user_id="user123",
            )
            
            assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_template_missing_name(self):
        """Test template validation with missing name."""
        template_no_name = {
            "description": "A test template",
            "nodes": [],
            "edges": [],
        }
        
        with patch("chatter.core.workflow_validator.validate_workflow_definition") as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)
            
            validator = WorkflowValidator()
            
            validator.security_manager.check_workflow_security = AsyncMock(
                return_value={"allowed": True}
            )
            validator.capability_checker.check_workflow_capabilities = AsyncMock(
                return_value={}
            )
            
            result = await validator.validate_template(
                template_data=template_no_name,
                user_id="user123",
            )
            
            assert not result.is_valid
            assert any("name is required" in str(e).lower() for e in result.errors)

    def test_estimate_execution_time(self, sample_workflow):
        """Test execution time estimation."""
        validator = WorkflowValidator()
        
        estimated_time = validator._estimate_execution_time(sample_workflow)
        
        # Should estimate 10s for model node + 5s for tool node = 15s
        assert estimated_time == 15

    def test_has_critical_errors_true(self):
        """Test critical error detection."""
        validator = WorkflowValidator()
        
        result = ValidationResult(
            is_valid=False,
            errors=["Invalid structure: circular dependency detected"],
        )
        
        assert validator._has_critical_errors(result)

    def test_has_critical_errors_false(self):
        """Test non-critical error detection."""
        validator = WorkflowValidator()
        
        result = ValidationResult(
            is_valid=False,
            errors=["Node name is too long"],
        )
        
        assert not validator._has_critical_errors(result)

    def test_merge_results(self):
        """Test merging multiple validation results."""
        validator = WorkflowValidator()
        
        results = [
            ValidationResult(is_valid=True),
            ValidationResult(
                is_valid=False,
                errors=["Error 1"],
                warnings=["Warning 1"],
            ),
            ValidationResult(
                is_valid=False,
                errors=["Error 2"],
                warnings=["Warning 2"],
            ),
        ]
        
        merged = validator._merge_results(results)
        
        assert not merged.is_valid
        assert len(merged.errors) == 2
        assert len(merged.warnings) == 2


class TestValidationResult:
    """Tests for ValidationResult enhancements."""

    def test_has_errors_true(self):
        """Test has_errors with errors."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1"],
        )
        
        assert result.has_errors()

    def test_has_errors_false(self):
        """Test has_errors without errors."""
        result = ValidationResult(is_valid=True)
        
        assert not result.has_errors()

    def test_has_warnings_true(self):
        """Test has_warnings with warnings."""
        result = ValidationResult(
            is_valid=True,
            warnings=["Warning 1"],
        )
        
        assert result.has_warnings()

    def test_has_warnings_false(self):
        """Test has_warnings without warnings."""
        result = ValidationResult(is_valid=True)
        
        assert not result.has_warnings()

    def test_to_dict(self):
        """Test to_dict conversion."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1"],
            warnings=["Warning 1"],
            metadata={"key": "value"},
        )
        
        data = result.to_dict()
        
        assert data["is_valid"] is False
        assert len(data["errors"]) == 1
        assert len(data["warnings"]) == 1
        assert data["metadata"]["key"] == "value"

    def test_to_api_response(self):
        """Test to_api_response conversion."""
        result = ValidationResult(
            is_valid=True,
            warnings=["Warning 1"],
            metadata={"key": "value"},
        )
        
        response = result.to_api_response()
        
        assert response["valid"] is True
        assert len(response["warnings"]) == 1
        assert response["details"]["key"] == "value"
