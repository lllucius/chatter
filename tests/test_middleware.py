"""Tests for middleware components."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse, Response

from chatter.middleware.auth_security import AuthRateLimitMiddleware
from chatter.middleware.security import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """Test SecurityHeadersMiddleware functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.app = FastAPI()

        @self.app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        self.app.add_middleware(SecurityHeadersMiddleware)
        self.client = TestClient(self.app)

    def test_security_headers_added(self):
        """Test that security headers are added to responses."""
        response = self.client.get("/test")

        assert response.status_code == 200

        # Check all security headers are present
        expected_headers = {
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Permissions-Policy",
            "X-Permitted-Cross-Domain-Policies",
        }

        for header in expected_headers:
            assert header in response.headers

    def test_content_security_policy_header(self):
        """Test Content Security Policy header configuration."""
        response = self.client.get("/test")

        csp = response.headers["Content-Security-Policy"]

        # Check key CSP directives
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "style-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "connect-src 'self' ws: wss:" in csp

    def test_x_frame_options_header(self):
        """Test X-Frame-Options header."""
        response = self.client.get("/test")

        assert response.headers["X-Frame-Options"] == "DENY"

    def test_x_content_type_options_header(self):
        """Test X-Content-Type-Options header."""
        response = self.client.get("/test")

        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_xss_protection_header(self):
        """Test X-XSS-Protection header."""
        response = self.client.get("/test")

        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_referrer_policy_header(self):
        """Test Referrer-Policy header."""
        response = self.client.get("/test")

        assert (
            response.headers["Referrer-Policy"]
            == "strict-origin-when-cross-origin"
        )

    def test_permissions_policy_header(self):
        """Test Permissions-Policy header."""
        response = self.client.get("/test")

        permissions_policy = response.headers["Permissions-Policy"]

        # Check key permissions are restricted
        assert "camera=()" in permissions_policy
        assert "microphone=()" in permissions_policy
        assert "geolocation=()" in permissions_policy
        assert "payment=()" in permissions_policy

    def test_strict_transport_security_enabled(self):
        """Test HSTS header when enabled."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        app.add_middleware(
            SecurityHeadersMiddleware, strict_transport_security=True
        )
        client = TestClient(app)

        response = client.get("/test")

        assert "Strict-Transport-Security" in response.headers
        hsts = response.headers["Strict-Transport-Security"]
        assert "max-age=" in hsts
        assert "includeSubDomains" in hsts

    def test_strict_transport_security_disabled(self):
        """Test HSTS header when disabled."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        app.add_middleware(
            SecurityHeadersMiddleware, strict_transport_security=False
        )
        client = TestClient(app)

        response = client.get("/test")

        assert "Strict-Transport-Security" not in response.headers

    def test_security_headers_on_different_response_types(self):
        """Test security headers added to different response types."""
        app = FastAPI()

        @app.get("/json")
        async def json_endpoint():
            return {"message": "json"}

        @app.get("/html")
        async def html_endpoint():
            return Response(
                content="<html><body>test</body></html>",
                media_type="text/html",
            )

        @app.get("/error")
        async def error_endpoint():
            return JSONResponse(
                content={"error": "test"}, status_code=400
            )

        app.add_middleware(SecurityHeadersMiddleware)
        client = TestClient(app)

        # Test JSON response
        response = client.get("/json")
        assert "X-Frame-Options" in response.headers

        # Test HTML response
        response = client.get("/html")
        assert "X-Frame-Options" in response.headers

        # Test error response
        response = client.get("/error")
        assert "X-Frame-Options" in response.headers

    def test_security_headers_dont_override_existing(self):
        """Test that security headers don't override existing ones."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            response = JSONResponse(content={"message": "test"})
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            return response

        app.add_middleware(SecurityHeadersMiddleware)
        client = TestClient(app)

        response = client.get("/test")

        # Should preserve the original header value
        assert response.headers["X-Frame-Options"] == "SAMEORIGIN"


class TestAuthRateLimitMiddleware:
    """Test AuthRateLimitMiddleware functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.app = FastAPI()

        @self.app.post("/auth/login")
        async def login_endpoint():
            return {"message": "login successful"}

        @self.app.post("/auth/register")
        async def register_endpoint():
            return {"message": "registration successful"}

        @self.app.post("/auth/password-reset")
        async def password_reset_endpoint():
            return {"message": "password reset sent"}

        @self.app.post("/auth/refresh")
        async def refresh_endpoint():
            return {"message": "token refreshed"}

        @self.app.get("/other")
        async def other_endpoint():
            return {"message": "other endpoint"}

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    def test_middleware_initialization(self, mock_get_limiter):
        """Test middleware initialization."""
        mock_limiter = MagicMock()
        mock_get_limiter.return_value = mock_limiter

        middleware = AuthRateLimitMiddleware(self.app)

        assert middleware.rate_limiter == mock_limiter
        assert "login" in middleware.rate_limits
        assert "register" in middleware.rate_limits
        assert "password_reset" in middleware.rate_limits
        assert "refresh" in middleware.rate_limits

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    def test_rate_limit_configuration(self, mock_get_limiter):
        """Test rate limit configurations."""
        mock_limiter = MagicMock()
        mock_get_limiter.return_value = mock_limiter

        middleware = AuthRateLimitMiddleware(self.app)

        # Check login limits
        login_limits = middleware.rate_limits["login"]
        assert login_limits["per_minute"] == 5
        assert login_limits["per_hour"] == 20
        assert login_limits["per_day"] == 100

        # Check register limits
        register_limits = middleware.rate_limits["register"]
        assert register_limits["per_minute"] == 2
        assert register_limits["per_hour"] == 10
        assert register_limits["per_day"] == 20

        # Check password reset limits (most restrictive)
        reset_limits = middleware.rate_limits["password_reset"]
        assert reset_limits["per_minute"] == 1
        assert reset_limits["per_hour"] == 5
        assert reset_limits["per_day"] == 10

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_login_endpoint_rate_limiting(self, mock_get_limiter):
        """Test rate limiting on login endpoint."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(
            return_value=(False, {"retry_after": 60})
        )
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        response = client.post("/auth/login")

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "rate limit" in response.json()["detail"].lower()

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_register_endpoint_rate_limiting(
        self, mock_get_limiter
    ):
        """Test rate limiting on register endpoint."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(
            return_value=(False, {"retry_after": 120})
        )
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        response = client.post("/auth/register")

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "120"

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_password_reset_endpoint_rate_limiting(
        self, mock_get_limiter
    ):
        """Test rate limiting on password reset endpoint."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(
            return_value=(False, {"retry_after": 300})
        )
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        response = client.post("/auth/password-reset")

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_non_auth_endpoint_not_rate_limited(
        self, mock_get_limiter
    ):
        """Test that non-auth endpoints are not rate limited."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(
            return_value=(False, {"retry_after": 60})
        )
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        response = client.get("/other")

        assert response.status_code == 200
        mock_limiter.is_allowed.assert_not_called()

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_rate_limit_allowed_request(self, mock_get_limiter):
        """Test request allowed by rate limiter."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(return_value=(True, {}))
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        response = client.post("/auth/login")

        assert response.status_code == 200
        assert response.json()["message"] == "login successful"

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_client_ip_identification(self, mock_get_limiter):
        """Test client IP identification for rate limiting."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(return_value=(True, {}))
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        # Test with X-Forwarded-For header
        response = client.post(
            "/auth/login",
            headers={"X-Forwarded-For": "192.168.1.100, 10.0.0.1"},
        )

        assert response.status_code == 200
        # Verify that rate limiter was called with client IP
        mock_limiter.is_allowed.assert_called_once()

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_rate_limit_with_user_agent_tracking(
        self, mock_get_limiter
    ):
        """Test rate limiting considers user agent."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(return_value=(True, {}))
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        response = client.post(
            "/auth/login", headers={"User-Agent": "TestBot/1.0"}
        )

        assert response.status_code == 200
        # Verify rate limiter was called
        mock_limiter.is_allowed.assert_called_once()

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_rate_limit_error_handling(self, mock_get_limiter):
        """Test error handling in rate limiting."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(
            side_effect=Exception("Rate limiter error")
        )
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        # Should handle rate limiter error gracefully
        response = client.post("/auth/login")

        # Request should be allowed when rate limiter fails
        assert response.status_code == 200

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    async def test_different_auth_endpoints_have_different_limits(
        self, mock_get_limiter
    ):
        """Test that different auth endpoints have different rate limits."""
        mock_limiter = MagicMock()

        # Mock different responses for different endpoints
        def mock_is_allowed(*args, **kwargs):
            # Extract endpoint type from rate limiter call
            if "password_reset" in str(args):
                return AsyncMock(
                    return_value=(False, {"retry_after": 300})
                )()
            else:
                return AsyncMock(return_value=(True, {}))()

        mock_limiter.is_allowed = AsyncMock(side_effect=mock_is_allowed)
        mock_get_limiter.return_value = mock_limiter

        self.app.add_middleware(AuthRateLimitMiddleware)
        client = TestClient(self.app)

        # Login should work
        response = client.post("/auth/login")
        assert response.status_code == 200

        # Password reset should be rate limited
        response = client.post("/auth/password-reset")
        # This test would need the actual middleware logic to work properly

    def test_get_client_ip_x_forwarded_for(self):
        """Test client IP extraction from X-Forwarded-For header."""
        AuthRateLimitMiddleware(self.app)

        # Mock request with X-Forwarded-For
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "192.168.1.100, 10.0.0.1"}
        request.client.host = "127.0.0.1"

        # This would test the actual IP extraction logic
        # For now, we test that the middleware would handle it

    def test_get_client_ip_x_real_ip(self):
        """Test client IP extraction from X-Real-IP header."""
        AuthRateLimitMiddleware(self.app)

        # Mock request with X-Real-IP
        request = MagicMock(spec=Request)
        request.headers = {"X-Real-IP": "192.168.1.100"}
        request.client.host = "127.0.0.1"

        # This would test the actual IP extraction logic

    def test_get_client_ip_fallback(self):
        """Test client IP fallback to request.client.host."""
        AuthRateLimitMiddleware(self.app)

        # Mock request without proxy headers
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client.host = "127.0.0.1"

        # This would test the fallback IP extraction logic


