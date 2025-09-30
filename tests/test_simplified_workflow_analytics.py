"""Unit tests for simplified workflow analytics service."""

from unittest.mock import AsyncMock, patch

import pytest

from chatter.services.simplified_workflow_analytics import (
    SimplifiedWorkflowAnalyticsService,
)


class TestSimplifiedWorkflowAnalyticsService:
    """Test cases for SimplifiedWorkflowAnalyticsService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        with patch(
            'chatter.services.simplified_workflow_analytics.get_persistent_cache'
        ) as mock_cache_factory:
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache.set.return_value = None
            mock_cache_factory.return_value = mock_cache

            return SimplifiedWorkflowAnalyticsService()

    @pytest.mark.asyncio
    async def test_empty_workflow_analysis(self, service):
        """Test analysis of empty workflow."""
        result = await service.analyze_workflow([], [])

        # Verify required fields are present
        assert "complexity" in result
        assert "bottlenecks" in result
        assert "optimization_suggestions" in result
        assert "execution_paths" in result
        assert "risk_factors" in result
        assert "total_execution_time_ms" in result
        assert "started_at" in result

        # Verify complexity structure
        complexity = result["complexity"]
        assert "score" in complexity
        assert "depth" in complexity
        assert "branching_factor" in complexity
        assert complexity["node_count"] == 0
        assert complexity["edge_count"] == 0

    @pytest.mark.asyncio
    async def test_simple_workflow_analysis(self, service):
        """Test analysis of simple workflow."""
        nodes = [
            {"id": "1", "data": {"nodeType": "start"}},
            {"id": "2", "data": {"nodeType": "llm"}},
            {"id": "3", "data": {"nodeType": "end"}},
        ]
        edges = [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
        ]

        result = await service.analyze_workflow(nodes, edges)

        # Verify complexity metrics
        complexity = result["complexity"]
        assert complexity["score"] > 0
        assert complexity["node_count"] == 3
        assert complexity["edge_count"] == 2
        assert complexity["depth"] == 3
        assert complexity["branching_factor"] >= 0

        # Should have no risk factors (has start node)
        assert len(result["risk_factors"]) == 0
        assert result["execution_paths"] >= 1

    @pytest.mark.asyncio
    async def test_workflow_without_start_node(self, service):
        """Test analysis of workflow without start node."""
        nodes = [
            {"id": "1", "data": {"nodeType": "llm"}},
            {"id": "2", "data": {"nodeType": "end"}},
        ]
        edges = [
            {"source": "1", "target": "2"},
        ]

        result = await service.analyze_workflow(nodes, edges)

        # Should detect missing start node
        assert "No start node defined" in result["risk_factors"]

        # Should have optimization suggestion
        suggestions = result["optimization_suggestions"]
        assert any(s["type"] == "validation" for s in suggestions)
        assert any(
            "start node" in s["description"] for s in suggestions
        )

    @pytest.mark.asyncio
    async def test_complex_workflow_analysis(self, service):
        """Test analysis of complex workflow."""
        # Create a workflow with many nodes
        nodes = [
            {"id": f"node_{i}", "data": {"nodeType": "llm"}}
            for i in range(25)
        ]
        edges = [
            {"source": f"node_{i}", "target": f"node_{i+1}"}
            for i in range(24)
        ]

        result = await service.analyze_workflow(nodes, edges)

        # Should detect complexity
        assert (
            "High complexity workflow with many nodes"
            in result["risk_factors"]
        )

        # Should have complexity suggestion
        suggestions = result["optimization_suggestions"]
        assert any(s["type"] == "complexity" for s in suggestions)

    @pytest.mark.asyncio
    async def test_workflow_with_bottlenecks(self, service):
        """Test detection of bottlenecks in workflow."""
        nodes = [
            {"id": "1", "data": {"nodeType": "start"}},
            {"id": "2", "data": {"nodeType": "llm"}},
            {"id": "3", "data": {"nodeType": "llm"}},
            {"id": "4", "data": {"nodeType": "llm"}},
            {
                "id": "5",
                "data": {"nodeType": "convergence"},
            },  # This will be a bottleneck
            {"id": "6", "data": {"nodeType": "llm"}},
        ]
        # Multiple edges pointing to node 5 to create a bottleneck (needs > 3)
        edges = [
            {"source": "1", "target": "2"},
            {"source": "1", "target": "3"},
            {"source": "1", "target": "4"},
            {"source": "1", "target": "6"},
            {"source": "2", "target": "5"},
            {"source": "3", "target": "5"},
            {"source": "4", "target": "5"},
            {"source": "6", "target": "5"},  # 4th connection to node 5
        ]

        result = await service.analyze_workflow(nodes, edges)

        # Should detect bottlenecks
        bottlenecks = result["bottlenecks"]
        assert len(bottlenecks) > 0

        # Check bottleneck structure
        bottleneck = bottlenecks[0]
        assert "node_id" in bottleneck
        assert "node_type" in bottleneck
        assert "reason" in bottleneck
        assert "severity" in bottleneck
        assert "suggestions" in bottleneck

    @pytest.mark.asyncio
    async def test_disconnected_nodes(self, service):
        """Test detection of disconnected nodes."""
        nodes = [
            {"id": "1", "data": {"nodeType": "start"}},
            {"id": "2", "data": {"nodeType": "llm"}},
            {
                "id": "3",
                "data": {"nodeType": "isolated"},
            },  # Disconnected
            {
                "id": "4",
                "data": {"nodeType": "isolated"},
            },  # Disconnected
        ]
        edges = [
            {"source": "1", "target": "2"},
        ]

        result = await service.analyze_workflow(nodes, edges)

        # Should detect disconnected nodes
        assert any(
            "disconnected nodes found" in rf
            for rf in result["risk_factors"]
        )

        # Should have connectivity suggestion
        suggestions = result["optimization_suggestions"]
        assert any(s["type"] == "connectivity" for s in suggestions)

    def test_complexity_calculations(self, service):
        """Test complexity calculation methods."""
        nodes = [
            {"id": "1", "data": {"nodeType": "start"}},
            {"id": "2", "data": {"nodeType": "llm"}},
            {"id": "3", "data": {"nodeType": "end"}},
        ]
        edges = [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
        ]

        # Test depth calculation
        depth = service._calculate_max_depth(nodes, edges)
        assert depth == 3

        # Test branching factor
        branching_factor = service._calculate_branching_factor(
            nodes, edges
        )
        assert branching_factor >= 0

        # Test execution paths
        paths = service._calculate_execution_paths(nodes, edges)
        assert paths >= 1

    def test_fallback_analysis(self, service):
        """Test fallback analysis structure."""
        nodes = [{"id": "1", "data": {"nodeType": "test"}}]
        edges = []

        result = service._get_fallback_analysis(nodes, edges)

        # Verify all required fields are present
        required_fields = [
            "complexity",
            "bottlenecks",
            "optimization_suggestions",
            "execution_paths",
            "risk_factors",
            "total_execution_time_ms",
            "started_at",
            "completed_at",
        ]

        for field in required_fields:
            assert field in result

        # Verify complexity structure
        complexity = result["complexity"]
        required_complexity_fields = [
            "score",
            "depth",
            "branching_factor",
        ]
        for field in required_complexity_fields:
            assert field in complexity

    # New tests for cache invalidation fix
    def test_validate_analytics_result_valid(self, service):
        """Test validation with valid analytics result."""
        valid_result = {
            "complexity": {
                "score": 5,
                "node_count": 3,
                "edge_count": 2,
                "depth": 2,
                "branching_factor": 0.67,
                "loop_complexity": 0,
                "conditional_complexity": 0,
            },
            "bottlenecks": [],
            "optimization_suggestions": [],
            "execution_paths": 1,
            "estimated_execution_time_ms": None,
            "risk_factors": ["Low risk workflow"],
            "total_execution_time_ms": 0,
            "error": None,
            "started_at": "2025-01-01T00:00:00Z",
            "completed_at": "2025-01-01T00:00:00Z",
        }

        assert service._validate_analytics_result(valid_result) is True

    def test_validate_analytics_result_missing_top_level_field(
        self, service
    ):
        """Test validation with missing top-level field."""
        invalid_result = {
            "complexity": {
                "score": 5,
                "depth": 2,
                "branching_factor": 0.67,
            },
            "bottlenecks": [],
            "optimization_suggestions": [],
            # Missing execution_paths
            "risk_factors": ["Low risk workflow"],
            "total_execution_time_ms": 0,
            "started_at": "2025-01-01T00:00:00Z",
        }

        assert (
            service._validate_analytics_result(invalid_result) is False
        )

    def test_validate_analytics_result_missing_complexity_field(
        self, service
    ):
        """Test validation with missing complexity field."""
        invalid_result = {
            "complexity": {
                # Missing score
                "node_count": 3,
                "edge_count": 2,
                "depth": 2,
                "branching_factor": 0.67,
            },
            "bottlenecks": [],
            "optimization_suggestions": [],
            "execution_paths": 1,
            "risk_factors": ["Low risk workflow"],
            "total_execution_time_ms": 0,
            "started_at": "2025-01-01T00:00:00Z",
        }

        assert (
            service._validate_analytics_result(invalid_result) is False
        )

    def test_validate_analytics_result_invalid_complexity_type(
        self, service
    ):
        """Test validation with invalid complexity type."""
        invalid_result = {
            "complexity": "invalid",  # Should be dict
            "bottlenecks": [],
            "optimization_suggestions": [],
            "execution_paths": 1,
            "risk_factors": ["Low risk workflow"],
            "total_execution_time_ms": 0,
            "started_at": "2025-01-01T00:00:00Z",
        }

        assert (
            service._validate_analytics_result(invalid_result) is False
        )

    def test_validate_analytics_result_invalid_input_type(
        self, service
    ):
        """Test validation with invalid input type."""
        assert service._validate_analytics_result("invalid") is False
        assert service._validate_analytics_result(None) is False
        assert service._validate_analytics_result([]) is False

    def test_cache_key_versioning(self, service):
        """Test that cache key includes version."""
        nodes = [{"id": "1", "data": {"nodeType": "start"}}]
        edges = [{"source": "1", "target": "2"}]

        cache_key = service._generate_cache_key(nodes, edges)

        # Should include version to invalidate old cache
        assert "workflow_analytics_v2:" in cache_key

    def test_cache_key_fallback_versioning(self, service):
        """Test that cache key fallback also includes version."""
        # Test with empty data that should trigger fallback
        nodes = []  # Empty lists should use simple fallback
        edges = []

        # Mock the json.dumps to raise an exception
        import json

        original_dumps = json.dumps

        def mock_dumps(*args, **kwargs):
            raise ValueError("JSON serialization error")

        # Temporarily replace json.dumps
        json.dumps = mock_dumps

        try:
            cache_key = service._generate_cache_key(nodes, edges)
            # Should include version even in fallback
            assert "workflow_analytics_v2:fallback" in cache_key
        finally:
            # Restore original json.dumps
            json.dumps = original_dumps
