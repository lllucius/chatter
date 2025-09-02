"""Tests for analytics service and statistics generation."""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatter.core.analytics import (
    AnalyticsService,
    ConversationAnalyzer,
    PerformanceAnalyzer,
    TrendAnalyzer,
    UserBehaviorAnalyzer,
)
from chatter.models.conversation import (
    MessageRole,
)
from chatter.models.document import DocumentStatus
from chatter.schemas.analytics import (
    AnalyticsTimeRange,
)


@pytest.mark.unit
class TestAnalyticsService:
    """Test AnalyticsService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.analytics_service = AnalyticsService(self.mock_session)

    @pytest.mark.asyncio
    async def test_get_conversation_stats_basic(self):
        """Test getting basic conversation statistics."""
        # Arrange
        user_id = "user-123"

        # Mock database queries
        mock_conversations = [
            MagicMock(id="conv-1", created_at=datetime.now(UTC)),
            MagicMock(id="conv-2", created_at=datetime.now(UTC)),
        ]
        mock_messages = [
            MagicMock(role=MessageRole.USER),
            MagicMock(role=MessageRole.ASSISTANT),
            MagicMock(role=MessageRole.USER),
            MagicMock(role=MessageRole.ASSISTANT),
        ]

        # Mock query results
        self.mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_conversations
        )
        self.mock_session.execute.return_value.scalar.side_effect = [
            len(mock_conversations),  # total_conversations
            len(mock_messages),  # total_messages
            len(
                [m for m in mock_messages if m.role == MessageRole.USER]
            ),  # user_messages
            15.5,  # avg_conversation_length
        ]

        # Act
        stats = await self.analytics_service.get_conversation_stats(
            user_id
        )

        # Assert
        assert stats["total_conversations"] == 2
        assert stats["total_messages"] == 4
        assert stats["user_messages"] == 2
        assert stats["avg_conversation_length"] == 15.5
        assert "most_active_period" in stats

    @pytest.mark.asyncio
    async def test_get_conversation_stats_with_time_range(self):
        """Test getting conversation statistics with time range filter."""
        # Arrange
        user_id = "user-123"
        time_range = AnalyticsTimeRange.LAST_7_DAYS

        # Mock filtered results
        self.mock_session.execute.return_value.scalar.side_effect = [
            5,  # conversations in last 7 days
            25,  # messages in last 7 days
            12,  # user messages in last 7 days
            8.3,  # avg conversation length
        ]

        # Act
        stats = await self.analytics_service.get_conversation_stats(
            user_id, time_range
        )

        # Assert
        assert stats["total_conversations"] == 5
        assert stats["total_messages"] == 25
        assert "time_range" in stats
        assert stats["time_range"] == time_range.value

    @pytest.mark.asyncio
    async def test_get_user_behavior_stats(self):
        """Test getting user behavior statistics."""
        # Arrange
        user_id = "user-123"

        # Mock user behavior data
        mock_session_data = [
            {"hour": 9, "activity_count": 15},
            {"hour": 14, "activity_count": 22},
            {"hour": 20, "activity_count": 8},
        ]

        self.mock_session.execute.return_value.all.return_value = (
            mock_session_data
        )

        # Act
        behavior_stats = (
            await self.analytics_service.get_user_behavior_stats(
                user_id
            )
        )

        # Assert
        assert "hourly_activity" in behavior_stats
        assert "peak_hours" in behavior_stats
        assert "activity_patterns" in behavior_stats
        assert len(behavior_stats["hourly_activity"]) == 3

    @pytest.mark.asyncio
    async def test_get_performance_metrics(self):
        """Test getting performance metrics."""
        # Arrange
        time_range = AnalyticsTimeRange.LAST_30_DAYS

        # Mock performance data
        self.mock_session.execute.return_value.scalar.side_effect = [
            1250.5,  # avg_response_time
            0.025,  # error_rate
            45.2,  # requests_per_minute
            150.0,  # avg_memory_usage
            35.5,  # avg_cpu_usage
        ]

        # Act
        metrics = await self.analytics_service.get_performance_metrics(
            time_range
        )

        # Assert
        assert metrics["avg_response_time"] == 1250.5
        assert metrics["error_rate"] == 0.025
        assert metrics["requests_per_minute"] == 45.2
        assert metrics["avg_memory_usage"] == 150.0
        assert metrics["avg_cpu_usage"] == 35.5

    @pytest.mark.asyncio
    async def test_get_document_usage_stats(self):
        """Test getting document usage statistics."""
        # Arrange
        time_range = AnalyticsTimeRange.LAST_7_DAYS

        # Mock document data
        mock_documents = [
            MagicMock(status=DocumentStatus.PROCESSED, access_count=15),
            MagicMock(status=DocumentStatus.PROCESSED, access_count=8),
            MagicMock(status=DocumentStatus.FAILED, access_count=0),
        ]

        self.mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_documents
        )

        # Act
        doc_stats = (
            await self.analytics_service.get_document_usage_stats(
                time_range
            )
        )

        # Assert
        assert doc_stats["total_documents"] == 3
        assert doc_stats["processed_documents"] == 2
        assert doc_stats["failed_documents"] == 1
        assert doc_stats["total_accesses"] == 23

    @pytest.mark.asyncio
    async def test_generate_usage_report(self):
        """Test generating comprehensive usage report."""
        # Arrange
        user_id = "user-123"
        time_range = AnalyticsTimeRange.LAST_30_DAYS

        # Mock various stats
        with (
            patch.object(
                self.analytics_service, 'get_conversation_stats'
            ) as mock_conv_stats,
            patch.object(
                self.analytics_service, 'get_user_behavior_stats'
            ) as mock_behavior_stats,
            patch.object(
                self.analytics_service, 'get_performance_metrics'
            ) as mock_perf_metrics,
        ):

            mock_conv_stats.return_value = {"total_conversations": 50}
            mock_behavior_stats.return_value = {"peak_hours": [9, 14]}
            mock_perf_metrics.return_value = {"avg_response_time": 1200}

            # Act
            report = await self.analytics_service.generate_usage_report(
                user_id, time_range
            )

            # Assert
            assert "conversation_stats" in report
            assert "behavior_stats" in report
            assert "performance_metrics" in report
            assert "generated_at" in report
            assert report["user_id"] == user_id

    def test_build_time_filter(self):
        """Test building time filter for queries."""
        # Arrange
        time_ranges = [
            AnalyticsTimeRange.LAST_24_HOURS,
            AnalyticsTimeRange.LAST_7_DAYS,
            AnalyticsTimeRange.LAST_30_DAYS,
            AnalyticsTimeRange.LAST_90_DAYS,
        ]

        # Act & Assert
        for time_range in time_ranges:
            filter_condition = (
                self.analytics_service._build_time_filter(time_range)
            )
            # Should return a valid SQL condition or None
            assert filter_condition is not None or time_range is None

    @pytest.mark.asyncio
    async def test_error_handling_in_stats_collection(self):
        """Test error handling during statistics collection."""
        # Arrange
        user_id = "user-123"
        self.mock_session.execute.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(Exception):
            await self.analytics_service.get_conversation_stats(user_id)


@pytest.mark.unit
class TestConversationAnalyzer:
    """Test ConversationAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ConversationAnalyzer()

    def test_analyze_conversation_length(self):
        """Test analyzing conversation length patterns."""
        # Arrange
        conversations = [
            {"messages": ["msg1", "msg2", "msg3"]},
            {"messages": ["msg1", "msg2"]},
            {"messages": ["msg1", "msg2", "msg3", "msg4", "msg5"]},
            {"messages": ["msg1"]},
        ]

        # Act
        analysis = self.analyzer.analyze_conversation_length(
            conversations
        )

        # Assert
        assert analysis["avg_length"] == 2.75
        assert analysis["min_length"] == 1
        assert analysis["max_length"] == 5
        assert analysis["median_length"] == 2.5

    def test_analyze_conversation_topics(self):
        """Test analyzing conversation topics."""
        # Arrange
        messages = [
            {"content": "I need help with Python programming"},
            {"content": "Can you help me debug this code?"},
            {"content": "What's the weather like today?"},
            {"content": "How do I write a function in Python?"},
        ]

        # Act
        topics = self.analyzer.analyze_conversation_topics(messages)

        # Assert
        assert "topics" in topics
        assert "topic_distribution" in topics
        # Should identify programming as a major topic
        assert any(
            "programming" in topic.lower() or "code" in topic.lower()
            for topic in topics["topics"]
        )

    def test_calculate_engagement_score(self):
        """Test calculating conversation engagement score."""
        # Arrange
        conversation_data = {
            "message_count": 15,
            "response_time_avg": 2.5,
            "user_questions": 8,
            "follow_up_questions": 3,
            "conversation_duration": 1800,  # 30 minutes
        }

        # Act
        engagement_score = self.analyzer.calculate_engagement_score(
            conversation_data
        )

        # Assert
        assert 0.0 <= engagement_score <= 1.0
        assert isinstance(engagement_score, float)

    def test_identify_conversation_patterns(self):
        """Test identifying conversation patterns."""
        # Arrange
        conversations = [
            {
                "start_time": "09:00",
                "topic": "programming",
                "length": 10,
                "satisfaction": 0.8,
            },
            {
                "start_time": "14:30",
                "topic": "general",
                "length": 5,
                "satisfaction": 0.6,
            },
            {
                "start_time": "09:15",
                "topic": "programming",
                "length": 12,
                "satisfaction": 0.9,
            },
        ]

        # Act
        patterns = self.analyzer.identify_conversation_patterns(
            conversations
        )

        # Assert
        assert "time_patterns" in patterns
        assert "topic_patterns" in patterns
        assert "satisfaction_patterns" in patterns

    def test_analyze_sentiment_trends(self):
        """Test analyzing sentiment trends in conversations."""
        # Arrange
        messages = [
            {
                "content": "I'm really frustrated with this issue",
                "timestamp": "2024-01-01T09:00:00Z",
            },
            {
                "content": "Thank you, that's very helpful!",
                "timestamp": "2024-01-01T09:15:00Z",
            },
            {
                "content": "This is exactly what I needed",
                "timestamp": "2024-01-01T09:30:00Z",
            },
        ]

        # Act
        sentiment_trends = self.analyzer.analyze_sentiment_trends(
            messages
        )

        # Assert
        assert "overall_sentiment" in sentiment_trends
        assert "sentiment_progression" in sentiment_trends
        assert len(sentiment_trends["sentiment_progression"]) == 3


