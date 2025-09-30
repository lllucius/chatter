"""Simplified workflow analytics service.

This provides essential workflow analysis without the complexity
of the original analytics system.
"""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from chatter.core.workflow_performance import get_workflow_cache
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SimplifiedWorkflowAnalyticsService:
    """Simplified service for basic workflow analysis."""

    def __init__(self, session=None):
        self.session = session
        self.cache = get_workflow_cache().workflow_cache

    async def analyze_workflow(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Perform basic workflow analysis with caching."""
        try:
            # Create cache key from workflow structure
            cache_key = self._generate_cache_key(nodes, edges)

            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                # Validate cached result has required structure
                if self._validate_analytics_result(cached_result):
                    logger.debug("Returning cached workflow analytics")
                    return cached_result
                else:
                    logger.warning(
                        "Cached result has invalid structure, regenerating"
                    )

            # Perform basic analysis
            analysis = self._perform_basic_analysis(nodes, edges)

            # Cache the result for future use
            await self.cache.set(
                cache_key, analysis, ttl=3600
            )  # 1 hour TTL

            return analysis

        except Exception as e:
            logger.error(f"Workflow analysis failed: {e}")
            # Return basic fallback analysis
            return self._get_fallback_analysis(nodes, edges)

    def _generate_cache_key(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> str:
        """Generate cache key from workflow structure."""
        try:
            # Create deterministic hash from nodes and edges
            workflow_data = {
                "nodes": sorted(nodes, key=lambda x: x.get("id", "")),
                "edges": sorted(edges, key=lambda x: x.get("id", "")),
            }
            content = json.dumps(workflow_data, sort_keys=True)
            # Include schema version to invalidate old cached data
            return f"workflow_analytics_v2:{hashlib.md5(content.encode()).hexdigest()}"
        except Exception:
            # Fallback to simple hash
            return f"workflow_analytics_v2:fallback_{len(nodes)}_{len(edges)}"

    def _perform_basic_analysis(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Perform basic workflow analysis."""
        # Basic complexity metrics
        complexity = self._calculate_basic_complexity(nodes, edges)

        # Simple suggestions
        suggestions = self._get_basic_suggestions(nodes, edges)

        # Basic bottleneck detection
        bottlenecks = self._detect_basic_bottlenecks(nodes, edges)

        # Calculate execution paths (simplified)
        execution_paths = self._calculate_execution_paths(nodes, edges)

        # Generate risk factors
        risk_factors = self._get_risk_factors(nodes, edges)

        # Get current timestamp for execution tracking
        now = datetime.now(UTC)

        return {
            "complexity": complexity,
            "bottlenecks": bottlenecks,
            "optimization_suggestions": suggestions,
            "execution_paths": execution_paths,
            "estimated_execution_time_ms": None,
            "risk_factors": risk_factors,
            "total_execution_time_ms": 0,  # This is analysis time, not workflow execution
            "error": None,
            "started_at": now,
            "completed_at": now,
        }

    def _calculate_basic_complexity(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate basic complexity metrics."""
        node_count = len(nodes)
        edge_count = len(edges)

        # Count different node types
        node_types = {}
        for node in nodes:
            node_type = node.get("data", {}).get("nodeType", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

        # Simple complexity scoring
        complexity_score = node_count + (edge_count * 0.5)
        if complexity_score < 5:
            complexity_level = "low"
        elif complexity_score < 15:
            complexity_level = "medium"
        else:
            complexity_level = "high"

        # Calculate depth (maximum path length)
        depth = self._calculate_max_depth(nodes, edges)

        # Calculate branching factor
        branching_factor = self._calculate_branching_factor(
            nodes, edges
        )

        return {
            "score": int(complexity_score),  # Required field for schema
            "node_count": node_count,
            "edge_count": edge_count,
            "depth": depth,  # Required field for schema
            "branching_factor": branching_factor,  # Required field for schema
            "loop_complexity": 0,  # Default value
            "conditional_complexity": max(
                0, edge_count - node_count + 2
            ),  # Basic formula
        }

    def _get_basic_suggestions(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Get basic optimization suggestions."""
        suggestions = []

        # Too many nodes
        if len(nodes) > 20:
            suggestions.append(
                {
                    "type": "complexity",
                    "description": "Consider breaking down large workflows into smaller components",
                    "impact": "medium",
                    "node_ids": None,
                }
            )

        # No start node
        start_nodes = [
            n
            for n in nodes
            if n.get("data", {}).get("nodeType") == "start"
        ]
        if not start_nodes:
            suggestions.append(
                {
                    "type": "validation",
                    "description": "Workflow should have at least one start node",
                    "impact": "high",
                    "node_ids": None,
                }
            )

        # Disconnected nodes
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge.get("source"))
            connected_nodes.add(edge.get("target"))

        disconnected = [
            n for n in nodes if n.get("id") not in connected_nodes
        ]
        if disconnected and len(disconnected) > 1:
            disconnected_ids = [n.get("id") for n in disconnected]
            suggestions.append(
                {
                    "type": "connectivity",
                    "description": f"Found {len(disconnected)} disconnected nodes",
                    "impact": "medium",
                    "node_ids": disconnected_ids,
                }
            )

        return suggestions

    def _detect_basic_bottlenecks(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Detect basic bottlenecks in the workflow."""
        bottlenecks = []

        # Nodes with many incoming connections
        incoming_counts = {}
        for edge in edges:
            target = edge.get("target")
            if target:
                incoming_counts[target] = (
                    incoming_counts.get(target, 0) + 1
                )

        # Flag nodes with high incoming connections as bottlenecks
        for node_id, count in incoming_counts.items():
            if count > 3:  # Threshold for bottleneck
                # Find the actual node to get more info
                node = next(
                    (n for n in nodes if n.get("id") == node_id), None
                )
                node_type = (
                    node.get("data", {}).get("nodeType", "unknown")
                    if node
                    else "unknown"
                )

                bottlenecks.append(
                    {
                        "node_id": node_id,
                        "node_type": node_type,
                        "reason": f"Node has {count} incoming connections",
                        "severity": "medium",
                        "suggestions": [
                            "Consider simplifying node connections"
                        ],
                    }
                )

        return bottlenecks

    def _calculate_max_depth(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> int:
        """Calculate maximum depth of the workflow."""
        if not nodes or not edges:
            return len(nodes)  # If no edges, depth equals node count

        # Build adjacency list
        adjacency = {}
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                if source not in adjacency:
                    adjacency[source] = []
                adjacency[source].append(target)

        # Find start nodes (nodes with no incoming edges)
        all_nodes = {n.get("id") for n in nodes}
        targets = {edge.get("target") for edge in edges}
        start_nodes = all_nodes - targets

        if not start_nodes:
            return 1  # Circular or no clear start

        # DFS to find maximum depth
        def dfs(node, visited):
            if node in visited:
                return 0  # Avoid cycles
            visited.add(node)
            max_child_depth = 0
            for neighbor in adjacency.get(node, []):
                max_child_depth = max(
                    max_child_depth, dfs(neighbor, visited.copy())
                )
            return 1 + max_child_depth

        max_depth = 0
        for start_node in start_nodes:
            depth = dfs(start_node, set())
            max_depth = max(max_depth, depth)

        return max_depth

    def _calculate_branching_factor(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> float:
        """Calculate average branching factor."""
        if not nodes or not edges:
            return 0.0

        # Count outgoing edges for each node
        outgoing_counts = {}
        for edge in edges:
            source = edge.get("source")
            if source:
                outgoing_counts[source] = (
                    outgoing_counts.get(source, 0) + 1
                )

        if not outgoing_counts:
            return 0.0

        # Calculate average
        total_outgoing = sum(outgoing_counts.values())
        return round(total_outgoing / len(nodes), 2)

    def _calculate_execution_paths(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> int:
        """Calculate approximate number of execution paths."""
        if not nodes:
            return 0
        if not edges:
            return 1

        # Simple estimation based on branching nodes
        branching_nodes = 0
        outgoing_counts = {}
        for edge in edges:
            source = edge.get("source")
            if source:
                outgoing_counts[source] = (
                    outgoing_counts.get(source, 0) + 1
                )

        for count in outgoing_counts.values():
            if count > 1:
                branching_nodes += (
                    count - 1
                )  # Each additional branch adds paths

        return max(
            1, 2 ** min(branching_nodes, 10)
        )  # Cap to prevent overflow

    def _get_risk_factors(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> list[str]:
        """Identify risk factors in the workflow."""
        risk_factors = []

        # Check for complex workflow
        if len(nodes) > 15:
            risk_factors.append(
                "High complexity workflow with many nodes"
            )

        # Check for missing start nodes
        start_nodes = [
            n
            for n in nodes
            if n.get("data", {}).get("nodeType") == "start"
        ]
        if not start_nodes:
            risk_factors.append("No start node defined")

        # Check for disconnected nodes
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge.get("source"))
            connected_nodes.add(edge.get("target"))

        disconnected = [
            n for n in nodes if n.get("id") not in connected_nodes
        ]
        if disconnected:
            risk_factors.append(
                f"{len(disconnected)} disconnected nodes found"
            )

        # Check for potential bottlenecks
        incoming_counts = {}
        for edge in edges:
            target = edge.get("target")
            if target:
                incoming_counts[target] = (
                    incoming_counts.get(target, 0) + 1
                )

        high_convergence = [
            node_id
            for node_id, count in incoming_counts.items()
            if count > 3
        ]
        if high_convergence:
            risk_factors.append(
                f"{len(high_convergence)} potential bottleneck nodes"
            )

        return risk_factors

    def _validate_analytics_result(
        self, result: dict[str, Any]
    ) -> bool:
        """Validate that analytics result has the required structure."""
        if not isinstance(result, dict):
            return False

        # Check required top-level fields
        required_top_fields = [
            "complexity",
            "bottlenecks",
            "optimization_suggestions",
            "execution_paths",
            "risk_factors",
            "total_execution_time_ms",
            "started_at",
        ]

        for field in required_top_fields:
            if field not in result:
                return False

        # Check complexity structure
        complexity = result.get("complexity", {})
        if not isinstance(complexity, dict):
            return False

        required_complexity_fields = [
            "score",
            "depth",
            "branching_factor",
        ]
        for field in required_complexity_fields:
            if field not in complexity:
                return False

        return True

    def _get_fallback_analysis(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Get basic fallback analysis when main analysis fails."""
        now = datetime.now(UTC)

        return {
            "complexity": {
                "score": 0,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "depth": 1,
                "branching_factor": 0.0,
                "loop_complexity": 0,
                "conditional_complexity": 0,
            },
            "bottlenecks": [],
            "optimization_suggestions": [],
            "execution_paths": 1,
            "estimated_execution_time_ms": None,
            "risk_factors": ["Analysis failed - using fallback data"],
            "total_execution_time_ms": 0,
            "error": None,
            "started_at": now,
            "completed_at": now,
        }
