"""Tests for monitoring and metrics collection utilities."""

import pytest
import time
from unittest.mock import patch, MagicMock
from collections import deque
from datetime import datetime, UTC

from chatter.utils.monitoring import (
    MetricType,
    RequestMetrics,
    DatabaseMetrics,
    MonitoringService,
    PerformanceTracker,
    AlertManager
)


@pytest.mark.unit
class TestMetrics:
    """Test metrics data classes."""

    def test_request_metrics_creation(self):
        """Test RequestMetrics creation and attributes."""
        # Arrange
        timestamp = time.time()
        
        # Act
        metrics = RequestMetrics(
            timestamp=timestamp,
            method="GET",
            path="/api/v1/health",
            status_code=200,
            response_time_ms=123.45,
            correlation_id="test-corr-123",
            user_id="user-456",
            rate_limited=False,
            cache_hit=True,
            db_queries=2,
            db_time_ms=45.67
        )
        
        # Assert
        assert metrics.timestamp == timestamp
        assert metrics.method == "GET"
        assert metrics.path == "/api/v1/health"
        assert metrics.status_code == 200
        assert metrics.response_time_ms == 123.45
        assert metrics.correlation_id == "test-corr-123"
        assert metrics.user_id == "user-456"
        assert metrics.rate_limited is False
        assert metrics.cache_hit is True
        assert metrics.db_queries == 2
        assert metrics.db_time_ms == 45.67

    def test_database_metrics_creation(self):
        """Test DatabaseMetrics creation and attributes."""
        # Arrange
        timestamp = time.time()
        
        # Act
        metrics = DatabaseMetrics(
            timestamp=timestamp,
            operation="select",
            table="users",
            duration_ms=78.9,
            rows_affected=15,
            correlation_id="test-corr-456",
            query_hash="hash-abc123"
        )
        
        # Assert
        assert metrics.timestamp == timestamp
        assert metrics.operation == "select"
        assert metrics.table == "users"
        assert metrics.duration_ms == 78.9
        assert metrics.rows_affected == 15
        assert metrics.correlation_id == "test-corr-456"
        assert metrics.query_hash == "hash-abc123"

    def test_metric_type_enum(self):
        """Test MetricType enum values."""
        # Assert
        assert MetricType.REQUEST == "request"
        assert MetricType.DATABASE == "database"
        assert MetricType.CACHE == "cache"
        assert MetricType.LLM == "llm"
        assert MetricType.WORKFLOW == "workflow"
        assert MetricType.ERROR == "error"


