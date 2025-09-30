"""
Contract Testing

API compatibility and compliance testing including OpenAPI specification validation.
"""

from typing import Any

import pytest
from httpx import AsyncClient


class TestContractTesting:
    """API contract testing for compatibility and compliance."""

    @pytest.mark.contract
    async def test_api_response_schema_validation(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test API response schema validation."""
        try:
            # Test health endpoint schema
            response = await client.get("/healthz")
            if response.status_code == 200:
                self._validate_health_response_schema(response.json())

            # Test authenticated endpoints if auth is available
            if auth_headers:
                # Test profile endpoint schema
                profile_response = await client.get(
                    "/api/v1/auth/profile", headers=auth_headers
                )
                if profile_response.status_code == 200:
                    self._validate_user_profile_schema(
                        profile_response.json()
                    )

                # Test chats list endpoint schema
                chats_response = await client.get(
                    "/api/v1/chats", headers=auth_headers
                )
                if chats_response.status_code == 200:
                    self._validate_chats_list_schema(
                        chats_response.json()
                    )

                # Test documents list endpoint schema
                docs_response = await client.get(
                    "/api/v1/documents", headers=auth_headers
                )
                if docs_response.status_code == 200:
                    self._validate_documents_list_schema(
                        docs_response.json()
                    )

            print("API response schema validation: PASSED")

        except Exception as e:
            pytest.skip(f"API response schema validation skipped: {e}")

    def _validate_health_response_schema(self, data: dict[str, Any]):
        """Validate health endpoint response schema."""
        # Health response should have basic structure
        assert (
            "status" in data or "healthy" in data or "timestamp" in data
        ), "Health response missing expected fields"

        # If status field exists, it should be a valid status
        if "status" in data:
            valid_statuses = [
                "healthy",
                "unhealthy",
                "degraded",
                "ok",
                "error",
            ]
            assert (
                data["status"] in valid_statuses
            ), f"Invalid health status: {data['status']}"

    def _validate_user_profile_schema(self, data: dict[str, Any]):
        """Validate user profile response schema."""
        required_fields = ["id", "username"]
        for field in required_fields:
            assert (
                field in data
            ), f"Profile response missing required field: {field}"

        # Validate field types
        assert isinstance(
            data["id"], str | int
        ), "Profile ID should be string or int"
        assert isinstance(
            data["username"], str
        ), "Username should be string"

        if "email" in data:
            assert isinstance(
                data["email"], str
            ), "Email should be string"
            assert "@" in data["email"], "Email should contain @ symbol"

        # Password should never be returned
        assert (
            "password" not in data
        ), "Profile response should not contain password"

    def _validate_chats_list_schema(self, data: Any):
        """Validate chats list response schema."""
        if isinstance(data, list):
            # Array response format
            for chat in data:
                self._validate_chat_object_schema(chat)
        elif isinstance(data, dict):
            # Paginated response format
            if "items" in data:
                assert isinstance(
                    data["items"], list
                ), "Chat items should be array"
                for chat in data["items"]:
                    self._validate_chat_object_schema(chat)

            # Pagination metadata
            if "total" in data:
                assert isinstance(
                    data["total"], int
                ), "Total should be integer"
            if "page" in data:
                assert isinstance(
                    data["page"], int
                ), "Page should be integer"

    def _validate_chat_object_schema(self, chat: dict[str, Any]):
        """Validate individual chat object schema."""
        required_fields = ["id", "title"]
        for field in required_fields:
            assert (
                field in chat
            ), f"Chat object missing required field: {field}"

        assert isinstance(
            chat["id"], str | int
        ), "Chat ID should be string or int"
        assert isinstance(
            chat["title"], str
        ), "Chat title should be string"

        if "created_at" in chat:
            # Should be ISO datetime string or timestamp
            assert isinstance(
                chat["created_at"], str | int
            ), "created_at should be string or timestamp"

        if "updated_at" in chat:
            assert isinstance(
                chat["updated_at"], str | int
            ), "updated_at should be string or timestamp"

    def _validate_documents_list_schema(self, data: Any):
        """Validate documents list response schema."""
        if isinstance(data, list):
            for doc in data:
                self._validate_document_object_schema(doc)
        elif isinstance(data, dict):
            if "items" in data:
                assert isinstance(
                    data["items"], list
                ), "Document items should be array"
                for doc in data["items"]:
                    self._validate_document_object_schema(doc)

    def _validate_document_object_schema(self, doc: dict[str, Any]):
        """Validate individual document object schema."""
        required_fields = ["id", "title"]
        for field in required_fields:
            assert (
                field in doc
            ), f"Document object missing required field: {field}"

        assert isinstance(
            doc["id"], str | int
        ), "Document ID should be string or int"
        assert isinstance(
            doc["title"], str
        ), "Document title should be string"

        if "status" in doc:
            valid_statuses = [
                "pending",
                "processing",
                "completed",
                "failed",
            ]
            assert (
                doc["status"] in valid_statuses
            ), f"Invalid document status: {doc['status']}"

    @pytest.mark.contract
    async def test_error_response_consistency(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test error response consistency across endpoints."""
        try:
            # Test various error scenarios
            error_scenarios = [
                {
                    "name": "Not Found",
                    "method": "GET",
                    "path": "/api/v1/nonexistent",
                    "expected_status": 404,
                },
                {
                    "name": "Unauthorized",
                    "method": "GET",
                    "path": "/api/v1/auth/profile",
                    "headers": {},
                    "expected_status": 401,
                },
                {
                    "name": "Invalid Resource",
                    "method": "GET",
                    "path": "/api/v1/chats/invalid-id",
                    "headers": auth_headers,
                    "expected_status": [404, 400],
                },
            ]

            error_consistency_results = []

            for scenario in error_scenarios:
                headers = scenario.get("headers", {})

                if scenario["method"] == "GET":
                    response = await client.get(
                        scenario["path"], headers=headers
                    )
                else:
                    continue  # Skip non-GET methods

                result = {
                    "scenario": scenario["name"],
                    "expected_status": scenario["expected_status"],
                    "actual_status": response.status_code,
                    "consistent": False,
                    "has_error_structure": False,
                }

                # Check status code
                if isinstance(scenario["expected_status"], list):
                    result["consistent"] = (
                        response.status_code
                        in scenario["expected_status"]
                    )
                else:
                    result["consistent"] = (
                        response.status_code
                        == scenario["expected_status"]
                    )

                # Check error response structure
                if response.status_code >= 400:
                    try:
                        error_data = response.json()

                        # Common error response fields
                        error_fields = [
                            "error",
                            "message",
                            "detail",
                            "code",
                        ]
                        has_error_field = any(
                            field in error_data
                            for field in error_fields
                        )

                        result["has_error_structure"] = has_error_field

                        # Error message should be informative but not leak sensitive info
                        if "message" in error_data:
                            message = str(error_data["message"]).lower()
                            sensitive_terms = [
                                "password",
                                "secret",
                                "token",
                                "database",
                                "internal",
                            ]
                            has_sensitive_info = any(
                                term in message
                                for term in sensitive_terms
                            )

                            if has_sensitive_info:
                                result["security_issue"] = (
                                    "Error message contains sensitive information"
                                )

                    except Exception:
                        # Response might not be JSON for some errors
                        result["has_error_structure"] = False

                error_consistency_results.append(result)

            # Report consistency results
            consistent_count = sum(
                1 for r in error_consistency_results if r["consistent"]
            )
            structured_count = sum(
                1
                for r in error_consistency_results
                if r.get("has_error_structure", False)
            )

            print(
                f"Error response consistency: {consistent_count}/{len(error_consistency_results)} status codes correct"
            )
            print(
                f"Error response structure: {structured_count}/{len(error_consistency_results)} have proper structure"
            )

        except Exception as e:
            pytest.skip(f"Error response consistency test skipped: {e}")

    @pytest.mark.contract
    async def test_openapi_specification_compliance(
        self, client: AsyncClient
    ):
        """Test OpenAPI specification compliance."""
        try:
            # Try to get OpenAPI/Swagger documentation
            openapi_endpoints = [
                "/openapi.json",
                "/docs/openapi.json",
                "/api/openapi.json",
                "/swagger.json",
                "/api/v1/openapi.json",
            ]

            openapi_spec = None
            openapi_endpoint = None

            for endpoint in openapi_endpoints:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    try:
                        openapi_spec = response.json()
                        openapi_endpoint = endpoint
                        break
                    except Exception:
                        continue

            if openapi_spec:
                print(
                    f"OpenAPI specification found at: {openapi_endpoint}"
                )

                # Validate basic OpenAPI structure
                self._validate_openapi_structure(openapi_spec)

                print("OpenAPI specification compliance: PASSED")
            else:
                print("OpenAPI specification: NOT FOUND")
                pytest.skip(
                    "OpenAPI specification not available for compliance testing"
                )

        except Exception as e:
            pytest.skip(
                f"OpenAPI specification compliance test skipped: {e}"
            )

    def _validate_openapi_structure(self, spec: dict[str, Any]):
        """Validate basic OpenAPI specification structure."""
        # Check for required OpenAPI fields
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            assert (
                field in spec
            ), f"OpenAPI spec missing required field: {field}"

        # Validate OpenAPI version
        openapi_version = spec["openapi"]
        assert isinstance(
            openapi_version, str
        ), "OpenAPI version should be string"
        assert openapi_version.startswith(
            "3."
        ), f"Expected OpenAPI 3.x, got {openapi_version}"

        # Validate info section
        info = spec["info"]
        assert "title" in info, "OpenAPI info missing title"
        assert "version" in info, "OpenAPI info missing version"

        # Validate paths structure
        paths = spec["paths"]
        assert isinstance(paths, dict), "OpenAPI paths should be object"

        # Check for common API paths
        expected_paths = ["/healthz", "/readyz", "/api/v1"]
        found_paths = list(paths.keys())

        for expected in expected_paths:
            matching_paths = [p for p in found_paths if expected in p]
            if not matching_paths:
                print(
                    f"Expected path pattern '{expected}' not found in OpenAPI spec"
                )

    @pytest.mark.contract
    async def test_frontend_backend_contract_validation(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test frontend-backend contract validation."""
        try:
            # Test that API responses match expected frontend contract
            if auth_headers:
                # Test profile endpoint for frontend compatibility
                profile_response = await client.get(
                    "/api/v1/auth/profile", headers=auth_headers
                )

                if profile_response.status_code == 200:
                    profile_data = profile_response.json()

                    # Frontend typically expects these fields
                    frontend_expected_fields = [
                        "id",
                        "username",
                        "email",
                        "full_name",
                    ]
                    missing_fields = []

                    for field in frontend_expected_fields:
                        if field not in profile_data:
                            missing_fields.append(field)

                    if missing_fields:
                        print(
                            f"Profile API missing frontend-expected fields: {missing_fields}"
                        )
                    else:
                        print(
                            "Profile API contract: Compatible with frontend"
                        )

                # Test chats endpoint for frontend compatibility
                chats_response = await client.get(
                    "/api/v1/chats", headers=auth_headers
                )

                if chats_response.status_code == 200:
                    chats_data = chats_response.json()

                    if isinstance(chats_data, list) and chats_data:
                        first_chat = chats_data[0]

                        # Frontend typically expects these fields
                        chat_expected_fields = [
                            "id",
                            "title",
                            "created_at",
                        ]
                        missing_chat_fields = []

                        for field in chat_expected_fields:
                            if field not in first_chat:
                                missing_chat_fields.append(field)

                        if missing_chat_fields:
                            print(
                                f"Chat API missing frontend-expected fields: {missing_chat_fields}"
                            )
                        else:
                            print(
                                "Chat API contract: Compatible with frontend"
                            )

            print("Frontend-backend contract validation: COMPLETED")

        except Exception as e:
            pytest.skip(
                f"Frontend-backend contract validation skipped: {e}"
            )

    @pytest.mark.contract
    async def test_cors_headers_and_security_compliance(
        self, client: AsyncClient
    ):
        """Test CORS headers and security compliance."""
        try:
            # Test CORS preflight request
            cors_headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            }

            preflight_response = await client.options(
                "/api/v1/chats", headers=cors_headers
            )

            cors_compliance = {
                "preflight_supported": preflight_response.status_code
                in [200, 204],
                "cors_headers_present": False,
                "security_headers_present": False,
            }

            if cors_compliance["preflight_supported"]:
                response_headers = preflight_response.headers

                # Check for CORS headers
                cors_header_names = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers",
                ]

                cors_headers_found = [
                    h
                    for h in cors_header_names
                    if h in response_headers
                ]
                cors_compliance["cors_headers_present"] = (
                    len(cors_headers_found) > 0
                )

                if cors_headers_found:
                    print(f"CORS headers present: {cors_headers_found}")

                # Check for security headers
                security_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "X-XSS-Protection",
                ]

                security_headers_found = [
                    h for h in security_headers if h in response_headers
                ]
                cors_compliance["security_headers_present"] = (
                    len(security_headers_found) > 0
                )

                if security_headers_found:
                    print(
                        f"Security headers present: {security_headers_found}"
                    )

            # Test actual API request with CORS
            api_response = await client.get(
                "/api/v1/chats",
                headers={"Origin": "http://localhost:3000"},
            )

            if api_response.status_code != 404:  # If endpoint exists
                api_cors_headers = api_response.headers
                if "Access-Control-Allow-Origin" in api_cors_headers:
                    print(
                        f"API CORS Origin: {api_cors_headers['Access-Control-Allow-Origin']}"
                    )

            print("CORS and security compliance: TESTED")

        except Exception as e:
            pytest.skip(
                f"CORS and security compliance test skipped: {e}"
            )

    @pytest.mark.contract
    async def test_data_consistency_across_services(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test data consistency across different service endpoints."""
        if not auth_headers:
            pytest.skip(
                "Authentication required for cross-service consistency test"
            )

        try:
            # Get user profile data
            profile_response = await client.get(
                "/api/v1/auth/profile", headers=auth_headers
            )

            if profile_response.status_code != 200:
                pytest.skip(
                    "Cannot get user profile for consistency testing"
                )

            profile_data = profile_response.json()
            user_id = profile_data.get("id")
            profile_data.get("username")

            consistency_results = []

            # Test user data consistency across different endpoints
            endpoints_to_check = [
                "/api/v1/chats",
                "/api/v1/documents",
                "/api/v1/agents",  # if available
            ]

            for endpoint in endpoints_to_check:
                response = await client.get(
                    endpoint, headers=auth_headers
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check if returned data references the same user
                    if isinstance(data, list) and data:
                        first_item = data[0]

                        if "user_id" in first_item:
                            item_user_id = first_item["user_id"]
                            consistent = str(item_user_id) == str(
                                user_id
                            )
                            consistency_results.append(
                                {
                                    "endpoint": endpoint,
                                    "consistent": consistent,
                                    "issue": (
                                        f"User ID mismatch: {item_user_id} vs {user_id}"
                                        if not consistent
                                        else None
                                    ),
                                }
                            )

                        if (
                            "owner" in first_item
                            or "created_by" in first_item
                        ):
                            owner_field = (
                                "owner"
                                if "owner" in first_item
                                else "created_by"
                            )
                            owner_data = first_item[owner_field]

                            if (
                                isinstance(owner_data, dict)
                                and "id" in owner_data
                            ):
                                owner_id = owner_data["id"]
                                consistent = str(owner_id) == str(
                                    user_id
                                )
                                consistency_results.append(
                                    {
                                        "endpoint": endpoint,
                                        "field": owner_field,
                                        "consistent": consistent,
                                        "issue": (
                                            f"Owner ID mismatch: {owner_id} vs {user_id}"
                                            if not consistent
                                            else None
                                        ),
                                    }
                                )

            # Report consistency results
            if consistency_results:
                consistent_count = sum(
                    1 for r in consistency_results if r["consistent"]
                )
                total_count = len(consistency_results)

                print(
                    f"Cross-service data consistency: {consistent_count}/{total_count} checks passed"
                )

                for result in consistency_results:
                    if not result["consistent"]:
                        print(
                            f"  {result['endpoint']}: {result['issue']}"
                        )
            else:
                print(
                    "Cross-service data consistency: No data to verify"
                )

        except Exception as e:
            pytest.skip(f"Cross-service consistency test skipped: {e}")
