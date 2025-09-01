"""Tests for analytics API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.main import app


@pytest.mark.unit
class TestAnalyticsEndpoints:
    """Test analytics API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_get_conversation_stats_success(self):
        """Test successful conversation statistics retrieval."""
        # Arrange
        mock_stats = {
            "total_conversations": 156,
            "active_conversations": 23,
            "avg_conversation_length": 8.5,
            "avg_response_time": 1.2,
            "total_messages": 1324,
            "user_satisfaction_avg": 4.3,
            "period": "7d",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-08T00:00:00Z"
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_conversation_stats.return_value = mock_stats
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/analytics/conversations", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["total_conversations"] == 156
                assert response_data["period"] == "7d"
                assert response_data["user_satisfaction_avg"] == 4.3

    def test_get_conversation_stats_with_date_range(self):
        """Test conversation statistics with custom date range."""
        # Arrange
        start_date = "2024-01-01T00:00:00Z"
        end_date = "2024-01-31T23:59:59Z"

        mock_stats = {
            "total_conversations": 450,
            "active_conversations": 67,
            "avg_conversation_length": 12.3,
            "period": "custom",
            "start_date": start_date,
            "end_date": end_date
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_conversation_stats.return_value = mock_stats
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get(
                    f"/api/v1/analytics/conversations?start_date={start_date}&end_date={end_date}",
                    headers=headers
                )

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["total_conversations"] == 450
                assert response_data["start_date"] == start_date

    def test_get_usage_metrics_success(self):
        """Test successful usage metrics retrieval."""
        # Arrange
        mock_metrics = {
            "total_api_calls": 12500,
            "total_tokens_consumed": 850000,
            "unique_users": 245,
            "avg_tokens_per_request": 68,
            "peak_usage_hour": "14:00",
            "api_endpoints_usage": {
                "/api/v1/chat/": 8500,
                "/api/v1/documents/": 2100,
                "/api/v1/agents/": 1900
            },
            "error_rate": 0.02,
            "period": "24h"
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_usage_metrics.return_value = mock_metrics
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/analytics/usage", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["total_api_calls"] == 12500
                assert response_data["unique_users"] == 245
                assert response_data["error_rate"] == 0.02

    def test_get_performance_metrics_success(self):
        """Test successful performance metrics retrieval."""
        # Arrange
        mock_metrics = {
            "avg_response_time": 1.45,
            "p95_response_time": 3.2,
            "p99_response_time": 8.7,
            "throughput_requests_per_second": 45.3,
            "memory_usage_mb": 512,
            "cpu_usage_percent": 23.5,
            "database_connections_active": 12,
            "cache_hit_rate": 0.87,
            "slowest_endpoints": [
                {"endpoint": "/api/v1/documents/process", "avg_time": 4.2},
                {"endpoint": "/api/v1/agents/interact", "avg_time": 2.8}
            ]
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_performance_metrics.return_value = mock_metrics
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/analytics/performance", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["avg_response_time"] == 1.45
                assert response_data["cache_hit_rate"] == 0.87
                assert len(response_data["slowest_endpoints"]) == 2

    def test_get_document_analytics_success(self):
        """Test successful document analytics retrieval."""
        # Arrange
        mock_analytics = {
            "total_documents": 1250,
            "documents_processed_today": 45,
            "avg_processing_time": 2.3,
            "storage_used_gb": 15.7,
            "popular_document_types": [
                {"type": "pdf", "count": 650},
                {"type": "docx", "count": 320},
                {"type": "txt", "count": 280}
            ],
            "processing_status": {
                "completed": 1200,
                "processing": 12,
                "failed": 38
            },
            "embedding_stats": {
                "total_embeddings": 125000,
                "avg_embedding_time": 0.15
            }
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_document_analytics.return_value = mock_analytics
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/analytics/documents", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["total_documents"] == 1250
                assert response_data["storage_used_gb"] == 15.7

    def test_get_system_analytics_success(self):
        """Test successful system analytics retrieval."""
        # Arrange
        mock_analytics = {
            "uptime_seconds": 86400,
            "system_health": "healthy",
            "service_status": {
                "database": "healthy",
                "redis": "healthy",
                "vector_store": "healthy",
                "job_queue": "degraded"
            },
            "resource_usage": {
                "memory_total_gb": 16,
                "memory_used_gb": 8.5,
                "disk_total_gb": 500,
                "disk_used_gb": 127.3,
                "cpu_cores": 8,
                "load_average": [1.2, 1.5, 1.8]
            },
            "recent_alerts": [
                {
                    "level": "warning",
                    "message": "High memory usage detected",
                    "timestamp": "2024-01-01T12:30:00Z"
                }
            ]
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_system_analytics.return_value = mock_analytics
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/analytics/system", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["system_health"] == "healthy"
                assert response_data["service_status"]["job_queue"] == "degraded"

    def test_get_dashboard_data_success(self):
        """Test successful dashboard data retrieval."""
        # Arrange
        mock_dashboard = {
            "overview": {
                "total_users": 1250,
                "active_users_today": 156,
                "total_conversations": 8500,
                "messages_today": 2100
            },
            "performance": {
                "avg_response_time": 1.2,
                "system_health": "healthy",
                "uptime_percentage": 99.8
            },
            "usage": {
                "api_calls_today": 12500,
                "tokens_consumed_today": 850000,
                "documents_processed_today": 45
            },
            "recent_activity": [
                {
                    "type": "conversation_started",
                    "count": 23,
                    "timestamp": "2024-01-01T14:00:00Z"
                },
                {
                    "type": "document_uploaded",
                    "count": 8,
                    "timestamp": "2024-01-01T13:30:00Z"
                }
            ]
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_dashboard_data.return_value = mock_dashboard
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/analytics/dashboard", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["overview"]["total_users"] == 1250
                assert response_data["performance"]["system_health"] == "healthy"

    def test_analytics_unauthorized_access(self):
        """Test analytics access without authentication."""
        # Act
        response = self.client.get("/api/v1/analytics/conversations")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_analytics_invalid_period(self):
        """Test analytics with invalid time period."""
        # Arrange
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_conversation_stats.side_effect = ValueError("Invalid period")
                mock_service.return_value = mock_analytics

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/analytics/conversations?period=invalid", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
class TestAnalyticsIntegration:
    """Integration tests for analytics functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_analytics_data_consistency(self):
        """Test consistency across different analytics endpoints."""
        headers = {"Authorization": "Bearer integration-token"}

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()

                # Mock conversation stats
                mock_analytics.get_conversation_stats.return_value = {
                    "total_conversations": 100,
                    "period": "7d"
                }

                # Mock usage metrics
                mock_analytics.get_usage_metrics.return_value = {
                    "total_api_calls": 5000,
                    "period": "7d"
                }

                # Mock dashboard data
                mock_analytics.get_dashboard_data.return_value = {
                    "overview": {"total_conversations": 100},
                    "usage": {"api_calls_today": 5000}
                }

                mock_service.return_value = mock_analytics

                # Get data from different endpoints
                conv_response = self.client.get("/api/v1/analytics/conversations", headers=headers)
                usage_response = self.client.get("/api/v1/analytics/usage", headers=headers)
                dashboard_response = self.client.get("/api/v1/analytics/dashboard", headers=headers)

                # Verify all responses are successful
                assert conv_response.status_code == status.HTTP_200_OK
                assert usage_response.status_code == status.HTTP_200_OK
                assert dashboard_response.status_code == status.HTTP_200_OK

                # Verify data consistency (in real implementation, these should match)
                conv_data = conv_response.json()
                dashboard_data = dashboard_response.json()

                assert conv_data["total_conversations"] == dashboard_data["overview"]["total_conversations"]

    def test_analytics_performance_tracking(self):
        """Test analytics performance metrics collection."""
        headers = {"Authorization": "Bearer integration-token"}

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.analytics.get_analytics_service') as mock_service:
                mock_analytics = AsyncMock()
                mock_analytics.get_performance_metrics.return_value = {
                    "avg_response_time": 1.2,
                    "throughput_requests_per_second": 50.0,
                    "error_rate": 0.01
                }
                mock_service.return_value = mock_analytics

                # Act
                response = self.client.get("/api/v1/analytics/performance", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()

                # Verify performance metrics are within expected ranges
                assert 0 <= response_data["avg_response_time"] <= 10  # Reasonable response time
                assert 0 <= response_data["error_rate"] <= 1  # Error rate is a percentage
