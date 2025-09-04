"""Unit tests for analytics API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient


class TestAnalyticsUnit:
    """Unit tests for analytics API endpoints."""

    @pytest.mark.unit
    async def test_get_conversation_stats_requires_auth(self, client: AsyncClient):
        """Test that getting conversation stats requires authentication."""
        response = await client.get("/api/v1/analytics/conversations")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_usage_metrics_requires_auth(self, client: AsyncClient):
        """Test that getting usage metrics requires authentication."""
        response = await client.get("/api/v1/analytics/usage")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_performance_metrics_requires_auth(self, client: AsyncClient):
        """Test that getting performance metrics requires authentication."""
        response = await client.get("/api/v1/analytics/performance")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_document_analytics_requires_auth(self, client: AsyncClient):
        """Test that getting document analytics requires authentication."""
        response = await client.get("/api/v1/analytics/documents")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_system_analytics_requires_auth(self, client: AsyncClient):
        """Test that getting system analytics requires authentication."""
        response = await client.get("/api/v1/analytics/system")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_dashboard_requires_auth(self, client: AsyncClient):
        """Test that getting dashboard requires authentication."""
        response = await client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_toolserver_analytics_requires_auth(self, client: AsyncClient):
        """Test that getting toolserver analytics requires authentication."""
        response = await client.get("/api/v1/analytics/toolservers")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_user_analytics_requires_auth(self, client: AsyncClient):
        """Test that getting user analytics requires authentication."""
        response = await client.get("/api/v1/analytics/users/user-123")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_export_analytics_requires_auth(self, client: AsyncClient):
        """Test that exporting analytics requires authentication."""
        response = await client.post("/api/v1/analytics/export", json={})
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_health_requires_auth(self, client: AsyncClient):
        """Test that getting analytics health requires authentication."""
        response = await client.get("/api/v1/analytics/health")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_metrics_summary_requires_auth(self, client: AsyncClient):
        """Test that getting metrics summary requires authentication."""
        response = await client.get("/api/v1/analytics/metrics/summary")
        assert response.status_code == 401

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_conversation_stats_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful conversation stats retrieval."""
        # Mock analytics service
        mock_service = AsyncMock()
        mock_stats = {
            "total_conversations": 150,
            "active_conversations": 12,
            "conversations_today": 8,
            "average_messages_per_conversation": 4.5,
            "conversations_by_hour": [1, 2, 0, 3, 5, 2, 4, 1, 0, 2, 3, 6],
            "top_conversation_topics": [
                {"topic": "technical_support", "count": 45},
                {"topic": "general_inquiry", "count": 38}
            ]
        }
        mock_service.get_conversation_stats.return_value = mock_stats
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/conversations", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_conversations"] == 150
        assert data["active_conversations"] == 12
        assert len(data["conversations_by_hour"]) == 12
        assert len(data["top_conversation_topics"]) == 2

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_usage_metrics_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful usage metrics retrieval."""
        mock_service = AsyncMock()
        mock_metrics = {
            "api_calls_today": 1250,
            "api_calls_this_week": 8500,
            "api_calls_this_month": 35000,
            "tokens_used_today": 125000,
            "tokens_used_this_week": 850000,
            "tokens_used_this_month": 3500000,
            "top_endpoints": [
                {"endpoint": "/chat/completions", "calls": 500},
                {"endpoint": "/documents/process", "calls": 300}
            ],
            "usage_by_hour": [10, 15, 8, 25, 35, 42, 38, 28, 20, 18, 25, 30]
        }
        mock_service.get_usage_metrics.return_value = mock_metrics
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/usage", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["api_calls_today"] == 1250
        assert data["tokens_used_today"] == 125000
        assert len(data["top_endpoints"]) == 2
        assert len(data["usage_by_hour"]) == 12

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_performance_metrics_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful performance metrics retrieval."""
        mock_service = AsyncMock()
        mock_metrics = {
            "average_response_time": 245.6,
            "p95_response_time": 450.2,
            "p99_response_time": 850.1,
            "error_rate": 0.02,
            "successful_requests": 9850,
            "failed_requests": 150,
            "response_times_by_hour": [200, 210, 195, 220, 250, 240, 235, 225, 215, 205, 230, 245],
            "slowest_endpoints": [
                {"endpoint": "/documents/process", "avg_time": 1250.5},
                {"endpoint": "/chat/completions", "avg_time": 180.3}
            ]
        }
        mock_service.get_performance_metrics.return_value = mock_metrics
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/performance", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["average_response_time"] == 245.6
        assert data["error_rate"] == 0.02
        assert len(data["slowest_endpoints"]) == 2

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_document_analytics_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful document analytics retrieval."""
        mock_service = AsyncMock()
        mock_analytics = {
            "total_documents": 450,
            "documents_processed_today": 25,
            "processing_success_rate": 0.95,
            "average_processing_time": 2.4,
            "documents_by_type": {
                "pdf": 200,
                "docx": 150,
                "txt": 100
            },
            "processing_status_breakdown": {
                "completed": 425,
                "processing": 15,
                "failed": 10
            }
        }
        mock_service.get_document_analytics.return_value = mock_analytics
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/documents", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_documents"] == 450
        assert data["processing_success_rate"] == 0.95
        assert "documents_by_type" in data

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_system_analytics_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful system analytics retrieval."""
        mock_service = AsyncMock()
        mock_analytics = {
            "uptime_seconds": 3600000,
            "memory_usage_mb": 1024,
            "cpu_usage_percent": 25.5,
            "disk_usage_percent": 45.2,
            "active_connections": 150,
            "database_connections": 25,
            "cache_hit_rate": 0.85,
            "system_health": "healthy"
        }
        mock_service.get_system_analytics.return_value = mock_analytics
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/system", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["cpu_usage_percent"] == 25.5
        assert data["cache_hit_rate"] == 0.85
        assert data["system_health"] == "healthy"

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_dashboard_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful dashboard data retrieval."""
        mock_service = AsyncMock()
        mock_dashboard = {
            "summary": {
                "total_users": 125,
                "active_users": 45,
                "total_conversations": 350,
                "api_calls_today": 1250
            },
            "recent_activity": [
                {"timestamp": "2024-01-01T12:00:00Z", "event": "User login", "user": "user1"},
                {"timestamp": "2024-01-01T11:55:00Z", "event": "Document processed", "user": "user2"}
            ],
            "alerts": [
                {"level": "warning", "message": "High API usage detected", "timestamp": "2024-01-01T12:05:00Z"}
            ]
        }
        mock_service.get_dashboard_data.return_value = mock_dashboard
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"]["total_users"] == 125
        assert len(data["recent_activity"]) == 2
        assert len(data["alerts"]) == 1

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_user_analytics_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful user analytics retrieval."""
        mock_service = AsyncMock()
        mock_user_analytics = {
            "user_id": "user-123",
            "conversations_count": 25,
            "messages_sent": 150,
            "documents_uploaded": 8,
            "api_calls_made": 500,
            "tokens_used": 50000,
            "activity_by_day": {
                "2024-01-01": 10,
                "2024-01-02": 15,
                "2024-01-03": 8
            }
        }
        mock_service.get_user_analytics.return_value = mock_user_analytics
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/users/user-123", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "user-123"
        assert data["conversations_count"] == 25
        assert "activity_by_day" in data

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_export_analytics_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful analytics export."""
        mock_service = AsyncMock()
        mock_export_result = {
            "export_id": "export-123",
            "status": "completed",
            "download_url": "https://example.com/download/export-123",
            "format": "csv",
            "records_count": 1000
        }
        mock_service.export_analytics.return_value = mock_export_result
        mock_analytics_service.return_value = mock_service
        
        export_data = {
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            },
            "format": "csv",
            "include_types": ["conversations", "usage", "performance"]
        }
        
        response = await client.post("/api/v1/analytics/export", json=export_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["export_id"] == "export-123"
        assert data["status"] == "completed"
        assert data["records_count"] == 1000

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_analytics_service_error_handling(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test analytics service error handling."""
        mock_service = AsyncMock()
        mock_service.get_conversation_stats.side_effect = Exception("Analytics service error")
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/conversations", headers=auth_headers)
        assert response.status_code == 500

    @pytest.mark.unit
    async def test_invalid_user_id_format(self, client: AsyncClient, auth_headers: dict):
        """Test user analytics with invalid user ID format."""
        # This would depend on validation logic in the API
        response = await client.get("/api/v1/analytics/users/invalid-user-id", headers=auth_headers)
        # Should return appropriate error code based on validation
        assert response.status_code in [400, 404]

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_metrics_summary_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful metrics summary retrieval."""
        mock_service = AsyncMock()
        mock_summary = {
            "timestamp": "2024-01-01T12:00:00Z",
            "api_calls": 1250,
            "error_rate": 0.02,
            "avg_response_time": 245.6,
            "active_users": 45,
            "system_health": "healthy",
            "alerts_count": 2
        }
        mock_service.get_metrics_summary.return_value = mock_summary
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/metrics/summary", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["api_calls"] == 1250
        assert data["system_health"] == "healthy"
        assert data["alerts_count"] == 2

    @pytest.mark.unit
    @patch('chatter.api.analytics.AnalyticsService')
    async def test_get_health_success(self, mock_analytics_service, client: AsyncClient, auth_headers: dict):
        """Test successful analytics health check."""
        mock_service = AsyncMock()
        mock_health = {
            "status": "healthy",
            "services": {
                "database": "healthy",
                "cache": "healthy",
                "analytics_engine": "healthy"
            },
            "last_updated": "2024-01-01T12:00:00Z"
        }
        mock_service.get_health_status.return_value = mock_health
        mock_analytics_service.return_value = mock_service
        
        response = await client.get("/api/v1/analytics/health", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data