@pytest.mark.unit
class TestMonitoringService:
    """Test monitoring service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitoring = MonitoringService()

    def test_monitoring_service_initialization(self):
        """Test monitoring service initialization."""
        # Act
        service = MonitoringService()
        
        # Assert
        assert isinstance(service.request_metrics, deque)
        assert isinstance(service.database_metrics, deque)
        assert isinstance(service.error_counts, dict)
        assert service.start_time is not None

    def test_record_request_metric(self):
        """Test recording request metrics."""
        # Arrange
        request_metric = RequestMetrics(
            timestamp=time.time(),
            method="POST",
            path="/api/v1/chat",
            status_code=201,
            response_time_ms=256.78,
            correlation_id="req-123"
        )
        
        # Act
        self.monitoring.record_request(request_metric)
        
        # Assert
        assert len(self.monitoring.request_metrics) == 1
        recorded_metric = self.monitoring.request_metrics[0]
        assert recorded_metric.method == "POST"
        assert recorded_metric.path == "/api/v1/chat"
        assert recorded_metric.status_code == 201

    def test_record_database_metric(self):
        """Test recording database metrics."""
        # Arrange
        db_metric = DatabaseMetrics(
            timestamp=time.time(),
            operation="insert",
            table="messages",
            duration_ms=89.12,
            rows_affected=1,
            correlation_id="db-456"
        )
        
        # Act
        self.monitoring.record_database_query(db_metric)
        
        # Assert
        assert len(self.monitoring.database_metrics) == 1
        recorded_metric = self.monitoring.database_metrics[0]
        assert recorded_metric.operation == "insert"
        assert recorded_metric.table == "messages"
        assert recorded_metric.duration_ms == 89.12

    def test_record_error(self):
        """Test recording error events."""
        # Arrange
        error_type = "ValidationError"
        error_message = "Invalid input format"
        
        # Act
        self.monitoring.record_error(
            error_type=error_type,
            error_message=error_message,
            correlation_id="err-789"
        )
        
        # Assert
        assert error_type in self.monitoring.error_counts
        assert self.monitoring.error_counts[error_type] == 1
        
        # Record another error of same type
        self.monitoring.record_error(error_type, "Another error", "err-790")
        assert self.monitoring.error_counts[error_type] == 2

    def test_get_request_stats(self):
        """Test getting request statistics."""
        # Arrange
        # Add some test request metrics
        for i in range(5):
            metric = RequestMetrics(
                timestamp=time.time(),
                method="GET",
                path=f"/api/v1/endpoint{i}",
                status_code=200 if i < 4 else 500,
                response_time_ms=100 + (i * 50),
                correlation_id=f"req-{i}"
            )
            self.monitoring.record_request(metric)
        
        # Act
        stats = self.monitoring.get_request_stats()
        
        # Assert
        assert stats["total_requests"] == 5
        assert stats["avg_response_time_ms"] == 200.0  # (100+150+200+250+300)/5
        assert stats["success_rate"] == 0.8  # 4 success out of 5
        assert stats["error_rate"] == 0.2  # 1 error out of 5

    def test_get_database_stats(self):
        """Test getting database statistics."""
        # Arrange
        operations = ["select", "select", "insert", "update", "delete"]
        durations = [50, 75, 120, 90, 60]
        
        for op, duration in zip(operations, durations):
            metric = DatabaseMetrics(
                timestamp=time.time(),
                operation=op,
                table="test_table",
                duration_ms=duration,
                rows_affected=1,
                correlation_id=f"db-{op}"
            )
            self.monitoring.record_database_query(metric)
        
        # Act
        stats = self.monitoring.get_database_stats()
        
        # Assert
        assert stats["total_queries"] == 5
        assert stats["avg_query_time_ms"] == 79.0  # (50+75+120+90+60)/5
        assert stats["operations"]["select"] == 2
        assert stats["operations"]["insert"] == 1

    def test_get_error_stats(self):
        """Test getting error statistics."""
        # Arrange
        error_types = ["ValidationError", "DatabaseError", "ValidationError", "TimeoutError"]
        
        for error_type in error_types:
            self.monitoring.record_error(error_type, "Test error", f"err-{error_type}")
        
        # Act
        stats = self.monitoring.get_error_stats()
        
        # Assert
        assert stats["total_errors"] == 4
        assert stats["error_types"]["ValidationError"] == 2
        assert stats["error_types"]["DatabaseError"] == 1
        assert stats["error_types"]["TimeoutError"] == 1

    def test_get_system_health(self):
        """Test getting system health status."""
        # Arrange
        # Add some metrics to simulate system activity
        for i in range(10):
            self.monitoring.record_request(RequestMetrics(
                timestamp=time.time(),
                method="GET",
                path="/api/v1/test",
                status_code=200,
                response_time_ms=100,
                correlation_id=f"req-{i}"
            ))
        
        # Act
        health = self.monitoring.get_system_health()
        
        # Assert
        assert "status" in health
        assert "uptime_seconds" in health
        assert "request_rate" in health
        assert "error_rate" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]

    def test_metrics_cleanup_old_data(self):
        """Test cleanup of old metrics data."""
        # Arrange
        old_timestamp = time.time() - 3600  # 1 hour ago
        recent_timestamp = time.time()
        
        # Add old metric
        old_metric = RequestMetrics(
            timestamp=old_timestamp,
            method="GET",
            path="/api/v1/old",
            status_code=200,
            response_time_ms=100,
            correlation_id="old-req"
        )
        
        # Add recent metric
        recent_metric = RequestMetrics(
            timestamp=recent_timestamp,
            method="GET",
            path="/api/v1/recent",
            status_code=200,
            response_time_ms=100,
            correlation_id="recent-req"
        )
        
        self.monitoring.record_request(old_metric)
        self.monitoring.record_request(recent_metric)
        
        # Act
        cleaned_count = self.monitoring.cleanup_old_metrics(max_age_seconds=1800)  # 30 minutes
        
        # Assert
        assert cleaned_count == 1  # Old metric should be removed
        assert len(self.monitoring.request_metrics) == 1
        assert self.monitoring.request_metrics[0].correlation_id == "recent-req"


@pytest.mark.unit
class TestPerformanceTracker:
    """Test performance tracking functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()

    def test_performance_tracker_context_manager(self):
        """Test performance tracker as context manager."""
        # Act
        with self.tracker.track_operation("test_operation") as operation:
            time.sleep(0.1)  # Simulate work
            operation.add_metadata("items_processed", 10)
        
        # Assert
        metrics = self.tracker.get_operation_metrics("test_operation")
        assert len(metrics) == 1
        assert metrics[0]["duration_ms"] >= 100  # At least 100ms
        assert metrics[0]["metadata"]["items_processed"] == 10

    def test_performance_tracker_decorator(self):
        """Test performance tracker as decorator."""
        # Arrange
        @self.tracker.track_performance("decorated_function")
        def test_function(x, y):
            time.sleep(0.05)  # Simulate work
            return x + y
        
        # Act
        result = test_function(3, 4)
        
        # Assert
        assert result == 7
        metrics = self.tracker.get_operation_metrics("decorated_function")
        assert len(metrics) == 1
        assert metrics[0]["duration_ms"] >= 50

    def test_performance_tracker_statistics(self):
        """Test performance tracker statistics."""
        # Arrange
        operation_name = "batch_processing"
        
        # Record multiple operations
        for i in range(5):
            with self.tracker.track_operation(operation_name):
                time.sleep(0.02 * (i + 1))  # Variable duration
        
        # Act
        stats = self.tracker.get_operation_stats(operation_name)
        
        # Assert
        assert stats["count"] == 5
        assert stats["avg_duration_ms"] > 0
        assert stats["min_duration_ms"] > 0
        assert stats["max_duration_ms"] > stats["min_duration_ms"]
        assert stats["total_duration_ms"] > 0


