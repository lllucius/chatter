#!/usr/bin/env python3
"""
Demo script for the Chatter API platform.
This script demonstrates the core functionality of the advanced AI chatbot backend.
"""

import asyncio
from typing import Any

import httpx


class ChatterAPIDemo:
    """Demo client for the Chatter API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the demo client.

        Args:
            base_url: Base URL of the Chatter API
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.token = None
        self.user_info = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    async def register_user(self, email: str, username: str, password: str, full_name: str) -> dict[str, Any]:
        """Register a new user.

        Args:
            email: User email
            username: Username
            password: Password
            full_name: Full name

        Returns:
            Registration response
        """
        response = await self.client.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password,
                "full_name": full_name,
            }
        )
        response.raise_for_status()
        data = response.json()

        # Store token and user info
        self.token = data["access_token"]
        self.user_info = data["user"]

        return data

    async def login(self, email: str, password: str) -> dict[str, Any]:
        """Login user.

        Args:
            email: User email
            password: Password

        Returns:
            Login response
        """
        response = await self.client.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": email,
                "password": password,
            }
        )
        response.raise_for_status()
        data = response.json()

        # Store token and user info
        self.token = data["access_token"]
        self.user_info = data["user"]

        return data

    def _get_headers(self) -> dict[str, str]:
        """Get authorization headers.

        Returns:
            Headers with authorization
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")

        return {"Authorization": f"Bearer {self.token}"}

    async def get_profile(self) -> dict[str, Any]:
        """Get current user profile.

        Returns:
            User profile
        """
        response = await self.client.get(
            f"{self.base_url}/api/v1/auth/me",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def create_conversation(self, title: str, description: str = None) -> dict[str, Any]:
        """Create a new conversation.

        Args:
            title: Conversation title
            description: Conversation description

        Returns:
            Created conversation
        """
        response = await self.client.post(
            f"{self.base_url}/api/v1/chat/conversations",
            headers=self._get_headers(),
            json={
                "title": title,
                "description": description,
            }
        )
        response.raise_for_status()
        return response.json()

    async def list_conversations(self) -> dict[str, Any]:
        """List user conversations.

        Returns:
            List of conversations
        """
        response = await self.client.get(
            f"{self.base_url}/api/v1/chat/conversations",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Get conversation details.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation details with messages
        """
        response = await self.client.get(
            f"{self.base_url}/api/v1/chat/conversations/{conversation_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def check_health(self) -> dict[str, Any]:
        """Check API health.

        Returns:
            Health status
        """
        response = await self.client.get(f"{self.base_url}/healthz")
        response.raise_for_status()
        return response.json()


async def run_demo():
    """Run the Chatter API demo."""
    print("🚀 Chatter API Platform Demo")
    print("=" * 50)

    async with ChatterAPIDemo() as demo:
        try:
            # Check API health
            print("\n1. Checking API health...")
            health = await demo.check_health()
            print(f"   Status: {health['status']}")
            print(f"   Version: {health['version']}")
            print(f"   Environment: {health['environment']}")

            # Register a new user
            print("\n2. Registering a new user...")
            user_data = await demo.register_user(
                email="demo@chatter.ai",
                username="demo_user",
                password="DemoPassword123!",
                full_name="Demo User"
            )
            print(f"   User created: {user_data['user']['username']}")
            print(f"   User ID: {user_data['user']['id']}")
            print(f"   Token received: {user_data['access_token'][:20]}...")

            # Get user profile
            print("\n3. Getting user profile...")
            profile = await demo.get_profile()
            print(f"   Email: {profile['email']}")
            print(f"   Full name: {profile['full_name']}")
            print(f"   Created: {profile['created_at']}")

            # Create conversations
            print("\n4. Creating conversations...")
            conv1 = await demo.create_conversation(
                title="General Chat",
                description="A general conversation"
            )
            print(f"   Created conversation: {conv1['title']}")
            print(f"   Conversation ID: {conv1['id']}")

            conv2 = await demo.create_conversation(
                title="Technical Discussion",
                description="Discussion about technical topics"
            )
            print(f"   Created conversation: {conv2['title']}")
            print(f"   Conversation ID: {conv2['id']}")

            # List conversations
            print("\n5. Listing conversations...")
            conversations = await demo.list_conversations()
            print(f"   Total conversations: {conversations['total']}")
            for conv in conversations['conversations']:
                print(f"   - {conv['title']} (ID: {conv['id'][:8]}...)")

            # Get conversation details
            print("\n6. Getting conversation details...")
            details = await demo.get_conversation(conv1['id'])
            print(f"   Conversation: {details['title']}")
            print(f"   Messages: {len(details['messages'])}")
            print(f"   Status: {details['status']}")

            print("\n✅ Demo completed successfully!")
            print("\nThe Chatter API platform is working correctly with:")
            print("   - User authentication and registration")
            print("   - Conversation management")
            print("   - Health checks and monitoring")
            print("   - Database persistence")
            print("   - RESTful API endpoints")

            print("\nTo test chat functionality, configure LLM providers in .env:")
            print("   OPENAI_API_KEY=your_openai_key")
            print("   ANTHROPIC_API_KEY=your_anthropic_key")

        except httpx.HTTPStatusError as e:
            print(f"\n❌ HTTP Error: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_demo())
