"""
Locust Load Testing Scenarios

Provides realistic user behavior scenarios for load testing the Chatter platform.
"""
from locust import task, between
import random
from .locust_base import (
    BaseChatterUser, 
    HealthCheckMixin, 
    AuthenticationMixin, 
    ChatMixin, 
    DocumentMixin
)


class MixedWorkloadUser(
    BaseChatterUser, 
    HealthCheckMixin, 
    AuthenticationMixin, 
    ChatMixin, 
    DocumentMixin
):
    """
    Realistic mixed workload user that performs a variety of operations.
    
    Usage:
    locust -f tests/load/locust_scenarios.py MixedWorkloadUser --host=http://localhost:8000
    """
    
    wait_time = between(2, 5)
    
    @task(10)
    def browse_and_interact(self):
        """Simulate browsing and interaction patterns."""
        # Simulate typical user journey
        if random.random() < 0.7:  # 70% chance to interact with chats
            if random.random() < 0.3:  # 30% create new chat
                chat = self.create_test_chat()
                if chat:
                    # Send a few messages to the new chat
                    for i in range(random.randint(1, 3)):
                        message = f"Hello! This is message {i+1} in my new chat."
                        self.send_chat_message(chat["id"], message)
            else:  # 70% interact with existing chats
                self.list_chats()
                if self.chats:
                    chat = random.choice(self.chats)
                    self.safe_request("get", f"/api/v1/chats/{chat['id']}", headers=self.auth_headers)
        
        elif random.random() < 0.3:  # 30% chance to work with documents
            if random.random() < 0.4:  # 40% upload new document
                self.create_test_document()
            else:  # 60% browse existing documents
                self.list_documents()


class HeavyUser(BaseChatterUser, ChatMixin, DocumentMixin):
    """
    Heavy user that performs resource-intensive operations.
    
    Usage:
    locust -f tests/load/locust_scenarios.py HeavyUser --host=http://localhost:8000
    """
    
    wait_time = between(3, 8)
    
    @task(5)
    def create_multiple_chats(self):
        """Create multiple chats in succession."""
        for _ in range(random.randint(2, 4)):
            self.create_test_chat()
    
    @task(3)
    def upload_large_documents(self):
        """Upload larger documents."""
        if not self.auth_headers:
            return
        
        # Create a larger document
        large_content = "Large document content for load testing. " * 500  # ~20KB
        files = {"file": ("large_loadtest_doc.txt", large_content, "text/plain")}
        data = {
            "title": f"Large Load Test Document {random.randint(1, 1000)}",
            "description": "Large document for load testing"
        }
        
        response = self.safe_request("post", "/api/v1/documents/upload", files=files, data=data, headers=self.auth_headers)
        if response and response.status_code in [200, 201]:
            self.documents.append(response.json())
    
    @task(4)
    def send_many_messages(self):
        """Send multiple messages rapidly."""
        if self.chats and self.auth_headers:
            chat = random.choice(self.chats)
            for i in range(random.randint(5, 10)):
                message = f"Rapid message {i+1}: {random.randint(1, 10000)}"
                self.send_chat_message(chat["id"], message)
    
    @task(2)
    def complex_search_operations(self):
        """Perform complex search operations."""
        if self.auth_headers:
            search_terms = ["test", "document", "chat", "load", "performance"]
            term = random.choice(search_terms)
            self.safe_request("get", f"/api/v1/documents/search?q={term}", headers=self.auth_headers)


