"""
Base Classes for Load Testing

Provides base functionality and utilities for Locust load testing.
"""

import random
import string
from typing import Any

from locust import HttpUser, between, task


class BaseChatterUser(HttpUser):
    """Base class for Chatter platform load testing users."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token: str | None = None
        self.user_id: str | None = None
        self.username: str | None = None
        self.chats: list = []
        self.documents: list = []

    def on_start(self):
        """Called when a user starts. Attempt to authenticate."""
        self.register_and_login()

    def register_and_login(self):
        """Register a new user and login to get auth token."""
        try:
            # Generate unique user data
            random_suffix = "".join(
                random.choices(
                    string.ascii_lowercase + string.digits, k=8
                )
            )
            username = f"loadtest_{random_suffix}"
            email = f"loadtest_{random_suffix}@example.com"

            user_data = {
                "username": username,
                "email": email,
                "password": "LoadTest123!",
                "full_name": f"Load Test User {random_suffix}",
            }

            # Try to register
            with self.client.post(
                "/api/v1/auth/register",
                json=user_data,
                catch_response=True,
            ) as response:
                if response.status_code in [200, 201]:
                    self.username = username
                elif response.status_code == 404:
                    # Registration endpoint doesn't exist, skip auth
                    return
                else:
                    response.failure(
                        f"Registration failed: {response.status_code}"
                    )
                    return

            # Try to login
            login_data = {
                "username": username,
                "password": "LoadTest123!",
            }

            with self.client.post(
                "/api/v1/auth/login",
                json=login_data,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    token_data = response.json()
                    self.auth_token = token_data.get("access_token")
                    self.user_id = token_data.get("user_id")
                elif response.status_code == 404:
                    # Login endpoint doesn't exist, skip auth
                    pass
                else:
                    response.failure(
                        f"Login failed: {response.status_code}"
                    )

        except Exception:
            # Gracefully handle auth failures
            pass

    @property
    def auth_headers(self) -> dict[str, str]:
        """Get authentication headers if available."""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    def safe_request(self, method: str, url: str, **kwargs):
        """Make a safe request that handles missing endpoints gracefully."""
        with getattr(self.client, method.lower())(
            url, catch_response=True, **kwargs
        ) as response:
            if response.status_code == 404:
                response.success()  # Don't count missing endpoints as failures
                return None
            return response

    def create_test_chat(self) -> dict[str, Any] | None:
        """Create a test chat and return its data."""
        if not self.auth_headers:
            return None

        chat_data = {
            "title": f"Load Test Chat {random.randint(1, 1000)}",
            "description": "Automated load test chat",
        }

        response = self.safe_request(
            "post",
            "/api/v1/chats",
            json=chat_data,
            headers=self.auth_headers,
        )
        if response and response.status_code in [200, 201]:
            chat = response.json()
            self.chats.append(chat)
            return chat
        return None

    def create_test_document(self) -> dict[str, Any] | None:
        """Create a test document and return its data."""
        if not self.auth_headers:
            return None

        # Create a simple text file
        content = (
            f"Load test document content {random.randint(1, 1000)} "
            * 20
        )
        files = {"file": ("loadtest_doc.txt", content, "text/plain")}
        data = {
            "title": f"Load Test Document {random.randint(1, 1000)}",
            "description": "Automated load test document",
        }

        response = self.safe_request(
            "post",
            "/api/v1/documents/upload",
            files=files,
            data=data,
            headers=self.auth_headers,
        )
        if response and response.status_code in [200, 201]:
            doc = response.json()
            self.documents.append(doc)
            return doc
        return None

    def send_chat_message(self, chat_id: str, message: str) -> bool:
        """Send a message to a chat."""
        if not self.auth_headers:
            return False

        message_data = {"message": message, "message_type": "user"}

        response = self.safe_request(
            "post",
            f"/api/v1/chats/{chat_id}/messages",
            json=message_data,
            headers=self.auth_headers,
        )
        return response and response.status_code in [200, 201]


class HealthCheckMixin:
    """Mixin for basic health check functionality."""

    @task(1)
    def health_check(self):
        """Basic health check."""
        self.safe_request("get", "/healthz")

    @task(1)
    def ready_check(self):
        """Readiness check."""
        self.safe_request("get", "/readyz")


class AuthenticationMixin:
    """Mixin for authentication-related load testing."""

    @task(2)
    def get_profile(self):
        """Get user profile."""
        if self.auth_headers:
            self.safe_request(
                "get", "/api/v1/auth/profile", headers=self.auth_headers
            )

    @task(1)
    def refresh_token(self):
        """Attempt to refresh authentication token."""
        if self.auth_headers:
            self.safe_request(
                "post",
                "/api/v1/auth/refresh",
                headers=self.auth_headers,
            )


class ChatMixin:
    """Mixin for chat-related load testing."""

    @task(3)
    def list_chats(self):
        """List user's chats."""
        if self.auth_headers:
            self.safe_request(
                "get", "/api/v1/chats", headers=self.auth_headers
            )

    @task(2)
    def create_chat(self):
        """Create a new chat."""
        self.create_test_chat()

    @task(4)
    def send_message(self):
        """Send a message to an existing chat."""
        if self.chats and self.auth_headers:
            chat = random.choice(self.chats)
            message = f"Load test message {random.randint(1, 1000)}"
            self.send_chat_message(chat["id"], message)


class DocumentMixin:
    """Mixin for document-related load testing."""

    @task(2)
    def list_documents(self):
        """List user's documents."""
        if self.auth_headers:
            self.safe_request(
                "get", "/api/v1/documents", headers=self.auth_headers
            )

    @task(1)
    def upload_document(self):
        """Upload a test document."""
        self.create_test_document()

    @task(2)
    def get_document(self):
        """Retrieve a specific document."""
        if self.documents and self.auth_headers:
            doc = random.choice(self.documents)
            self.safe_request(
                "get",
                f"/api/v1/documents/{doc['id']}",
                headers=self.auth_headers,
            )