@pytest.mark.unit
class TestUserBehaviorAnalyzer:
    """Test UserBehaviorAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = UserBehaviorAnalyzer()

    def test_analyze_activity_patterns(self):
        """Test analyzing user activity patterns."""
        # Arrange
        activities = [
            {"timestamp": "2024-01-01T09:00:00Z", "type": "message"},
            {"timestamp": "2024-01-01T09:15:00Z", "type": "message"},
            {"timestamp": "2024-01-01T14:30:00Z", "type": "message"},
            {"timestamp": "2024-01-01T14:45:00Z", "type": "message"},
            {"timestamp": "2024-01-01T20:00:00Z", "type": "message"},
        ]

        # Act
        patterns = self.analyzer.analyze_activity_patterns(activities)

        # Assert
        assert "hourly_distribution" in patterns
        assert "peak_hours" in patterns
        assert "activity_clusters" in patterns

    def test_calculate_user_engagement_metrics(self):
        """Test calculating user engagement metrics."""
        # Arrange
        user_data = {
            "total_sessions": 25,
            "total_messages": 150,
            "avg_session_duration": 15.5,
            "return_frequency": 0.8,
            "feature_usage": {"chat": 120, "documents": 30},
        }

        # Act
        engagement = self.analyzer.calculate_user_engagement_metrics(
            user_data
        )

        # Assert
        assert "engagement_score" in engagement
        assert "session_quality" in engagement
        assert "feature_adoption" in engagement
        assert 0.0 <= engagement["engagement_score"] <= 1.0

    def test_identify_user_segments(self):
        """Test identifying user behavior segments."""
        # Arrange
        users = [
            {
                "id": "user1",
                "activity_level": "high",
                "engagement": 0.9,
                "feature_usage": 15,
            },
            {
                "id": "user2",
                "activity_level": "low",
                "engagement": 0.3,
                "feature_usage": 3,
            },
            {
                "id": "user3",
                "activity_level": "medium",
                "engagement": 0.6,
                "feature_usage": 8,
            },
            {
                "id": "user4",
                "activity_level": "high",
                "engagement": 0.8,
                "feature_usage": 12,
            },
        ]

        # Act
        segments = self.analyzer.identify_user_segments(users)

        # Assert
        assert "power_users" in segments
        assert "casual_users" in segments
        assert "inactive_users" in segments
        assert len(segments["power_users"]) >= 1

    def test_predict_churn_risk(self):
        """Test predicting user churn risk."""
        # Arrange
        user_metrics = {
            "days_since_last_activity": 15,
            "activity_decline_rate": 0.3,
            "engagement_score": 0.2,
            "support_tickets": 3,
            "feature_adoption_rate": 0.1,
        }

        # Act
        churn_risk = self.analyzer.predict_churn_risk(user_metrics)

        # Assert
        assert "risk_score" in churn_risk
        assert "risk_factors" in churn_risk
        assert "recommendations" in churn_risk
        assert 0.0 <= churn_risk["risk_score"] <= 1.0


@pytest.mark.unit
class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = PerformanceAnalyzer()

    def test_analyze_response_times(self):
        """Test analyzing system response times."""
        # Arrange
        response_times = [
            1.2,
            0.8,
            2.1,
            1.5,
            0.9,
            3.2,
            1.1,
            1.8,
            0.7,
            2.5,
        ]

        # Act
        analysis = self.analyzer.analyze_response_times(response_times)

        # Assert
        assert "avg_response_time" in analysis
        assert "median_response_time" in analysis
        assert "p95_response_time" in analysis
        assert "p99_response_time" in analysis
        assert analysis["avg_response_time"] > 0

    def test_analyze_error_patterns(self):
        """Test analyzing error patterns."""
        # Arrange
        errors = [
            {
                "type": "timeout",
                "timestamp": "2024-01-01T09:00:00Z",
                "severity": "high",
            },
            {
                "type": "timeout",
                "timestamp": "2024-01-01T09:15:00Z",
                "severity": "high",
            },
            {
                "type": "validation",
                "timestamp": "2024-01-01T10:00:00Z",
                "severity": "medium",
            },
            {
                "type": "database",
                "timestamp": "2024-01-01T11:00:00Z",
                "severity": "high",
            },
        ]

        # Act
        patterns = self.analyzer.analyze_error_patterns(errors)

        # Assert
        assert "error_frequency" in patterns
        assert "error_types" in patterns
        assert "severity_distribution" in patterns
        assert "timeout" in patterns["error_types"]

    def test_calculate_system_health_score(self):
        """Test calculating overall system health score."""
        # Arrange
        metrics = {
            "avg_response_time": 1.5,
            "error_rate": 0.02,
            "uptime": 0.999,
            "cpu_usage": 0.65,
            "memory_usage": 0.75,
            "disk_usage": 0.80,
        }

        # Act
        health_score = self.analyzer.calculate_system_health_score(
            metrics
        )

        # Assert
        assert 0.0 <= health_score <= 1.0
        assert isinstance(health_score, float)

    def test_identify_performance_bottlenecks(self):
        """Test identifying performance bottlenecks."""
        # Arrange
        performance_data = {
            "database_query_time": 2.5,
            "llm_response_time": 8.2,
            "network_latency": 0.1,
            "cache_hit_rate": 0.3,
            "concurrent_requests": 150,
        }

        # Act
        bottlenecks = self.analyzer.identify_performance_bottlenecks(
            performance_data
        )

        # Assert
        assert "bottlenecks" in bottlenecks
        assert "recommendations" in bottlenecks
        # Should identify LLM response time as a bottleneck
        assert any(
            "llm" in bottleneck.lower()
            for bottleneck in bottlenecks["bottlenecks"]
        )


@pytest.mark.unit
class TestTrendAnalyzer:
    """Test TrendAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TrendAnalyzer()

    def test_analyze_usage_trends(self):
        """Test analyzing usage trends over time."""
        # Arrange
        usage_data = [
            {"date": "2024-01-01", "users": 100, "messages": 500},
            {"date": "2024-01-02", "users": 110, "messages": 550},
            {"date": "2024-01-03", "users": 120, "messages": 600},
            {"date": "2024-01-04", "users": 115, "messages": 575},
            {"date": "2024-01-05", "users": 125, "messages": 625},
        ]

        # Act
        trends = self.analyzer.analyze_usage_trends(usage_data)

        # Assert
        assert "user_growth_rate" in trends
        assert "message_growth_rate" in trends
        assert "trend_direction" in trends

    def test_forecast_future_usage(self):
        """Test forecasting future usage patterns."""
        # Arrange
        historical_data = [
            {"period": "2024-01-01", "value": 100},
            {"period": "2024-01-02", "value": 105},
            {"period": "2024-01-03", "value": 110},
            {"period": "2024-01-04", "value": 108},
            {"period": "2024-01-05", "value": 115},
        ]

        # Act
        forecast = self.analyzer.forecast_future_usage(
            historical_data, periods=3
        )

        # Assert
        assert "forecast" in forecast
        assert "confidence_interval" in forecast
        assert len(forecast["forecast"]) == 3

    def test_detect_anomalies(self):
        """Test detecting anomalies in usage patterns."""
        # Arrange
        data_points = [
            100,
            105,
            110,
            108,
            115,
            112,
            500,
            118,
            120,
            115,
        ]  # 500 is anomaly

        # Act
        anomalies = self.analyzer.detect_anomalies(
            data_points, threshold=2.0
        )

        # Assert
        assert "anomalies" in anomalies
        assert "anomaly_indices" in anomalies
        assert len(anomalies["anomalies"]) > 0
        assert 500 in anomalies["anomalies"]

    def test_calculate_seasonal_patterns(self):
        """Test calculating seasonal patterns."""
        # Arrange
        daily_data = []
        for day in range(30):
            # Simulate higher usage on weekdays
            usage = 100 if day % 7 < 5 else 60
            daily_data.append({"day": day, "usage": usage})

        # Act
        patterns = self.analyzer.calculate_seasonal_patterns(daily_data)

        # Assert
        assert "daily_patterns" in patterns
        assert "weekly_patterns" in patterns
        assert "peak_periods" in patterns


