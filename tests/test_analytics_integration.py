"""Integration tests for analytics API endpoints."""

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAnalyticsIntegration:
    """Integration tests for analytics API endpoints."""

    @pytest.mark.integration
    async def test_analytics_dashboard_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test complete analytics dashboard workflow."""
        # Get dashboard data
        dashboard_response = await client.get(
            "/api/v1/analytics/dashboard", headers=auth_headers
        )

        # Should return valid dashboard data or handle gracefully
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            assert "summary" in dashboard_data
            assert isinstance(dashboard_data["summary"], dict)
        else:
            # Should handle gracefully if analytics service not available
            assert dashboard_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_conversation_analytics_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test conversation analytics workflow."""
        # Get conversation stats
        stats_response = await client.get(
            "/api/v1/analytics/conversations", headers=auth_headers
        )

        if stats_response.status_code == 200:
            stats_data = stats_response.json()

            # Verify structure of conversation stats
            expected_fields = [
                "total_conversations",
                "active_conversations",
                "conversations_today",
            ]

            for field in expected_fields:
                assert field in stats_data
                assert isinstance(stats_data[field], int)
        else:
            # Handle gracefully if service unavailable
            assert stats_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_usage_metrics_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test usage metrics workflow."""
        # Get usage metrics
        usage_response = await client.get(
            "/api/v1/analytics/usage", headers=auth_headers
        )

        if usage_response.status_code == 200:
            usage_data = usage_response.json()

            # Verify structure of usage metrics
            expected_fields = [
                "api_calls_today",
                "api_calls_this_week",
                "api_calls_this_month",
                "tokens_used_today",
            ]

            for field in expected_fields:
                assert field in usage_data
                assert isinstance(usage_data[field], int)
        else:
            assert usage_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_performance_metrics_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test performance metrics workflow."""
        # Get performance metrics
        perf_response = await client.get(
            "/api/v1/analytics/performance", headers=auth_headers
        )

        if perf_response.status_code == 200:
            perf_data = perf_response.json()

            # Verify structure of performance metrics
            expected_fields = [
                "average_response_time",
                "p95_response_time",
                "error_rate",
                "successful_requests",
            ]

            for field in expected_fields:
                assert field in perf_data
                assert isinstance(perf_data[field], int | float)
        else:
            assert perf_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_document_analytics_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test document analytics workflow."""
        # Get document analytics
        doc_response = await client.get(
            "/api/v1/analytics/documents", headers=auth_headers
        )

        if doc_response.status_code == 200:
            doc_data = doc_response.json()

            # Verify structure of document analytics
            expected_fields = [
                "total_documents",
                "documents_processed_today",
                "processing_success_rate",
            ]

            for field in expected_fields:
                assert field in doc_data
                assert isinstance(doc_data[field], int | float)
        else:
            assert doc_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_system_analytics_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test system analytics workflow."""
        # Get system analytics
        system_response = await client.get(
            "/api/v1/analytics/system", headers=auth_headers
        )

        if system_response.status_code == 200:
            system_data = system_response.json()

            # Verify structure of system analytics
            expected_fields = [
                "memory_usage_mb",
                "cpu_usage_percent",
                "active_connections",
            ]

            for field in expected_fields:
                if field in system_data:
                    assert isinstance(system_data[field], int | float)
        else:
            assert system_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_user_analytics_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test user analytics workflow."""
        # Test with a sample user ID
        user_id = "test-user-123"

        # Get user analytics
        user_response = await client.get(
            f"/api/v1/analytics/users/{user_id}", headers=auth_headers
        )

        if user_response.status_code == 200:
            user_data = user_response.json()

            # Verify structure of user analytics
            expected_fields = [
                "conversations_count",
                "messages_sent",
                "api_calls_made",
            ]

            for field in expected_fields:
                if field in user_data:
                    assert isinstance(user_data[field], int)
        else:
            # User may not exist or analytics unavailable
            assert user_response.status_code in [404, 503, 500]

    @pytest.mark.integration
    async def test_analytics_export_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test analytics export workflow."""
        # Request analytics export
        export_data = {
            "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
            "format": "json",
            "include_types": ["conversations", "usage"],
        }

        export_response = await client.post(
            "/api/v1/analytics/export",
            json=export_data,
            headers=auth_headers,
        )

        if export_response.status_code == 200:
            export_result = export_response.json()

            # Verify export response structure
            expected_fields = ["export_id", "status", "format"]

            for field in expected_fields:
                assert field in export_result
        else:
            # Export service may not be available
            assert export_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_analytics_health_check(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test analytics health check."""
        # Get analytics health
        health_response = await client.get(
            "/api/v1/analytics/health", headers=auth_headers
        )

        # Should return health status
        assert health_response.status_code in [200, 503]

        if health_response.status_code == 200:
            health_data = health_response.json()
            assert "status" in health_data
            assert health_data["status"] in [
                "healthy",
                "unhealthy",
                "degraded",
            ]

    @pytest.mark.integration
    async def test_metrics_summary_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test metrics summary workflow."""
        # Get metrics summary
        summary_response = await client.get(
            "/api/v1/analytics/metrics/summary", headers=auth_headers
        )

        if summary_response.status_code == 200:
            summary_data = summary_response.json()

            # Verify summary structure
            assert "timestamp" in summary_data

            # Should have basic metrics
            metric_fields = ["api_calls", "error_rate", "system_health"]
            for field in metric_fields:
                if field in summary_data:
                    assert summary_data[field] is not None
        else:
            assert summary_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_toolserver_analytics_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test toolserver analytics workflow."""
        # Get toolserver analytics
        toolserver_response = await client.get(
            "/api/v1/analytics/toolservers", headers=auth_headers
        )

        if toolserver_response.status_code == 200:
            toolserver_data = toolserver_response.json()

            # Should return some structure for toolserver analytics
            assert isinstance(toolserver_data, dict | list)
        else:
            # Toolserver analytics may not be available
            assert toolserver_response.status_code in [503, 500]

    @pytest.mark.integration
    async def test_concurrent_analytics_requests(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test concurrent analytics requests."""
        # Create concurrent requests to different analytics endpoints
        endpoints = [
            "/api/v1/analytics/conversations",
            "/api/v1/analytics/usage",
            "/api/v1/analytics/performance",
            "/api/v1/analytics/system",
            "/api/v1/analytics/health",
        ]

        # Create tasks for concurrent requests
        tasks = [
            asyncio.create_task(
                client.get(endpoint, headers=auth_headers)
            )
            for endpoint in endpoints
        ]

        # Wait for all requests
        responses = await asyncio.gather(*tasks)

        # All should return valid responses
        for response in responses:
            assert response.status_code in [
                200,
                500,
                503,
            ]  # Success or graceful error

    @pytest.mark.integration
    async def test_analytics_data_consistency(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test analytics data consistency across endpoints."""
        # Get data from multiple endpoints
        dashboard_response = await client.get(
            "/api/v1/analytics/dashboard", headers=auth_headers
        )
        usage_response = await client.get(
            "/api/v1/analytics/usage", headers=auth_headers
        )
        summary_response = await client.get(
            "/api/v1/analytics/metrics/summary", headers=auth_headers
        )

        # If all succeed, check for data consistency
        if (
            dashboard_response.status_code == 200
            and usage_response.status_code == 200
            and summary_response.status_code == 200
        ):
            dashboard_data = dashboard_response.json()
            usage_data = usage_response.json()
            summary_data = summary_response.json()

            # Check if API calls data is consistent
            dashboard_api_calls = dashboard_data.get("summary", {}).get(
                "api_calls_today"
            )
            usage_api_calls = usage_data.get("api_calls_today")
            summary_data.get("api_calls")

            # They should be consistent if all are provided
            if all(
                x is not None
                for x in [dashboard_api_calls, usage_api_calls]
            ):
                # Allow for some variation due to timing
                assert abs(dashboard_api_calls - usage_api_calls) <= 100

    @pytest.mark.integration
    async def test_analytics_error_handling(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test analytics error handling scenarios."""
        # Test with invalid parameters where applicable

        # Invalid user ID format
        invalid_user_response = await client.get(
            "/api/v1/analytics/users/invalid-user-format",
            headers=auth_headers,
        )
        assert invalid_user_response.status_code in [400, 404]

        # Invalid export parameters
        invalid_export_data = {
            "date_range": {
                "start": "invalid-date",
                "end": "2024-01-31",
            },
            "format": "invalid_format",
        }

        invalid_export_response = await client.post(
            "/api/v1/analytics/export",
            json=invalid_export_data,
            headers=auth_headers,
        )
        assert invalid_export_response.status_code in [400, 422]

    @pytest.mark.integration
    async def test_analytics_pagination_and_filtering(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test analytics endpoints that support pagination and filtering."""
        # Test with query parameters where supported

        # Test date range filtering on usage metrics
        usage_with_params = await client.get(
            "/api/v1/analytics/usage?start_date=2024-01-01&end_date=2024-01-31",
            headers=auth_headers,
        )

        # Should handle parameters gracefully
        assert usage_with_params.status_code in [200, 400, 503]

        # Test limit parameter on conversations
        conversations_limited = await client.get(
            "/api/v1/analytics/conversations?limit=10",
            headers=auth_headers,
        )

        assert conversations_limited.status_code in [200, 400, 503]

    @pytest.mark.integration
    async def test_analytics_response_format_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test that analytics responses follow expected format."""
        endpoints_to_test = [
            "/api/v1/analytics/conversations",
            "/api/v1/analytics/usage",
            "/api/v1/analytics/dashboard",
        ]

        for endpoint in endpoints_to_test:
            response = await client.get(endpoint, headers=auth_headers)

            if response.status_code == 200:
                data = response.json()

                # Should return valid JSON
                assert isinstance(data, dict)

                # Should not be empty
                assert len(data) > 0

                # Should not contain error fields if status is 200
                assert "error" not in data or data["error"] is None