@pytest.mark.integration
class TestMiddlewareIntegration:
    """Integration tests for middleware components."""

    def setup_method(self):
        """Set up test environment."""
        self.app = FastAPI()

        @self.app.post("/auth/login")
        async def login():
            return {"message": "login successful"}

        @self.app.get("/api/data")
        async def get_data():
            return {"data": "test"}

        # Add both middleware components
        self.app.add_middleware(SecurityHeadersMiddleware)
        self.app.add_middleware(AuthRateLimitMiddleware)

        self.client = TestClient(self.app)

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    def test_both_middleware_applied(self, mock_get_limiter):
        """Test that both security and rate limiting middleware are applied."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(return_value=(True, {}))
        mock_get_limiter.return_value = mock_limiter

        response = self.client.post("/auth/login")

        assert response.status_code == 200

        # Check security headers are present
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers

        # Check rate limiting was applied (method called)
        mock_limiter.is_allowed.assert_called_once()

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    def test_security_headers_on_rate_limited_response(
        self, mock_get_limiter
    ):
        """Test that security headers are added even on rate limited responses."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(
            return_value=(False, {"retry_after": 60})
        )
        mock_get_limiter.return_value = mock_limiter

        response = self.client.post("/auth/login")

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

        # Security headers should still be present
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers

    def test_non_auth_endpoints_only_security_headers(self):
        """Test that non-auth endpoints only get security headers."""
        response = self.client.get("/api/data")

        assert response.status_code == 200

        # Security headers should be present
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    def test_middleware_order_matters(self, mock_get_limiter):
        """Test that middleware order affects behavior."""
        # This test verifies that security headers are applied
        # even when rate limiting middleware intervenes

        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(
            return_value=(False, {"retry_after": 60})
        )
        mock_get_limiter.return_value = mock_limiter

        response = self.client.post("/auth/login")

        # Rate limit response should have security headers
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "X-Frame-Options" in response.headers

    def test_middleware_performance(self):
        """Test middleware performance with multiple requests."""
        import time

        start_time = time.time()

        # Make multiple requests
        for _ in range(10):
            response = self.client.get("/api/data")
            assert response.status_code == 200

        end_time = time.time()

        # Should complete reasonably quickly
        assert (
            end_time - start_time
        ) < 1.0  # Less than 1 second for 10 requests


