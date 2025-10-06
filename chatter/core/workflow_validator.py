"""Unified workflow validation orchestrator.

Phase 5: Validation Unification
This module provides a single orchestrator that consolidates all workflow
validation layers into a clean, sequential pipeline.

Previous state: Validation scattered across 6+ places
- API layer (Pydantic schemas)
- Management service (validate_workflow_definition)
- Core validation module (1,800 lines)
- Graph builder (definition validation)
- Security validator (workflow_security.py)
- Capability checker (workflow_capabilities.py)

New state: Single orchestrated validation pipeline
"""

from typing import Any

from chatter.core.validation import (
    ValidationContext,
    ValidationResult,
    validate_workflow_definition,
)
from chatter.core.workflow_capabilities import WorkflowCapabilityChecker
from chatter.core.workflow_security import WorkflowSecurityManager
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowValidator:
    """Orchestrator for all workflow validation layers.
    
    Consolidates 6+ validation layers into a single, sequential pipeline:
    1. Schema validation (Pydantic) - Already done at API layer
    2. Structure validation (core/validation) - Nodes, edges, structure
    3. Security validation (workflow_security) - Security policies
    4. Capability validation (workflow_capabilities) - Feature support
    5. Resource validation - Limits and quotas
    6. Business logic validation - Workflow-specific rules
    """

    def __init__(
        self,
        security_manager: WorkflowSecurityManager | None = None,
        capability_checker: WorkflowCapabilityChecker | None = None,
    ):
        """Initialize workflow validator.
        
        Args:
            security_manager: Security validation manager (optional)
            capability_checker: Capability validation checker (optional)
        """
        self.security_manager = security_manager or WorkflowSecurityManager()
        self.capability_checker = capability_checker or WorkflowCapabilityChecker()

    async def validate(
        self,
        workflow_data: dict[str, Any],
        user_id: str,
        context: str = "workflow_definition",
        validation_context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Orchestrate all validation layers in sequence.
        
        This is the single entry point for all workflow validation.
        Validates in the following order:
        1. Structure validation (nodes, edges, connectivity)
        2. Security validation (policies, permissions)
        3. Capability validation (features, limits)
        4. Resource validation (quotas, limits)
        
        Args:
            workflow_data: Workflow definition data (nodes, edges, metadata)
            user_id: User ID for ownership validation
            context: Validation context (e.g., "workflow_definition", "template")
            validation_context: Optional validation context for fine-tuning
            
        Returns:
            ValidationResult with all validation results merged
        """
        all_results: list[ValidationResult] = []
        
        # Step 1: Structure validation (core/validation)
        logger.debug(
            "Starting structure validation",
            user_id=user_id,
            context=context,
        )
        
        structure_result = validate_workflow_definition(
            workflow_data,
            validation_context,
        )
        all_results.append(structure_result)
        
        # If structure validation fails critically, stop here
        if not structure_result.is_valid and self._has_critical_errors(structure_result):
            logger.warning(
                "Structure validation failed with critical errors, skipping remaining validations",
                errors=structure_result.errors,
            )
            return structure_result
        
        # Step 2: Security validation
        logger.debug("Starting security validation")
        security_result = await self._validate_security(
            workflow_data,
            user_id,
        )
        all_results.append(security_result)
        
        # Step 3: Capability validation
        logger.debug("Starting capability validation")
        capability_result = await self._validate_capabilities(
            workflow_data,
        )
        all_results.append(capability_result)
        
        # Step 4: Resource validation
        logger.debug("Starting resource validation")
        resource_result = await self._validate_resources(
            workflow_data,
            user_id,
        )
        all_results.append(resource_result)
        
        # Merge all validation results
        final_result = self._merge_results(all_results)
        
        logger.info(
            f"Workflow validation {'passed' if final_result.is_valid else 'failed'}",
            is_valid=final_result.is_valid,
            error_count=len(final_result.errors),
            warning_count=len(final_result.warnings) if hasattr(final_result, 'warnings') else 0,
        )
        
        return final_result

    async def _validate_security(
        self,
        workflow_data: dict[str, Any],
        user_id: str,
    ) -> ValidationResult:
        """Validate security policies and permissions.
        
        Args:
            workflow_data: Workflow definition data
            user_id: User ID
            
        Returns:
            ValidationResult with security validation results
        """
        try:
            # Check security policies
            security_check = await self.security_manager.check_workflow_security(
                workflow_data=workflow_data,
                user_id=user_id,
            )
            
            errors = []
            warnings = []
            
            if not security_check.get("allowed", True):
                errors.append(
                    f"Security policy violation: {security_check.get('reason', 'Unknown reason')}"
                )
            
            # Check for security warnings
            if security_check.get("warnings"):
                warnings.extend(security_check["warnings"])
            
            result = ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
            )
            
            # Add warnings if the result supports them
            if hasattr(result, 'warnings'):
                result.warnings = warnings
            
            return result
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Security validation failed: {str(e)}"],
            )

    async def _validate_capabilities(
        self,
        workflow_data: dict[str, Any],
    ) -> ValidationResult:
        """Validate workflow capabilities and features.
        
        Args:
            workflow_data: Workflow definition data
            
        Returns:
            ValidationResult with capability validation results
        """
        try:
            # Check if workflow uses supported capabilities
            capability_check = await self.capability_checker.check_workflow_capabilities(
                workflow_data=workflow_data,
            )
            
            errors = []
            warnings = []
            
            # Check for unsupported features
            if capability_check.get("unsupported_features"):
                for feature in capability_check["unsupported_features"]:
                    errors.append(f"Unsupported feature: {feature}")
            
            # Check for deprecated features
            if capability_check.get("deprecated_features"):
                for feature in capability_check["deprecated_features"]:
                    warnings.append(f"Deprecated feature: {feature}")
            
            result = ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
            )
            
            if hasattr(result, 'warnings'):
                result.warnings = warnings
            
            return result
            
        except Exception as e:
            logger.error(f"Capability validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Capability validation failed: {str(e)}"],
            )

    async def _validate_resources(
        self,
        workflow_data: dict[str, Any],
        user_id: str,
    ) -> ValidationResult:
        """Validate resource limits and quotas.
        
        Args:
            workflow_data: Workflow definition data
            user_id: User ID
            
        Returns:
            ValidationResult with resource validation results
        """
        try:
            from chatter.core.workflow_limits import WorkflowLimits
            
            limits = WorkflowLimits()
            
            # Check workflow size limits
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            errors = []
            warnings = []
            
            # Validate node count
            if len(nodes) > limits.max_nodes:
                errors.append(
                    f"Too many nodes: {len(nodes)} (max: {limits.max_nodes})"
                )
            elif len(nodes) > limits.max_nodes * 0.8:
                warnings.append(
                    f"Node count approaching limit: {len(nodes)}/{limits.max_nodes}"
                )
            
            # Validate edge count
            if len(edges) > limits.max_edges:
                errors.append(
                    f"Too many edges: {len(edges)} (max: {limits.max_edges})"
                )
            
            # Validate execution time estimates
            estimated_time = self._estimate_execution_time(workflow_data)
            if estimated_time > limits.max_execution_time_seconds:
                errors.append(
                    f"Estimated execution time exceeds limit: {estimated_time}s (max: {limits.max_execution_time_seconds}s)"
                )
            
            result = ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
            )
            
            if hasattr(result, 'warnings'):
                result.warnings = warnings
            
            return result
            
        except Exception as e:
            logger.error(f"Resource validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Resource validation failed: {str(e)}"],
            )

    def _estimate_execution_time(
        self,
        workflow_data: dict[str, Any],
    ) -> int:
        """Estimate workflow execution time in seconds.
        
        Args:
            workflow_data: Workflow definition data
            
        Returns:
            Estimated execution time in seconds
        """
        # Simple estimation based on node count and types
        nodes = workflow_data.get("nodes", [])
        
        total_time = 0
        for node in nodes:
            node_type = node.get("type", "unknown")
            
            # Estimate time based on node type
            if node_type == "model":
                total_time += 10  # LLM calls take ~10s
            elif node_type == "tool":
                total_time += 5   # Tool calls take ~5s
            elif node_type == "conditional":
                total_time += 1   # Conditionals are fast
            else:
                total_time += 2   # Default estimate
        
        return total_time

    def _has_critical_errors(
        self,
        result: ValidationResult,
    ) -> bool:
        """Check if validation result has critical errors.
        
        Critical errors are those that make the workflow unexecutable.
        
        Args:
            result: Validation result
            
        Returns:
            True if result has critical errors
        """
        if not result.errors:
            return False
        
        # Critical error patterns
        critical_patterns = [
            "invalid structure",
            "missing required",
            "circular dependency",
            "unreachable nodes",
            "invalid node type",
        ]
        
        for error in result.errors:
            error_str = str(error).lower()
            if any(pattern in error_str for pattern in critical_patterns):
                return True
        
        return False

    def _merge_results(
        self,
        results: list[ValidationResult],
    ) -> ValidationResult:
        """Merge multiple validation results into one.
        
        Args:
            results: List of validation results
            
        Returns:
            Merged validation result
        """
        all_errors = []
        all_warnings = []
        
        for result in results:
            if result.errors:
                all_errors.extend(result.errors)
            if hasattr(result, 'warnings') and result.warnings:
                all_warnings.extend(result.warnings)
        
        merged = ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
        )
        
        if hasattr(merged, 'warnings'):
            merged.warnings = all_warnings
        
        return merged

    async def validate_template(
        self,
        template_data: dict[str, Any],
        user_id: str,
    ) -> ValidationResult:
        """Validate a workflow template.
        
        Templates have additional validation requirements.
        
        Args:
            template_data: Template data
            user_id: User ID
            
        Returns:
            ValidationResult
        """
        # Validate the workflow structure first
        result = await self.validate(
            workflow_data=template_data,
            user_id=user_id,
            context="template",
        )
        
        # Additional template-specific validations
        if result.is_valid:
            # Check for required template fields
            if not template_data.get("name"):
                result.errors.append("Template name is required")
                result.is_valid = False
            
            if not template_data.get("description"):
                if hasattr(result, 'warnings'):
                    result.warnings.append("Template description is recommended")
        
        return result