@pytest.mark.unit
class TestAlertManager:
    """Test alert management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.alert_manager = AlertManager()

    def test_alert_creation(self):
        """Test creating alerts."""
        # Act
        alert_id = self.alert_manager.create_alert(
            level="warning",
            message="High memory usage detected",
            source="system_monitor",
            metadata={"memory_usage": "85%"}
        )
        
        # Assert
        assert alert_id is not None
        alerts = self.alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0]["level"] == "warning"
        assert alerts[0]["message"] == "High memory usage detected"

    def test_alert_threshold_checking(self):
        """Test automatic alert creation based on thresholds."""
        # Arrange
        self.alert_manager.set_threshold(
            metric="response_time",
            threshold=500.0,
            level="warning"
        )
        
        # Act - Below threshold
        self.alert_manager.check_threshold("response_time", 300.0)
        alerts_below = self.alert_manager.get_active_alerts()
        
        # Act - Above threshold
        self.alert_manager.check_threshold("response_time", 600.0)
        alerts_above = self.alert_manager.get_active_alerts()
        
        # Assert
        assert len(alerts_below) == 0
        assert len(alerts_above) == 1
        assert "response_time" in alerts_above[0]["message"]

    def test_alert_resolution(self):
        """Test resolving alerts."""
        # Arrange
        alert_id = self.alert_manager.create_alert(
            level="critical",
            message="Database connection lost",
            source="database_monitor"
        )
        
        # Act
        resolved = self.alert_manager.resolve_alert(alert_id, "Database connection restored")
        
        # Assert
        assert resolved is True
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 0
        
        resolved_alerts = self.alert_manager.get_resolved_alerts()
        assert len(resolved_alerts) == 1
        assert resolved_alerts[0]["resolution_message"] == "Database connection restored"

    def test_alert_escalation(self):
        """Test alert escalation based on time."""
        # Arrange
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000.0
            
            alert_id = self.alert_manager.create_alert(
                level="warning",
                message="Test alert",
                source="test"
            )
            
            # Simulate time passing
            mock_time.return_value = 1000.0 + 3600  # 1 hour later
            
            # Act
            escalated_alerts = self.alert_manager.check_escalation(escalation_time_seconds=1800)  # 30 min
            
            # Assert
            assert len(escalated_alerts) == 1
            assert escalated_alerts[0]["id"] == alert_id
            assert escalated_alerts[0]["level"] == "critical"  # Should be escalated


@pytest.mark.integration
class TestMonitoringIntegration:
    """Integration tests for monitoring functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitoring = MonitoringService()
        self.tracker = PerformanceTracker()
        self.alert_manager = AlertManager()

    def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        # Arrange
        correlation_id = "integration-test-123"
        
        # Act - Track a complete request flow
        with self.tracker.track_operation("request_processing") as operation:
            # Simulate request processing
            operation.add_metadata("user_id", "user-123")
            
            # Record request start
            request_metric = RequestMetrics(
                timestamp=time.time(),
                method="POST",
                path="/api/v1/process",
                status_code=200,
                response_time_ms=0,  # Will be updated
                correlation_id=correlation_id
            )
            
            # Simulate database operations
            db_metric = DatabaseMetrics(
                timestamp=time.time(),
                operation="select",
                table="documents",
                duration_ms=45.0,
                rows_affected=5,
                correlation_id=correlation_id
            )
            self.monitoring.record_database_query(db_metric)
            
            # Simulate processing time
            time.sleep(0.05)
            
            # Update and record final request metric
            request_metric.response_time_ms = 75.0
            request_metric.db_queries = 1
            request_metric.db_time_ms = 45.0
            self.monitoring.record_request(request_metric)
        
        # Assert monitoring data was recorded
        request_stats = self.monitoring.get_request_stats()
        db_stats = self.monitoring.get_database_stats()
        performance_stats = self.tracker.get_operation_stats("request_processing")
        
        assert request_stats["total_requests"] == 1
        assert db_stats["total_queries"] == 1
        assert performance_stats["count"] == 1

    def test_monitoring_with_alerts(self):
        """Test monitoring integration with alerting."""
        # Arrange
        self.alert_manager.set_threshold("error_rate", 0.1, "warning")  # 10% error rate
        
        # Simulate requests with some errors
        for i in range(10):
            status_code = 500 if i < 2 else 200  # 20% error rate
            
            request_metric = RequestMetrics(
                timestamp=time.time(),
                method="GET",
                path="/api/v1/test",
                status_code=status_code,
                response_time_ms=100,
                correlation_id=f"req-{i}"
            )
            self.monitoring.record_request(request_metric)
            
            if status_code == 500:
                self.monitoring.record_error("APIError", f"Request failed: {i}", f"req-{i}")
        
        # Check if alert should be triggered
        stats = self.monitoring.get_request_stats()
        error_rate = stats["error_rate"]
        
        self.alert_manager.check_threshold("error_rate", error_rate)
        
        # Assert alert was created
        alerts = self.alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert "error_rate" in alerts[0]["message"]

    def test_monitoring_performance_bottleneck_detection(self):
        """Test detection of performance bottlenecks."""
        # Arrange
        slow_operations = ["heavy_computation", "external_api_call", "file_processing"]
        
        # Simulate operations with different performance characteristics
        for operation in slow_operations:
            with self.tracker.track_operation(operation):
                if operation == "heavy_computation":
                    time.sleep(0.1)  # Slow operation
                elif operation == "external_api_call":
                    time.sleep(0.05)  # Medium operation
                else:
                    time.sleep(0.01)  # Fast operation
        
        # Act - Find slowest operations
        all_stats = {}
        for operation in slow_operations:
            all_stats[operation] = self.tracker.get_operation_stats(operation)
        
        # Assert - Heavy computation should be slowest
        heavy_stats = all_stats["heavy_computation"]
        file_stats = all_stats["file_processing"]
        
        assert heavy_stats["avg_duration_ms"] > file_stats["avg_duration_ms"]
        assert heavy_stats["avg_duration_ms"] >= 100  # At least 100ms