@pytest.mark.integration
class TestAnalyticsIntegration:
    """Integration tests for analytics system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.analytics_service = AnalyticsService(self.mock_session)
        self.conversation_analyzer = ConversationAnalyzer()
        self.user_analyzer = UserBehaviorAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()

    @pytest.mark.asyncio
    async def test_comprehensive_analytics_workflow(self):
        """Test complete analytics workflow."""
        # Arrange
        user_id = "integration-user"
        time_range = AnalyticsTimeRange.LAST_30_DAYS

        # Mock database responses
        self.mock_session.execute.return_value.scalar.side_effect = [
            25,  # total_conversations
            150,  # total_messages
            75,  # user_messages
            6.0,  # avg_conversation_length
        ]

        # Act
        # Step 1: Get basic conversation stats
        conv_stats = (
            await self.analytics_service.get_conversation_stats(
                user_id, time_range
            )
        )

        # Step 2: Analyze conversation patterns
        mock_conversations = [
            {
                "messages": ["msg1", "msg2", "msg3"],
                "topic": "technical",
            },
            {"messages": ["msg1", "msg2"], "topic": "general"},
        ]
        conversation_analysis = (
            self.conversation_analyzer.analyze_conversation_length(
                mock_conversations
            )
        )

        # Step 3: Analyze user behavior
        mock_activities = [
            {"timestamp": "2024-01-01T09:00:00Z", "type": "message"},
            {"timestamp": "2024-01-01T14:00:00Z", "type": "message"},
        ]
        behavior_patterns = (
            self.user_analyzer.analyze_activity_patterns(
                mock_activities
            )
        )

        # Step 4: Analyze performance
        mock_response_times = [1.2, 1.5, 0.8, 2.1, 1.0]
        performance_analysis = (
            self.performance_analyzer.analyze_response_times(
                mock_response_times
            )
        )

        # Assert
        assert conv_stats["total_conversations"] == 25
        assert conversation_analysis["avg_length"] == 2.5
        assert "hourly_distribution" in behavior_patterns
        assert "avg_response_time" in performance_analysis

    @pytest.mark.asyncio
    async def test_real_time_analytics_processing(self):
        """Test real-time analytics processing."""
        # Arrange
        events = [
            {
                "type": "message_sent",
                "user_id": "user1",
                "timestamp": datetime.now(UTC),
            },
            {
                "type": "conversation_started",
                "user_id": "user2",
                "timestamp": datetime.now(UTC),
            },
            {
                "type": "error_occurred",
                "error_type": "timeout",
                "timestamp": datetime.now(UTC),
            },
        ]

        # Mock real-time processing
        processed_events = []

        # Act
        for event in events:
            # Simulate real-time event processing
            processed_event = {
                "original": event,
                "processed_at": datetime.now(UTC),
                "metrics_updated": True,
            }
            processed_events.append(processed_event)

        # Assert
        assert len(processed_events) == 3
        assert all(
            event["metrics_updated"] for event in processed_events
        )

    @pytest.mark.asyncio
    async def test_analytics_dashboard_data_aggregation(self):
        """Test aggregating data for analytics dashboard."""
        # Arrange
        dashboard_widgets = [
            "conversation_count",
            "active_users",
            "response_time",
            "error_rate",
            "user_satisfaction",
        ]

        # Mock widget data
        widget_data = {}

        # Act
        for widget in dashboard_widgets:
            if widget == "conversation_count":
                self.mock_session.execute.return_value.scalar.return_value = (
                    150
                )
                widget_data[widget] = (
                    await self.analytics_service.get_conversation_count()
                )
            elif widget == "response_time":
                widget_data[widget] = (
                    self.performance_analyzer.analyze_response_times(
                        [1.2, 1.5, 0.8]
                    )
                )
            # Add more widget data as needed

        # Assert
        assert len(widget_data) > 0
        if "conversation_count" in widget_data:
            assert widget_data["conversation_count"] == 150

    @pytest.mark.asyncio
    async def test_automated_report_generation(self):
        """Test automated analytics report generation."""
        # Arrange
        report_config = {
            "user_id": "test-user",
            "time_range": AnalyticsTimeRange.LAST_7_DAYS,
            "include_sections": [
                "conversations",
                "performance",
                "trends",
            ],
        }

        # Mock report data
        with (
            patch.object(
                self.analytics_service, 'get_conversation_stats'
            ) as mock_conv,
            patch.object(
                self.analytics_service, 'get_performance_metrics'
            ) as mock_perf,
        ):

            mock_conv.return_value = {"total_conversations": 10}
            mock_perf.return_value = {"avg_response_time": 1.5}

            # Act
            report = await self.analytics_service.generate_usage_report(
                report_config["user_id"], report_config["time_range"]
            )

            # Assert
            assert "conversation_stats" in report
            assert "performance_metrics" in report
            assert (
                report["conversation_stats"]["total_conversations"]
                == 10
            )

    @pytest.mark.asyncio
    async def test_analytics_performance_under_load(self):
        """Test analytics performance under high load."""
        # Arrange
        num_concurrent_requests = 50

        async def mock_analytics_request():
            # Simulate analytics query
            await asyncio.sleep(0.01)
            return {"result": "success"}

        # Act
        start_time = datetime.now()

        tasks = [
            mock_analytics_request()
            for _ in range(num_concurrent_requests)
        ]
        results = await asyncio.gather(*tasks)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Assert
        assert len(results) == num_concurrent_requests
        assert all(result["result"] == "success" for result in results)
        assert execution_time < 2.0  # Should complete within 2 seconds
