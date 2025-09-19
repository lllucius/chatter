"""Simplified workflow validation service.

This consolidates the validation logic into a more straightforward
implementation that focuses on the essential validations needed.
"""

from typing import Any

from chatter.models.workflow import WorkflowTemplate
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ValidationResult:
    """Simplified validation result."""

    def __init__(
        self,
        is_valid: bool,
        errors: list[str],
        warnings: list[str],
        requirements_met: bool = True,
    ):
        self.is_valid = is_valid
        self.valid = is_valid  # Alias for compatibility
        self.errors = errors
        self.warnings = warnings
        self.requirements_met = requirements_met


class SimplifiedWorkflowValidationService:
    """Simplified workflow validation service."""

    def validate_workflow_definition(
        self,
        definition: dict[str, Any],
        owner_id: str | None = None,
    ) -> ValidationResult:
        """Validate a workflow definition structure."""
        errors = []
        warnings = []

        # Basic structure validation
        required_fields = ["name", "nodes", "edges"]
        for field in required_fields:
            if field not in definition or not definition[field]:
                errors.append(f"Missing required field: {field}")

        # Validate name
        if "name" in definition:
            name = definition["name"]
            if not isinstance(name, str) or len(name.strip()) == 0:
                errors.append(
                    "Workflow name must be a non-empty string"
                )
            elif len(name) > 255:
                errors.append(
                    "Workflow name must be 255 characters or less"
                )

        # Validate nodes
        if "nodes" in definition and isinstance(
            definition["nodes"], list
        ):
            if len(definition["nodes"]) == 0:
                warnings.append("Workflow has no nodes")
            else:
                node_errors, node_warnings = self._validate_nodes(
                    definition["nodes"]
                )
                errors.extend(node_errors)
                warnings.extend(node_warnings)

        # Validate edges
        if "edges" in definition and isinstance(
            definition["edges"], list
        ):
            edge_errors, edge_warnings = self._validate_edges(
                definition["edges"], definition.get("nodes", [])
            )
            errors.extend(edge_errors)
            warnings.extend(edge_warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_workflow_template(
        self, template: WorkflowTemplate
    ) -> ValidationResult:
        """Validate a workflow template."""
        errors = []
        warnings = []

        # Check required fields
        if not template.name or len(template.name.strip()) == 0:
            errors.append("Template name is required")

        if not template.workflow_type:
            errors.append("Workflow type is required")
        elif not isinstance(template.workflow_type, str) or len(template.workflow_type.strip()) == 0:
            errors.append("Invalid workflow type: must be a non-empty string")

        if not template.description:
            warnings.append("Template description is empty")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _validate_nodes(
        self, nodes: list[dict[str, Any]]
    ) -> tuple[list[str], list[str]]:
        """Validate workflow nodes."""
        errors = []
        warnings = []

        if not nodes:
            return errors, warnings

        node_ids = set()
        node_types = set()
        valid_node_types = {
            "start",
            "model",
            "tool",
            "memory",
            "retrieval",
            "conditional",
            "loop",
            "variable",
            "errorHandler",
            "delay",
        }

        for i, node in enumerate(nodes):
            # Check required fields
            if "id" not in node:
                errors.append(f"Node {i} missing required field: id")
            elif node["id"] in node_ids:
                errors.append(f"Duplicate node ID: {node['id']}")
            else:
                node_ids.add(node["id"])

            if "type" not in node:
                errors.append(
                    f"Node {node.get('id', i)} missing required field: type"
                )
            elif node["type"] not in valid_node_types:
                warnings.append(f"Unknown node type: {node['type']}")
            else:
                node_types.add(node["type"])

        # Check for start node
        if "start" not in node_types:
            warnings.append(
                "Workflow should have at least one start node"
            )

        return errors, warnings

    def _validate_edges(
        self, edges: list[dict[str, Any]], nodes: list[dict[str, Any]]
    ) -> tuple[list[str], list[str]]:
        """Validate workflow edges."""
        errors = []
        warnings = []

        if not edges or not nodes:
            return errors, warnings

        node_ids = {node.get("id") for node in nodes if "id" in node}

        for i, edge in enumerate(edges):
            # Check required fields
            required_fields = ["id", "source", "target"]
            for field in required_fields:
                if field not in edge:
                    errors.append(
                        f"Edge {i} missing required field: {field}"
                    )

            # Check if source and target nodes exist
            if "source" in edge and edge["source"] not in node_ids:
                errors.append(
                    f"Edge {edge.get('id', i)} references non-existent source node: {edge['source']}"
                )

            if "target" in edge and edge["target"] not in node_ids:
                errors.append(
                    f"Edge {edge.get('id', i)} references non-existent target node: {edge['target']}"
                )

        return errors, warnings


# Create singleton instance
simplified_workflow_validation_service = (
    SimplifiedWorkflowValidationService()
)