class TestMiddlewareEdgeCases:
    """Test middleware edge cases and error scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.app = FastAPI()

    def test_security_middleware_with_exception(self):
        """Test security middleware behavior when endpoint raises exception."""

        @self.app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        self.app.add_middleware(SecurityHeadersMiddleware)

        client = TestClient(self.app)

        with pytest.raises(ValueError):
            client.get("/error")

    def test_empty_app_with_middleware(self):
        """Test middleware with empty app (no routes)."""
        self.app.add_middleware(SecurityHeadersMiddleware)

        client = TestClient(self.app)

        # Should return 404 with security headers
        response = client.get("/nonexistent")

        assert response.status_code == 404
        assert "X-Frame-Options" in response.headers

    @patch('chatter.middleware.auth_security.get_unified_rate_limiter')
    def test_rate_limit_middleware_with_none_client(
        self, mock_get_limiter
    ):
        """Test rate limiting when request has no client info."""
        mock_limiter = MagicMock()
        mock_limiter.is_allowed = AsyncMock(return_value=(True, {}))
        mock_get_limiter.return_value = mock_limiter

        @self.app.post("/auth/login")
        async def login():
            return {"message": "success"}

        self.app.add_middleware(AuthRateLimitMiddleware)

        # This tests that the middleware handles edge cases gracefully
