"""Complete load test scenarios for Chatter platform."""

from tests.load.locust_base import (
    ChatterUser,
)

# This file can be run with: locust -f tests/load/locust_scenarios.py --host=http://localhost:8000


class MixedWorkloadUser(ChatterUser):
    """User that performs a realistic mix of operations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weight = 3  # More common user type

    @task(4)
    def browse_conversations(self):
        """Browse and read conversations."""
        self.client.get(
            "/api/v1/chat/conversations",
            headers=self.get_headers(),
            catch_response=True,
        )

    @task(3)
    def send_chat_message(self):
        """Send a chat message."""
        if not self.conversation_ids:
            # Create a conversation first
            response = self.client.post(
                "/api/v1/chat/conversations",
                json={"title": "Load Test Chat"},
                headers=self.get_headers(),
                catch_response=True,
            )
            if response.status_code in [200, 201]:
                data = response.json()
                conv_id = data.get("id") or data.get("conversation_id")
                if conv_id:
                    self.conversation_ids.append(conv_id)

        if self.conversation_ids:
            import random

            conv_id = random.choice(self.conversation_ids)
            self.client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={
                    "content": "Hello from load test",
                    "role": "user",
                },
                headers=self.get_headers(),
                catch_response=True,
            )

    @task(2)
    def search_documents(self):
        """Search for documents."""
        import random

        queries = ["test", "example", "document", "ai", "chat"]
        self.client.post(
            "/api/v1/documents/search",
            json={"query": random.choice(queries)},
            headers=self.get_headers(),
            catch_response=True,
        )

    @task(1)
    def check_health(self):
        """Check application health."""
        self.client.get("/health", catch_response=True)


class HeavyUser(ChatterUser):
    """User that performs intensive operations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weight = 1  # Less common but resource-intensive

    @task(2)
    def upload_large_document(self):
        """Upload a larger document."""
        large_content = (
            "Large document content for load testing.\n" * 100
        )
        self.client.post(
            "/api/v1/documents/upload",
            files={
                "file": ("large_test.txt", large_content, "text/plain")
            },
            headers=(
                {"Authorization": f"Bearer {self.auth_token}"}
                if self.auth_token
                else {}
            ),
            catch_response=True,
        )

    @task(3)
    def complex_search(self):
        """Perform complex semantic search."""
        self.client.post(
            "/api/v1/documents/search/semantic",
            json={
                "query": "complex artificial intelligence machine learning",
                "limit": 20,
                "threshold": 0.7,
            },
            headers=self.get_headers(),
            catch_response=True,
        )

    @task(1)
    def analytics_request(self):
        """Request analytics data."""
        endpoints = [
            "/api/v1/analytics/usage",
            "/api/v1/analytics/conversations",
            "/api/v1/analytics/performance",
        ]
        import random

        endpoint = random.choice(endpoints)
        self.client.get(
            endpoint, headers=self.get_headers(), catch_response=True
        )


# Configure user classes and their distribution
if __name__ == "__main__":
    # This allows running with: python tests/load/locust_scenarios.py
    print("Load test scenarios defined. Run with:")
    print(
        "locust -f tests/load/locust_scenarios.py --host=http://localhost:8000"
    )
    print("\nAvailable user types:")
    print(
        "- MixedWorkloadUser: Realistic mix of operations (weight: 3)"
    )
    print("- HeavyUser: Resource-intensive operations (weight: 1)")
    print("- ChatLoadTestUser: Chat-focused testing")
    print("- DocumentLoadTestUser: Document-focused testing")
    print("- HealthCheckLoadTestUser: Basic health checking")
