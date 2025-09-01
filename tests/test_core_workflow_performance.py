"""Tests for workflow performance optimization utilities."""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.core.workflow_performance import (
    WorkflowCache,
    LazyToolLoader,
    PerformanceMonitor,
    WorkflowOptimizer,
    BatchProcessor,
    AsyncWorkflowPool
)


@pytest.mark.unit
class TestWorkflowCache:
    """Test WorkflowCache functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache = WorkflowCache(max_size=3)

    def test_cache_initialization(self):
        """Test WorkflowCache initialization."""
        # Assert
        assert self.cache.max_size == 3
        assert len(self.cache.cache) == 0
        assert len(self.cache.access_times) == 0
        assert self.cache.cache_hits == 0
        assert self.cache.cache_misses == 0

    def test_generate_cache_key_consistent(self):
        """Test cache key generation is consistent."""
        # Arrange
        provider = "openai"
        workflow_type = "full"
        config = {"temperature": 0.7, "max_tokens": 1000}
        
        # Act
        key1 = self.cache._generate_cache_key(provider, workflow_type, config)
        key2 = self.cache._generate_cache_key(provider, workflow_type, config)
        
        # Assert
        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) == 32  # MD5 hash length

    def test_generate_cache_key_different_configs(self):
        """Test cache key generation for different configurations."""
        # Arrange
        provider = "openai"
        workflow_type = "full"
        config1 = {"temperature": 0.7}
        config2 = {"temperature": 0.8}
        
        # Act
        key1 = self.cache._generate_cache_key(provider, workflow_type, config1)
        key2 = self.cache._generate_cache_key(provider, workflow_type, config2)
        
        # Assert
        assert key1 != key2

    def test_generate_cache_key_order_independence(self):
        """Test cache key generation is order-independent for config dict."""
        # Arrange
        provider = "openai"
        workflow_type = "full"
        config1 = {"temperature": 0.7, "max_tokens": 1000}
        config2 = {"max_tokens": 1000, "temperature": 0.7}
        
        # Act
        key1 = self.cache._generate_cache_key(provider, workflow_type, config1)
        key2 = self.cache._generate_cache_key(provider, workflow_type, config2)
        
        # Assert
        assert key1 == key2

    def test_cache_miss_on_empty_cache(self):
        """Test cache miss when cache is empty."""
        # Act
        result = self.cache.get("openai", "full", {"temperature": 0.7})
        
        # Assert
        assert result is None
        assert self.cache.cache_misses == 1
        assert self.cache.cache_hits == 0

    def test_cache_put_and_get(self):
        """Test putting and getting items from cache."""
        # Arrange
        provider = "openai"
        workflow_type = "full"
        config = {"temperature": 0.7}
        mock_workflow = MagicMock()
        
        # Act
        self.cache.put(provider, workflow_type, config, mock_workflow)
        result = self.cache.get(provider, workflow_type, config)
        
        # Assert
        assert result == mock_workflow
        assert self.cache.cache_hits == 1
        assert self.cache.cache_misses == 0

    def test_cache_eviction_lru(self):
        """Test LRU cache eviction when max size exceeded."""
        # Arrange
        workflows = [MagicMock() for _ in range(4)]
        configs = [{"temp": i * 0.1} for i in range(4)]
        
        # Act - Fill cache beyond max size
        for i, (config, workflow) in enumerate(zip(configs, workflows)):
            self.cache.put("openai", "full", config, workflow)
            if i < 3:  # First 3 should fit
                assert len(self.cache.cache) == i + 1
            else:  # 4th should trigger eviction
                assert len(self.cache.cache) == 3
        
        # Assert - Least recently used item should be evicted
        # First item should be evicted, others should remain
        assert self.cache.get("openai", "full", configs[0]) is None  # Evicted
        assert self.cache.get("openai", "full", configs[1]) == workflows[1]
        assert self.cache.get("openai", "full", configs[2]) == workflows[2]
        assert self.cache.get("openai", "full", configs[3]) == workflows[3]

    def test_cache_access_time_update(self):
        """Test that cache access updates access time."""
        # Arrange
        provider = "openai"
        workflow_type = "full"
        config = {"temperature": 0.7}
        mock_workflow = MagicMock()
        
        self.cache.put(provider, workflow_type, config, mock_workflow)
        
        # Get initial access time
        cache_key = self.cache._generate_cache_key(provider, workflow_type, config)
        initial_time = self.cache.access_times[cache_key]
        
        # Wait a bit and access again
        time.sleep(0.01)
        
        # Act
        self.cache.get(provider, workflow_type, config)
        
        # Assert
        new_time = self.cache.access_times[cache_key]
        assert new_time > initial_time

    def test_cache_statistics(self):
        """Test cache hit/miss statistics."""
        # Arrange
        provider = "openai"
        workflow_type = "full"
        config = {"temperature": 0.7}
        mock_workflow = MagicMock()
        
        # Act
        self.cache.get(provider, workflow_type, config)  # Miss
        self.cache.put(provider, workflow_type, config, mock_workflow)
        self.cache.get(provider, workflow_type, config)  # Hit
        self.cache.get(provider, workflow_type, config)  # Hit
        self.cache.get("other", "type", {})  # Miss
        
        # Assert
        assert self.cache.cache_hits == 2
        assert self.cache.cache_misses == 2
        assert self.cache.get_hit_rate() == 0.5

    def test_cache_clear(self):
        """Test clearing the cache."""
        # Arrange
        self.cache.put("openai", "full", {"temp": 0.7}, MagicMock())
        self.cache.put("anthropic", "tools", {"temp": 0.5}, MagicMock())
        
        # Act
        self.cache.clear()
        
        # Assert
        assert len(self.cache.cache) == 0
        assert len(self.cache.access_times) == 0


@pytest.mark.unit
class TestLazyToolLoader:
    """Test LazyToolLoader functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.loader = LazyToolLoader()

    def test_lazy_tool_loader_initialization(self):
        """Test LazyToolLoader initialization."""
        # Assert
        assert len(self.loader.loaded_tools) == 0
        assert len(self.loader.tool_configs) == 0

    def test_register_tool_config(self):
        """Test registering tool configuration."""
        # Arrange
        tool_name = "calculator"
        tool_config = {
            "module": "tools.calculator",
            "class": "Calculator",
            "init_params": {"precision": 10}
        }
        
        # Act
        self.loader.register_tool(tool_name, tool_config)
        
        # Assert
        assert tool_name in self.loader.tool_configs
        assert self.loader.tool_configs[tool_name] == tool_config
        assert tool_name not in self.loader.loaded_tools

    def test_load_tool_on_demand(self):
        """Test loading tool only when needed."""
        # Arrange
        tool_name = "calculator"
        tool_config = {
            "module": "tools.calculator",
            "class": "Calculator",
            "init_params": {}
        }
        mock_tool = MagicMock()
        
        self.loader.register_tool(tool_name, tool_config)
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_calculator_class = MagicMock(return_value=mock_tool)
            mock_module.Calculator = mock_calculator_class
            mock_import.return_value = mock_module
            
            # Act
            tool = self.loader.get_tool(tool_name)
            
            # Assert
            assert tool == mock_tool
            assert tool_name in self.loader.loaded_tools
            mock_import.assert_called_once_with("tools.calculator")
            mock_calculator_class.assert_called_once_with()

    def test_get_already_loaded_tool(self):
        """Test getting already loaded tool doesn't reload."""
        # Arrange
        tool_name = "calculator"
        mock_tool = MagicMock()
        self.loader.loaded_tools[tool_name] = mock_tool
        
        # Act
        tool = self.loader.get_tool(tool_name)
        
        # Assert
        assert tool == mock_tool

    def test_get_unregistered_tool(self):
        """Test getting unregistered tool raises error."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.loader.get_tool("nonexistent_tool")
        
        assert "not registered" in str(exc_info.value)

    def test_get_available_tools(self):
        """Test getting list of available tools."""
        # Arrange
        self.loader.register_tool("tool1", {"module": "mod1"})
        self.loader.register_tool("tool2", {"module": "mod2"})
        self.loader.loaded_tools["tool3"] = MagicMock()  # Already loaded
        
        # Act
        available = self.loader.get_available_tools()
        
        # Assert
        assert "tool1" in available
        assert "tool2" in available
        assert "tool3" in available

    def test_preload_tools(self):
        """Test preloading specific tools."""
        # Arrange
        tools_to_preload = ["tool1", "tool2"]
        mock_tools = [MagicMock(), MagicMock()]
        
        self.loader.register_tool("tool1", {"module": "mod1", "class": "Tool1"})
        self.loader.register_tool("tool2", {"module": "mod2", "class": "Tool2"})
        
        with patch.object(self.loader, 'get_tool') as mock_get_tool:
            mock_get_tool.side_effect = mock_tools
            
            # Act
            self.loader.preload_tools(tools_to_preload)
            
            # Assert
            assert mock_get_tool.call_count == 2
            mock_get_tool.assert_any_call("tool1")
            mock_get_tool.assert_any_call("tool2")


@pytest.mark.unit
class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor()

    def test_performance_monitor_initialization(self):
        """Test PerformanceMonitor initialization."""
        # Assert
        assert len(self.monitor.execution_times) == 0
        assert len(self.monitor.memory_usage) == 0
        assert len(self.monitor.active_workflows) == 0

    def test_start_monitoring_workflow(self):
        """Test starting workflow monitoring."""
        # Arrange
        workflow_id = "test-workflow-123"
        
        # Act
        self.monitor.start_monitoring(workflow_id)
        
        # Assert
        assert workflow_id in self.monitor.active_workflows
        assert "start_time" in self.monitor.active_workflows[workflow_id]
        assert "memory_start" in self.monitor.active_workflows[workflow_id]

    def test_stop_monitoring_workflow(self):
        """Test stopping workflow monitoring."""
        # Arrange
        workflow_id = "test-workflow-123"
        self.monitor.start_monitoring(workflow_id)
        
        # Small delay to ensure execution time > 0
        time.sleep(0.001)
        
        # Act
        metrics = self.monitor.stop_monitoring(workflow_id)
        
        # Assert
        assert workflow_id not in self.monitor.active_workflows
        assert workflow_id in self.monitor.execution_times
        assert "execution_time" in metrics
        assert "memory_delta" in metrics
        assert metrics["execution_time"] > 0

    def test_stop_monitoring_untracked_workflow(self):
        """Test stopping monitoring for untracked workflow."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.monitor.stop_monitoring("nonexistent-workflow")
        
        assert "not being monitored" in str(exc_info.value)

    def test_get_performance_summary(self):
        """Test getting performance summary."""
        # Arrange
        workflow_ids = ["workflow1", "workflow2", "workflow3"]
        
        # Simulate multiple workflow executions
        for workflow_id in workflow_ids:
            self.monitor.start_monitoring(workflow_id)
            time.sleep(0.001)  # Small delay
            self.monitor.stop_monitoring(workflow_id)
        
        # Act
        summary = self.monitor.get_performance_summary()
        
        # Assert
        assert summary["total_workflows"] == 3
        assert "avg_execution_time" in summary
        assert "min_execution_time" in summary
        assert "max_execution_time" in summary
        assert "total_execution_time" in summary
        assert summary["avg_execution_time"] > 0

    def test_get_workflow_performance_history(self):
        """Test getting performance history for specific workflow."""
        # Arrange
        workflow_id = "repeated-workflow"
        
        # Execute same workflow multiple times
        for _ in range(3):
            self.monitor.start_monitoring(workflow_id)
            time.sleep(0.001)
            self.monitor.stop_monitoring(workflow_id)
        
        # Act
        history = self.monitor.get_workflow_history(workflow_id)
        
        # Assert
        assert len(history) == 3
        assert all("execution_time" in entry for entry in history)
        assert all("timestamp" in entry for entry in history)

    def test_detect_performance_anomalies(self):
        """Test detecting performance anomalies."""
        # Arrange - Create baseline with normal execution times
        normal_times = [0.1, 0.11, 0.09, 0.1, 0.12]
        for i, exec_time in enumerate(normal_times):
            workflow_id = f"normal-{i}"
            self.monitor.execution_times[workflow_id] = [exec_time]
        
        # Add an anomalous slow execution
        self.monitor.execution_times["slow-workflow"] = [1.0]  # 10x slower
        
        # Act
        anomalies = self.monitor.detect_anomalies(threshold_multiplier=3.0)
        
        # Assert
        assert len(anomalies) > 0
        assert any("slow-workflow" in anomaly["workflow_id"] for anomaly in anomalies)


