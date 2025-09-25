"""Simplified workflow analytics service.

This provides essential workflow analysis without the complexity
of the original analytics system.
"""

import hashlib
import json
from datetime import datetime, UTC
from typing import Any

from chatter.core.cache_factory import get_persistent_cache
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SimplifiedWorkflowAnalyticsService:
    """Simplified service for basic workflow analysis."""

    def __init__(self, session=None):
        self.session = session
        self.cache = get_persistent_cache()

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
                logger.debug("Returning cached workflow analytics")
                return cached_result

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
            return f"workflow_analytics:{hashlib.md5(content.encode()).hexdigest()}"
        except Exception:
            # Fallback to simple hash
            return (
                f"workflow_analytics:fallback_{len(nodes)}_{len(edges)}"
            )

    def _perform_basic_analysis(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Perform basic workflow analysis."""
        # Basic complexity metrics
        complexity = self._calculate_basic_complexity(nodes, edges)

        # Simple suggestions
        optimization_suggestions = self._get_basic_suggestions(nodes, edges)

        # Basic bottleneck detection
        bottlenecks = self._detect_basic_bottlenecks(nodes, edges)

        # Calculate execution paths (simplified)
        execution_paths = max(1, len(edges) + 1)

        # Basic risk factors
        risk_factors = []
        if len(nodes) > 15:
            risk_factors.append("High node count may impact performance")
        if complexity["depth"] > 8:
            risk_factors.append("Deep workflow may be difficult to debug")
        if not any(n.get("data", {}).get("nodeType") == "start" for n in nodes):
            risk_factors.append("Missing start node")

        return {
            "complexity": complexity,
            "bottlenecks": bottlenecks,
            "optimization_suggestions": optimization_suggestions,
            "execution_paths": execution_paths,
            "estimated_execution_time_ms": None,
            "risk_factors": risk_factors,
            "total_execution_time_ms": 0,  # Default for analytics (not execution)
            "error": None,
            "started_at": datetime.now(UTC),
            "completed_at": None,
        }

    def _calculate_basic_complexity(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate basic complexity metrics."""
        node_count = len(nodes)
        edge_count = len(edges)

        # Calculate maximum path depth (simplified)
        depth = self._calculate_max_depth(nodes, edges)

        # Calculate average branching factor
        branching_factor = self._calculate_branching_factor(nodes, edges)

        # Simple complexity scoring
        complexity_score = int(node_count + (edge_count * 0.5) + (depth * 2))

        return {
            "score": complexity_score,
            "node_count": node_count,
            "edge_count": edge_count,
            "depth": depth,
            "branching_factor": branching_factor,
            "loop_complexity": 0,  # Default for simplified analytics
            "conditional_complexity": 0,  # Default for simplified analytics
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
            suggestions.append(
                {
                    "type": "optimization",
                    "description": f"Found {len(disconnected)} disconnected nodes",
                    "impact": "low",
                }
            )

        return suggestions

    def _calculate_max_depth(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> int:
        """Calculate maximum path depth in the workflow."""
        if not nodes:
            return 0

        # Find start nodes
        start_nodes = [
            n["id"]
            for n in nodes
            if n.get("data", {}).get("nodeType") == "start"
        ]
        
        if not start_nodes:
            # If no start nodes, return basic depth estimation
            return min(len(nodes), 10)

        # Build adjacency list
        graph = {}
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                if source not in graph:
                    graph[source] = []
                graph[source].append(target)

        # Calculate maximum depth from start nodes
        max_depth = 0
        for start_node in start_nodes:
            depth = self._dfs_depth(start_node, graph, set())
            max_depth = max(max_depth, depth)

        return max_depth

    def _dfs_depth(self, node: str, graph: dict, visited: set) -> int:
        """Calculate depth using DFS (with cycle detection)."""
        if node in visited:
            return 0  # Avoid infinite loops
        
        visited.add(node)
        max_child_depth = 0
        
        for neighbor in graph.get(node, []):
            child_depth = self._dfs_depth(neighbor, graph, visited.copy())
            max_child_depth = max(max_child_depth, child_depth)
        
        return 1 + max_child_depth

    def _calculate_branching_factor(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> float:
        """Calculate average branching factor."""
        if not nodes:
            return 0.0

        # Count outgoing edges for each node
        outgoing_counts = {}
        for edge in edges:
            source = edge.get("source")
            if source:
                outgoing_counts[source] = outgoing_counts.get(source, 0) + 1

        # Calculate average branching factor
        total_branching = sum(outgoing_counts.values())
        nodes_with_outgoing = len(outgoing_counts) or 1
        
        return round(total_branching / nodes_with_outgoing, 2)

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

        # Find node details
        node_details = {node.get("id"): node for node in nodes}

        for node_id, count in incoming_counts.items():
            if count > 3:  # More than 3 incoming connections
                node = node_details.get(node_id, {})
                node_type = node.get("data", {}).get("nodeType", "unknown")
                
                bottlenecks.append(
                    {
                        "node_id": node_id,
                        "node_type": node_type,
                        "reason": f"Node has {count} incoming connections",
                        "severity": "medium",
                        "suggestions": ["Consider simplifying node connections"],
                    }
                )

        return bottlenecks

    def _get_fallback_analysis(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Get basic fallback analysis when main analysis fails."""
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
            "risk_factors": ["Analysis failed - unable to assess risks"],
            "total_execution_time_ms": 0,
            "error": None,
            "started_at": datetime.now(UTC),
            "completed_at": None,
        }
