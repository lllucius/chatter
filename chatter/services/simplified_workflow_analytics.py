"""Simplified workflow analytics service.

This provides essential workflow analysis without the complexity
of the original analytics system.
"""

import hashlib
import json
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
        suggestions = self._get_basic_suggestions(nodes, edges)

        # Basic bottleneck detection
        bottlenecks = self._detect_basic_bottlenecks(nodes, edges)

        return {
            "complexity": complexity,
            "suggestions": suggestions,
            "bottlenecks": bottlenecks,
            "analysis_timestamp": None,  # Would use datetime.utcnow() if needed
            "cache_info": {"cached": False, "ttl": 3600},
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

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "node_types": node_types,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
            "cyclomatic_complexity": edge_count
            - node_count
            + 2,  # Basic formula
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
                    "severity": "medium",
                    "message": "Consider breaking down large workflows into smaller components",
                    "category": "structure",
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
                    "severity": "high",
                    "message": "Workflow should have at least one start node",
                    "category": "structure",
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
                    "severity": "low",
                    "message": f"Found {len(disconnected)} disconnected nodes",
                    "category": "structure",
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

        for node_id, count in incoming_counts.items():
            if count > 3:  # More than 3 incoming connections
                bottlenecks.append(
                    {
                        "node_id": node_id,
                        "type": "convergence",
                        "severity": "medium",
                        "description": f"Node has {count} incoming connections",
                        "suggestion": "Consider simplifying node connections",
                    }
                )

        return bottlenecks

    def _get_fallback_analysis(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Get basic fallback analysis when main analysis fails."""
        return {
            "complexity": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "complexity_level": "unknown",
                "complexity_score": 0,
            },
            "suggestions": [],
            "bottlenecks": [],
            "analysis_timestamp": None,
            "cache_info": {"cached": False, "error": True},
        }


# For backwards compatibility with existing code
class WorkflowAnalyticsService(SimplifiedWorkflowAnalyticsService):
    """Alias for backwards compatibility."""

    pass