@pytest.mark.unit
class TestWorkflowOptimizer:
    """Test WorkflowOptimizer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = WorkflowOptimizer()

    def test_workflow_optimizer_initialization(self):
        """Test WorkflowOptimizer initialization."""
        # Assert
        assert self.optimizer.cache is not None
        assert self.optimizer.tool_loader is not None
        assert self.optimizer.monitor is not None

    def test_analyze_workflow_performance(self):
        """Test analyzing workflow performance."""
        # Arrange
        workflow_config = {
            "workflow_type": "full",
            "enable_memory": True,
            "max_tool_calls": 10,
            "tools": ["calculator", "search", "web_browser"]
        }
        
        # Mock performance data
        mock_metrics = {
            "execution_time": 5.2,
            "memory_usage": 150.5,
            "tool_usage": {"calculator": 3, "search": 2},
            "cache_hit_rate": 0.6
        }
        
        # Act
        analysis = self.optimizer.analyze_workflow_performance(
            workflow_config, mock_metrics
        )
        
        # Assert
        assert "performance_score" in analysis
        assert "bottlenecks" in analysis
        assert "recommendations" in analysis
        assert analysis["performance_score"] >= 0.0
        assert analysis["performance_score"] <= 1.0

    def test_suggest_optimizations(self):
        """Test suggesting workflow optimizations."""
        # Arrange
        slow_workflow_config = {
            "workflow_type": "full",
            "enable_memory": True,
            "memory_window": 200,  # Very large
            "max_tool_calls": 50,  # Very high
            "temperature": 0.9,    # High randomness
            "tools": ["tool1", "tool2", "tool3", "tool4", "tool5"]  # Many tools
        }
        
        performance_data = {
            "execution_time": 30.0,  # Slow
            "memory_usage": 500.0,   # High memory
            "tool_usage": {"tool1": 1, "tool2": 0, "tool3": 0, "tool4": 0, "tool5": 0},
            "cache_hit_rate": 0.1    # Low cache hit
        }
        
        # Act
        suggestions = self.optimizer.suggest_optimizations(
            slow_workflow_config, performance_data
        )
        
        # Assert
        assert len(suggestions) > 0
        
        # Should suggest reducing memory window
        memory_suggestions = [s for s in suggestions if "memory" in s.lower()]
        assert len(memory_suggestions) > 0
        
        # Should suggest removing unused tools
        tool_suggestions = [s for s in suggestions if "tool" in s.lower()]
        assert len(tool_suggestions) > 0

    def test_optimize_workflow_config(self):
        """Test optimizing workflow configuration."""
        # Arrange
        original_config = {
            "workflow_type": "full",
            "enable_memory": True,
            "memory_window": 100,
            "max_tool_calls": 20,
            "temperature": 0.8,
            "tools": ["useful_tool", "unused_tool1", "unused_tool2"]
        }
        
        usage_stats = {
            "tool_usage": {"useful_tool": 50, "unused_tool1": 1, "unused_tool2": 0},
            "avg_memory_used": 30,  # Using much less than allocated
            "avg_tool_calls": 5     # Using much less than max
        }
        
        # Act
        optimized_config = self.optimizer.optimize_workflow_config(
            original_config, usage_stats
        )
        
        # Assert
        # Should reduce memory window based on actual usage
        assert optimized_config["memory_window"] < original_config["memory_window"]
        
        # Should reduce max_tool_calls based on actual usage
        assert optimized_config["max_tool_calls"] < original_config["max_tool_calls"]
        
        # Should keep useful tools, remove unused ones
        assert "useful_tool" in optimized_config["tools"]
        assert len(optimized_config["tools"]) < len(original_config["tools"])

    def test_benchmark_workflow_variants(self):
        """Test benchmarking different workflow variants."""
        # Arrange
        base_config = {
            "workflow_type": "full",
            "enable_memory": True,
            "memory_window": 50
        }
        
        variants = [
            {"memory_window": 25},
            {"memory_window": 50},
            {"memory_window": 100}
        ]
        
        # Mock execution function
        async def mock_execute_workflow(config):
            # Simulate execution time based on memory window
            execution_time = config["memory_window"] * 0.01
            return {
                "execution_time": execution_time,
                "memory_usage": config["memory_window"] * 2.0,
                "result": "success"
            }
        
        # Act
        async def run_benchmark():
            return await self.optimizer.benchmark_workflow_variants(
                base_config, variants, mock_execute_workflow, iterations=1
            )
        
        # Run async test
        results = asyncio.run(run_benchmark())
        
        # Assert
        assert len(results) == 3
        assert all("avg_execution_time" in result for result in results)
        assert all("config" in result for result in results)
        
        # Results should be ordered by performance (fastest first)
        execution_times = [r["avg_execution_time"] for r in results]
        assert execution_times == sorted(execution_times)


@pytest.mark.unit
class TestBatchProcessor:
    """Test BatchProcessor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = BatchProcessor(batch_size=3, max_concurrent=2)

    def test_batch_processor_initialization(self):
        """Test BatchProcessor initialization."""
        # Assert
        assert self.processor.batch_size == 3
        assert self.processor.max_concurrent == 2
        assert len(self.processor.pending_items) == 0

    @pytest.mark.asyncio
    async def test_add_item_to_batch(self):
        """Test adding items to batch processor."""
        # Arrange
        async def mock_process_batch(items):
            return [f"processed_{item}" for item in items]
        
        # Act
        self.processor.set_processor(mock_process_batch)
        
        # Add items
        results = []
        for i in range(5):
            result = await self.processor.add_item(f"item_{i}")
            if result:
                results.extend(result)
        
        # Process any remaining items
        remaining = await self.processor.flush()
        if remaining:
            results.extend(remaining)
        
        # Assert
        assert len(results) == 5
        assert all("processed_item_" in result for result in results)

    @pytest.mark.asyncio
    async def test_batch_automatic_processing(self):
        """Test automatic batch processing when batch size reached."""
        # Arrange
        processed_batches = []
        
        async def mock_process_batch(items):
            processed_batches.append(items)
            return [f"processed_{item}" for item in items]
        
        self.processor.set_processor(mock_process_batch)
        
        # Act - Add exactly batch_size items
        results = []
        for i in range(3):  # batch_size = 3
            result = await self.processor.add_item(f"item_{i}")
            if result:
                results.extend(result)
        
        # Assert
        assert len(processed_batches) == 1
        assert len(processed_batches[0]) == 3
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(self):
        """Test concurrent processing of multiple batches."""
        # Arrange
        processor = BatchProcessor(batch_size=2, max_concurrent=3)
        
        processing_order = []
        
        async def mock_process_batch(items):
            batch_id = f"batch_{len(processing_order)}"
            processing_order.append(batch_id)
            await asyncio.sleep(0.1)  # Simulate processing time
            return [f"processed_{item}_{batch_id}" for item in items]
        
        processor.set_processor(mock_process_batch)
        
        # Act - Add enough items to create multiple batches
        tasks = []
        for i in range(6):  # Will create 3 batches of size 2
            task = asyncio.create_task(processor.add_item(f"item_{i}"))
            tasks.append(task)
        
        # Wait for all processing to complete
        results = await asyncio.gather(*tasks)
        
        # Assert
        # Should have processed 3 batches
        assert len(processing_order) == 3


