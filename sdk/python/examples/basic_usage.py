"""Basic usage example for Chatter SDK."""

import asyncio

from chatter_sdk import ChatterClient
from chatter_sdk.models import ChatRequest, UserCreate


async def main():
    """Example of basic SDK usage."""

    # Initialize the client
    client = ChatterClient(
        base_url="http://localhost:8000",
        # access_token="your_token_here"  # Optional if registering/logging in
    )

    try:
        # Register a new user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="securepassword123"
        )

        auth_response = await client.auth.register(user_data)
        print(f"User registered: {auth_response.user.username}")

        # The client is now authenticated automatically

        # Create a conversation
        conversation = await client.chat.create_conversation({
            "title": "My First Conversation",
            "description": "Testing the SDK"
        })
        print(f"Conversation created: {conversation.id}")

        # Send a chat message
        chat_request = ChatRequest(
            message="Hello, how are you?",
            conversation_id=conversation.id
        )

        response = await client.chat.chat(chat_request)
        print(f"Assistant: {response.message.content}")

        # List conversations
        conversations = await client.chat.list_conversations()
        print(f"Total conversations: {conversations.total}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
