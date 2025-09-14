"""Centralized workflow validation service to eliminate duplication."""

from typing import Any

# Import validation classes with fallback handling
try:
    from chatter.core.validation.exceptions import (
        ValidationError as _ValidationError,
    )
    from chatter.core.validation.results import (
        ValidationResult as _ValidationResult,
    )

    _HAS_REAL_VALIDATION = True
except ImportError:
    _HAS_REAL_VALIDATION = False
    # Type hints for fallback - actual classes created at module level
    _ValidationResult = None  # type: ignore
    _ValidationError = None  # type: ignore


class _FallbackValidationResult:
    """Fallback validation result for environments without full validation engine."""

    def __init__(
        self,
        valid: bool,
        errors: list[str],
        warnings: list[str],
        requirements_met: bool = True,
    ):
        self.valid = valid
        self.errors = errors
        self.warnings = warnings
        self.requirements_met = requirements_met


class _FallbackValidationError(Exception):
    """Fallback validation error."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# Set up the classes to use
if _HAS_REAL_VALIDATION:
    ValidationResult = _ValidationResult
    ValidationError = _ValidationError
else:
    ValidationResult = _FallbackValidationResult  # type: ignore
    ValidationError = _FallbackValidationError  # type: ignore


# Use standard logging to avoid config dependencies
from chatter.models.workflow import (  # noqa: E402
    WorkflowDefinition,
    WorkflowTemplate,
    WorkflowType,
)
from chatter.utils.logging import get_logger  # noqa: E402

logger = get_logger(__name__)


def _create_validation_result(errors: list[str], warnings: list[str]) -> ValidationResult:  # type: ignore
    """Create ValidationResult using the appropriate interface."""
    if _HAS_REAL_VALIDATION:
        # Convert string errors to ValidationError objects
        error_objects = [_ValidationError(msg) for msg in errors]
        return _ValidationResult(
            is_valid=len(errors) == 0,
            errors=error_objects,
            warnings=warnings,
        )
    else:
        # Use fallback interface with string errors
        return _FallbackValidationResult(  # type: ignore
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            requirements_met=True,
        )


class WorkflowValidationService:
    """Centralized service for workflow validation to eliminate duplication."""

    def __init__(self) -> None:
        # Note: ValidationEngine is optional to avoid config dependencies
        self.validation_engine = None
        try:
            from chatter.core.validation.engine import ValidationEngine

            self.validation_engine = ValidationEngine()
        except ImportError:
            logger.info(
                "ValidationEngine not available - using basic validation"
            )

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
                errors.append(
                    f"Workflow definition missing required field: {field}"
                )

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
        if "nodes" in definition:
            nodes = definition["nodes"]
            if not isinstance(nodes, list):
                errors.append("Nodes must be a list")
            elif len(nodes) == 0:
                warnings.append("Workflow has no nodes")
            else:
                node_validation = self._validate_nodes(nodes)
                errors.extend(node_validation.get("errors", []))
                warnings.extend(node_validation.get("warnings", []))

        # Validate edges
        if "edges" in definition:
            edges = definition["edges"]
            if not isinstance(edges, list):
                errors.append("Edges must be a list")
            else:
                edge_validation = self._validate_edges(
                    edges, definition.get("nodes", [])
                )
                errors.extend(edge_validation.get("errors", []))
                warnings.extend(edge_validation.get("warnings", []))

        # Validate workflow structure (connectivity, cycles, etc.)
        if "nodes" in definition and "edges" in definition:
            structure_validation = self._validate_workflow_structure(
                definition["nodes"], definition["edges"]
            )
            errors.extend(structure_validation.get("errors", []))
            warnings.extend(structure_validation.get("warnings", []))

        return _create_validation_result(errors, warnings)

    def validate_workflow_template(
        self,
        template: WorkflowTemplate,
    ) -> ValidationResult:
        """Validate a workflow template."""
        errors = []
        warnings = []

        # Check required fields
        if not template.name:
            errors.append("Template name is required")
        elif len(template.name.strip()) == 0:
            errors.append("Template name cannot be empty")

        if not template.workflow_type:
            errors.append("Workflow type is required")
        elif template.workflow_type not in [
            t.value for t in WorkflowType
        ]:
            errors.append(
                f"Invalid workflow type: {template.workflow_type}"
            )

        if not template.description:
            warnings.append("Template description is empty")

        # Validate parameters
        if template.default_params:
            param_validation = self._validate_template_params(
                template.default_params
            )
            errors.extend(param_validation.get("errors", []))
            warnings.extend(param_validation.get("warnings", []))

        return _create_validation_result(errors, warnings)

    def validate_execution_request(
        self,
        request: dict[str, Any],
        definition: WorkflowDefinition,
    ) -> ValidationResult:
        """Validate a workflow execution request."""
        errors: list[str] = []
        warnings: list[str] = []

        # Validate input data structure
        if "input_data" in request:
            input_data = request["input_data"]
            if not isinstance(input_data, dict):
                errors.append("Input data must be a dictionary")

        # Check if workflow has required inputs
        start_nodes = [
            node
            for node in definition.nodes
            if node.get("type") == "start"
        ]
        if not start_nodes:
            errors.append("Workflow has no start node - cannot execute")

        return _create_validation_result(errors, warnings)

    def _validate_nodes(
        self, nodes: list[dict[str, Any]]
    ) -> dict[str, list[str]]:
        """Validate workflow nodes."""
        errors = []
        warnings = []

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
                errors.append(f"Invalid node type: {node['type']}")
            else:
                node_types.add(node["type"])

            if "data" not in node:
                errors.append(
                    f"Node {node.get('id', i)} missing required field: data"
                )
            elif not isinstance(node["data"], dict):
                errors.append(
                    f"Node {node.get('id', i)} data must be a dictionary"
                )

        # Check for start node
        if "start" not in node_types:
            errors.append("Workflow must have at least one start node")

        return {"errors": errors, "warnings": warnings}

    def _validate_edges(
        self, edges: list[dict[str, Any]], nodes: list[dict[str, Any]]
    ) -> dict[str, list[str]]:
        """Validate workflow edges."""
        errors = []
        warnings = []

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

        return {"errors": errors, "warnings": warnings}

    def _validate_workflow_structure(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, list[str]]:
        """Validate overall workflow structure."""
        errors = []
        warnings = []

        # Build adjacency list for graph analysis
        graph = {}
        node_ids = {node["id"] for node in nodes}

        for node_id in node_ids:
            graph[node_id] = []

        for edge in edges:
            if edge.get("source") and edge.get("target"):
                graph[edge["source"]].append(edge["target"])

        # Check for orphaned nodes (nodes with no connections)
        orphaned_nodes = []
        for node in nodes:
            node_id = node["id"]
            has_incoming = any(
                node_id in targets for targets in graph.values()
            )
            has_outgoing = len(graph[node_id]) > 0

            if (
                not has_incoming
                and not has_outgoing
                and node.get("type") != "start"
            ):
                orphaned_nodes.append(node_id)

        if orphaned_nodes:
            warnings.append(
                f"Orphaned nodes found (no connections): {', '.join(orphaned_nodes)}"
            )

        # Check for unreachable nodes
        start_nodes = [
            node["id"] for node in nodes if node.get("type") == "start"
        ]
        if start_nodes:
            reachable = self._find_reachable_nodes(graph, start_nodes)
            unreachable = node_ids - reachable
            if unreachable:
                warnings.append(
                    f"Unreachable nodes found: {', '.join(unreachable)}"
                )

        return {"errors": errors, "warnings": warnings}

    def _validate_template_params(
        self, params: dict[str, Any]
    ) -> dict[str, list[str]]:
        """Validate template parameters."""
        errors = []
        warnings = []

        # Check common parameter types
        if "max_tool_calls" in params:
            max_calls = params["max_tool_calls"]
            if not isinstance(max_calls, int) or max_calls <= 0:
                errors.append(
                    "max_tool_calls must be a positive integer"
                )

        if "temperature" in params:
            temp = params["temperature"]
            if (
                not isinstance(temp, int | float)
                or temp < 0
                or temp > 2
            ):
                errors.append(
                    "temperature must be a number between 0 and 2"
                )

        if "max_tokens" in params:
            tokens = params["max_tokens"]
            if not isinstance(tokens, int) or tokens <= 0:
                errors.append("max_tokens must be a positive integer")

        if "system_message" not in params:
            warnings.append(
                "No system message specified in template parameters"
            )

        return {"errors": errors, "warnings": warnings}

    def _find_reachable_nodes(
        self, graph: dict[str, list[str]], start_nodes: list[str]
    ) -> set:
        """Find all nodes reachable from start nodes using DFS."""
        reachable = set()
        stack = list(start_nodes)

        while stack:
            node = stack.pop()
            if node not in reachable:
                reachable.add(node)
                stack.extend(graph.get(node, []))

        return reachable


# Create singleton instance
workflow_validation_service = WorkflowValidationService()