class ChatLoadTestUser(BaseChatterUser, AuthenticationMixin):
    """
    Chat-focused load testing user.
    
    Usage:
    locust -f tests/load/locust_scenarios.py ChatLoadTestUser --host=http://localhost:8000
    """
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize with some chats."""
        super().on_start()
        # Create initial chats
        for _ in range(random.randint(2, 5)):
            self.create_test_chat()
    
    @task(15)
    def active_chatting(self):
        """Actively send messages to chats."""
        if self.chats and self.auth_headers:
            chat = random.choice(self.chats)
            messages = [
                "Hello, how are you?",
                "Can you help me with something?",
                "What's the weather like today?",
                "I need assistance with my project.",
                "Thank you for your help!",
                f"Random thought: {random.randint(1, 1000)}",
                "This is a load testing message.",
                "How is the system performing?"
            ]
            message = random.choice(messages)
            self.send_chat_message(chat["id"], message)
    
    @task(5)
    def check_chat_history(self):
        """Check chat message history."""
        if self.chats and self.auth_headers:
            chat = random.choice(self.chats)
            self.safe_request("get", f"/api/v1/chats/{chat['id']}/messages", headers=self.auth_headers)
    
    @task(3)
    def manage_chats(self):
        """Create or delete chats."""
        if random.random() < 0.7:  # 70% create new chat
            self.create_test_chat()
        else:  # 30% delete an old chat
            if len(self.chats) > 3:  # Keep at least 3 chats
                chat_to_delete = self.chats.pop(random.randint(0, len(self.chats) - 1))
                self.safe_request("delete", f"/api/v1/chats/{chat_to_delete['id']}", headers=self.auth_headers)


class DocumentLoadTestUser(BaseChatterUser, AuthenticationMixin):
    """
    Document-focused load testing user.
    
    Usage:
    locust -f tests/load/locust_scenarios.py DocumentLoadTestUser --host=http://localhost:8000
    """
    
    wait_time = between(2, 6)
    
    @task(8)
    def document_upload_workflow(self):
        """Upload and process documents."""
        self.create_test_document()
        
        # Check document status after upload
        if self.documents and self.auth_headers:
            doc = self.documents[-1]  # Latest document
            self.safe_request("get", f"/api/v1/documents/{doc['id']}/status", headers=self.auth_headers)
    
    @task(5)
    def browse_documents(self):
        """Browse and search documents."""
        if self.auth_headers:
            # List documents
            self.safe_request("get", "/api/v1/documents", headers=self.auth_headers)
            
            # Perform search if documents exist
            if self.documents:
                search_terms = ["test", "load", "document", "content"]
                term = random.choice(search_terms)
                self.safe_request("get", f"/api/v1/documents/search?q={term}", headers=self.auth_headers)
    
    @task(3)
    def document_operations(self):
        """Perform various document operations."""
        if self.documents and self.auth_headers:
            doc = random.choice(self.documents)
            
            # Get document details
            self.safe_request("get", f"/api/v1/documents/{doc['id']}", headers=self.auth_headers)
            
            # Update document metadata (if supported)
            update_data = {
                "title": f"Updated {doc.get('title', 'Document')}",
                "description": "Updated during load test"
            }
            self.safe_request("put", f"/api/v1/documents/{doc['id']}", json=update_data, headers=self.auth_headers)


class HealthCheckLoadTestUser(BaseChatterUser, HealthCheckMixin):
    """
    Basic system health monitoring user.
    
    Usage:
    locust -f tests/load/locust_scenarios.py HealthCheckLoadTestUser --host=http://localhost:8000
    """
    
    wait_time = between(5, 15)
    
    @task(10)
    def comprehensive_health_check(self):
        """Perform comprehensive health checks."""
        endpoints = [
            "/healthz",
            "/readyz", 
            "/metrics",
            "/api/v1/health"
        ]
        
        for endpoint in endpoints:
            self.safe_request("get", endpoint)
    
    @task(2)
    def api_availability_check(self):
        """Check API availability."""
        api_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/chats",
            "/api/v1/documents"
        ]
        
        for endpoint in api_endpoints:
            # Just check if endpoints respond (without auth)
            with self.client.options(endpoint, catch_response=True) as response:
                if response.status_code in [200, 405, 404]:  # Any response is good
                    response.success()


# Default user class for simple load testing
class DefaultLoadTestUser(MixedWorkloadUser):
    """
    Default load test user with mixed workload.
    
    This will be used when no specific user class is specified.
    """
    pass