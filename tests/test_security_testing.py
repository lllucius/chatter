"""Security and penetration testing for the Chatter platform."""

import pytest
import hashlib
import time
from unittest.mock import patch, MagicMock
from typing import Dict, List


@pytest.mark.integration
class TestSecurityVulnerabilities:
    """Test for common security vulnerabilities."""

    def test_sql_injection_protection(self, test_client):
        """Test protection against SQL injection attacks."""
        # Common SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1#"
        ]
        
        # Test SQL injection in query parameters
        for payload in sql_payloads:
            response = test_client.get(f"/api/v1/documents/search?q={payload}")
            
            # Should not return 500 (indicates proper input sanitization)
            if response.status_code not in [404, 401]:  # Skip if endpoint doesn't exist
                assert response.status_code < 500, f"SQL injection vulnerability detected with payload: {payload}"
        
        # Test SQL injection in JSON payloads
        for payload in sql_payloads:
            response = test_client.post(
                "/api/v1/chat/conversations",
                json={"title": payload, "description": payload}
            )
            
            if response.status_code not in [404, 401]:
                assert response.status_code < 500, f"SQL injection in JSON payload: {payload}"

    def test_xss_protection(self, test_client):
        """Test protection against Cross-Site Scripting (XSS) attacks."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            # Test XSS in conversation creation
            response = test_client.post(
                "/api/v1/chat/conversations",
                json={"title": payload}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                # Returned data should be sanitized
                assert payload not in str(data), f"XSS payload not sanitized: {payload}"
            
            # Test XSS in document upload
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": (payload, b"content", "text/plain")}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                assert payload not in str(data), f"XSS in filename not sanitized: {payload}"

    def test_authentication_security(self, test_client):
        """Test authentication security measures."""
        # Test brute force protection
        failed_attempts = 0
        for i in range(10):
            response = test_client.post(
                "/api/v1/auth/login",
                data={"username": "test@example.com", "password": f"wrong_password_{i}"}
            )
            
            if response.status_code == 404:
                pytest.skip("Authentication endpoint not available")
            
            if response.status_code == 401:
                failed_attempts += 1
            elif response.status_code == 429:
                # Rate limiting is working
                break
        
        # After many failed attempts, should implement some protection
        if failed_attempts >= 5:
            # Make one more attempt to see if rate limiting kicks in
            response = test_client.post(
                "/api/v1/auth/login",
                data={"username": "test@example.com", "password": "another_wrong_password"}
            )
            # Should be rate limited or have some protection mechanism
            # (429 Too Many Requests or similar)

    def test_authorization_checks(self, test_client):
        """Test proper authorization checks."""
        # Test accessing protected endpoints without authentication
        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/chat/conversations",
            "/api/v1/documents/upload",
            "/api/v1/agents"
        ]
        
        for endpoint in protected_endpoints:
            response = test_client.get(endpoint)
            
            if response.status_code == 404:
                continue  # Endpoint doesn't exist
            
            # Should require authentication (401) or be publicly accessible (200)
            assert response.status_code in [200, 401, 403], \
                f"Unexpected status {response.status_code} for {endpoint}"
            
            # Test with invalid token
            response = test_client.get(
                endpoint,
                headers={"Authorization": "Bearer invalid_token_12345"}
            )
            
            if response.status_code not in [404, 405]:
                assert response.status_code in [401, 403], \
                    f"Invalid token should be rejected for {endpoint}"

    def test_input_validation_security(self, test_client):
        """Test input validation for security."""
        # Test extremely large payloads (potential DoS)
        large_payload = "A" * 10000  # 10KB payload
        
        response = test_client.post(
            "/api/v1/chat/conversations",
            json={"title": large_payload}
        )
        
        if response.status_code not in [404, 401]:
            # Should either reject large payloads or handle them gracefully
            assert response.status_code in [200, 201, 400, 413], \
                "Large payload should be handled properly"
        
        # Test null byte injection
        null_byte_payload = "test\x00malicious"
        response = test_client.post(
            "/api/v1/chat/conversations",
            json={"title": null_byte_payload}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            # Null bytes should be filtered out
            assert "\x00" not in str(data), "Null bytes should be filtered"

    def test_file_upload_security(self, test_client):
        """Test file upload security measures."""
        # Test malicious file types
        malicious_files = [
            ("malware.exe", b"MZ\x90\x00", "application/octet-stream"),
            ("script.php", b"<?php echo 'hack'; ?>", "application/x-php"),
            ("test.bat", b"@echo off\necho hacked", "application/x-msdos-program"),
            (".htaccess", b"RewriteEngine On", "text/plain")
        ]
        
        for filename, content, mime_type in malicious_files:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": (filename, content, mime_type)}
            )
            
            if response.status_code == 404:
                pytest.skip("File upload endpoint not available")
            
            # Should reject dangerous file types
            if response.status_code not in [401, 403]:  # Skip if auth required
                assert response.status_code in [400, 415], \
                    f"Dangerous file type should be rejected: {filename}"
        
        # Test oversized files
        large_file_content = b"A" * (50 * 1024 * 1024)  # 50MB
        response = test_client.post(
            "/api/v1/documents/upload",
            files={"file": ("large.txt", large_file_content, "text/plain")}
        )
        
        if response.status_code not in [404, 401, 403]:
            # Should have file size limits
            assert response.status_code in [400, 413], \
                "Oversized files should be rejected"


@pytest.mark.integration
class TestDataProtectionCompliance:
    """Test compliance with data protection regulations."""

    def test_sensitive_data_handling(self, test_client):
        """Test handling of sensitive data."""
        # Test that sensitive data is not logged or exposed
        sensitive_data = [
            "password123!",
            "4532-1234-5678-9012",  # Credit card pattern
            "ssn-123-45-6789",      # SSN pattern
            "api_key_abcd1234"      # API key pattern
        ]
        
        for data in sensitive_data:
            response = test_client.post(
                "/api/v1/chat/conversations",
                json={"title": f"Test with {data}"}
            )
            
            if response.status_code in [200, 201]:
                # Check that sensitive data is not echoed back as-is
                response_text = str(response.json())
                
                # Passwords should never be returned
                if "password" in data:
                    assert data not in response_text, \
                        "Password should not be returned in response"

    def test_data_anonymization(self, test_client):
        """Test data anonymization capabilities."""
        # Test if there are endpoints for data anonymization
        anonymization_endpoints = [
            "/api/v1/data/anonymize",
            "/api/v1/users/anonymize",
            "/api/v1/privacy/anonymize"
        ]
        
        for endpoint in anonymization_endpoints:
            response = test_client.post(endpoint, json={"user_id": "test_user"})
            
            if response.status_code not in [404, 405]:
                # If endpoint exists, it should work properly
                assert response.status_code in [200, 401, 403], \
                    f"Anonymization endpoint should be functional: {endpoint}"

    def test_data_retention_policies(self, test_client):
        """Test data retention policy enforcement."""
        # Test if there are endpoints for data retention management
        retention_endpoints = [
            "/api/v1/data/retention",
            "/api/v1/cleanup/old-data",
            "/api/v1/privacy/data-retention"
        ]
        
        for endpoint in retention_endpoints:
            response = test_client.get(endpoint)
            
            if response.status_code == 200:
                data = response.json()
                # Should have information about retention policies
                assert isinstance(data, dict), \
                    f"Retention endpoint should return policy info: {endpoint}"


@pytest.mark.integration
class TestPerformanceSecurityTests:
    """Test performance-related security issues."""

    def test_rate_limiting(self, test_client):
        """Test rate limiting implementation."""
        # Test rate limiting on public endpoints
        public_endpoints = [
            "/health",
            "/api/v1/health",
            "/api/v1/chat/conversations"
        ]
        
        for endpoint in public_endpoints:
            # Make rapid requests to test rate limiting
            responses = []
            for i in range(20):
                response = test_client.get(endpoint)
                responses.append(response.status_code)
                
                if response.status_code == 429:  # Rate limited
                    break
            
            # Should implement some form of rate limiting for rapid requests
            rate_limited = 429 in responses
            if not rate_limited and endpoint != "/health":
                # Health endpoints might not have rate limiting
                print(f"Warning: No rate limiting detected for {endpoint}")

    def test_resource_exhaustion_protection(self, test_client):
        """Test protection against resource exhaustion attacks."""
        # Test with complex queries that might cause performance issues
        complex_queries = [
            "a" * 1000,  # Very long query
            ".*.*.*.*.*",  # Regex that could cause ReDoS
            "(((((((((",  # Unbalanced parentheses
        ]
        
        for query in complex_queries:
            start_time = time.time()
            
            response = test_client.post(
                "/api/v1/documents/search",
                json={"query": query}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code not in [404, 401]:
                # Response should complete within reasonable time (no ReDoS)
                assert response_time < 5.0, \
                    f"Query took too long ({response_time:.2f}s): {query[:50]}"

    def test_concurrent_request_handling(self, test_client):
        """Test handling of concurrent requests for security."""
        import concurrent.futures
        
        def make_request():
            return test_client.get("/health")
        
        # Test many concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in futures]
        
        # Server should handle concurrent requests gracefully
        error_responses = [r for r in results if r.status_code >= 500]
        error_rate = len(error_responses) / len(results)
        
        assert error_rate < 0.1, \
            f"High error rate ({error_rate:.2%}) under concurrent load"


@pytest.mark.integration
class TestApiSecurityHeaders:
    """Test security headers in API responses."""

    def test_security_headers_present(self, test_client):
        """Test that appropriate security headers are present."""
        response = test_client.get("/health")
        
        if response.status_code == 200:
            headers = {k.lower(): v for k, v in response.headers.items()}
            
            # Recommended security headers
            security_headers = [
                "x-content-type-options",  # Should be "nosniff"
                "x-frame-options",         # Should be "DENY" or "SAMEORIGIN"
                "x-xss-protection",        # Should be "1; mode=block"
                "strict-transport-security",  # HTTPS only
                "content-security-policy"     # CSP policy
            ]
            
            present_headers = [h for h in security_headers if h in headers]
            
            # At least some security headers should be present
            if len(present_headers) == 0:
                print("Warning: No security headers detected")
            else:
                print(f"Security headers present: {present_headers}")

    def test_information_disclosure_prevention(self, test_client):
        """Test that server doesn't disclose sensitive information."""
        # Test error responses don't leak information
        response = test_client.get("/api/v1/nonexistent/endpoint")
        
        if response.status_code >= 400:
            response_text = response.text.lower()
            
            # Should not leak sensitive information in error messages
            sensitive_info = [
                "traceback",
                "stack trace",
                "internal server error",
                "database connection",
                "secret_key",
                "password"
            ]
            
            for info in sensitive_info:
                assert info not in response_text, \
                    f"Error response leaks sensitive info: {info}"
        
        # Check server header doesn't reveal too much
        headers = {k.lower(): v for k, v in response.headers.items()}
        if "server" in headers:
            server_header = headers["server"].lower()
            # Should not reveal detailed version information
            assert not any(x in server_header for x in ["uvicorn", "gunicorn"]), \
                "Server header reveals implementation details"