@pytest.mark.integration
class TestWorkflowPerformanceIntegration:
    """Integration tests for workflow performance optimization."""

    @pytest.mark.asyncio
    async def test_end_to_end_performance_optimization(self):
        """Test complete performance optimization workflow."""
        # Arrange
        cache = WorkflowCache(max_size=10)
        monitor = PerformanceMonitor()
        optimizer = WorkflowOptimizer()
        
        # Mock workflow configuration
        base_config = {
            "workflow_type": "full",
            "enable_memory": True,
            "memory_window": 100,
            "max_tool_calls": 10,
            "tools": ["calculator", "search"]
        }
        
        mock_workflow = MagicMock()
        
        # Step 1: Cache miss - create and cache workflow
        cached_workflow = cache.get("openai", "full", base_config)
        assert cached_workflow is None
        
        cache.put("openai", "full", base_config, mock_workflow)
        
        # Step 2: Cache hit - retrieve cached workflow
        cached_workflow = cache.get("openai", "full", base_config)
        assert cached_workflow == mock_workflow
        
        # Step 3: Monitor performance
        workflow_id = "performance-test"
        monitor.start_monitoring(workflow_id)
        
        # Simulate workflow execution
        await asyncio.sleep(0.01)
        
        metrics = monitor.stop_monitoring(workflow_id)
        
        # Step 4: Analyze and optimize
        analysis = optimizer.analyze_workflow_performance(base_config, metrics)
        suggestions = optimizer.suggest_optimizations(base_config, metrics)
        
        # Assert
        assert analysis["performance_score"] >= 0.0
        assert len(suggestions) >= 0
        assert cache.cache_hits == 1
        assert metrics["execution_time"] > 0

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance optimization under high load."""
        # Arrange
        cache = WorkflowCache(max_size=50)
        monitor = PerformanceMonitor()
        
        # Simulate many concurrent workflow requests
        num_workflows = 20
        workflow_configs = []
        
        for i in range(num_workflows):
            config = {
                "workflow_type": "full",
                "temperature": i * 0.05,  # Different configs
                "max_tokens": 1000 + i * 100
            }
            workflow_configs.append(config)
        
        async def simulate_workflow_execution(config_id, config):
            # Check cache first
            cached = cache.get("openai", "full", config)
            if not cached:
                # Simulate workflow creation
                mock_workflow = MagicMock()
                cache.put("openai", "full", config, mock_workflow)
                cached = mock_workflow
            
            # Monitor execution
            workflow_id = f"workflow_{config_id}"
            monitor.start_monitoring(workflow_id)
            
            # Simulate execution time
            await asyncio.sleep(0.001 + config_id * 0.0001)
            
            return monitor.stop_monitoring(workflow_id)
        
        # Act - Execute all workflows concurrently
        start_time = time.time()
        
        tasks = [
            simulate_workflow_execution(i, config)
            for i, config in enumerate(workflow_configs)
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Assert
        assert len(results) == num_workflows
        assert all("execution_time" in result for result in results)
        
        # Cache should have improved performance
        assert cache.cache_hits > 0
        assert cache.get_hit_rate() > 0
        
        # Total time should be reasonable (parallelization working)
        assert total_time < 1.0  # Should complete in under 1 second
        
        # Performance summary should be available
        summary = monitor.get_performance_summary()
        assert summary["total_workflows"] == num_workflows
        assert summary["avg_execution_time"] > 0