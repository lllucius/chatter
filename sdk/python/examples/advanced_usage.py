"""Advanced usage example with document upload and profiles."""

import asyncio
from pathlib import Path
from chatter_sdk import ChatterClient
from chatter_sdk.models import ProfileCreate, DocumentSearchRequest


async def main():
    """Example of advanced SDK features."""

    client = ChatterClient(
        base_url="http://localhost:8000",
        access_token="your_access_token_here"  # Assume already authenticated
    )

    try:
        # Create a custom LLM profile
        profile = await client.profiles.create_profile(ProfileCreate(
            name="My Custom Profile",
            description="A profile optimized for technical discussions",
            llm_provider="openai",
            llm_model="gpt-4",
            temperature=0.3,
            max_tokens=2048,
            system_prompt="You are a helpful technical assistant specializing in software development."
        ))
        print(f"Profile created: {profile.name}")

        # Upload a document (if you have a file)
        # with open("sample.pdf", "rb") as f:
        #     document = await client.documents.upload_document(
        #         file=f,
        #         title="Sample Document",
        #         description="A sample PDF for testing"
        #     )
        #     print(f"Document uploaded: {document.title}")

        # Search documents
        search_request = DocumentSearchRequest(
            query="technical documentation",
            limit=5
        )
        search_results = await client.documents.search_documents(search_request)
        print(f"Found {len(search_results.results)} documents")

        # Start a conversation with the custom profile and retrieval
        conversation = await client.chat.create_conversation({
            "title": "Technical Discussion",
            "profile_id": profile.id,
            "enable_retrieval": True
        })

        # Chat with retrieval enabled
        response = await client.chat.chat({
            "message": "Explain the benefits of async programming in Python",
            "conversation_id": conversation.id,
            "enable_retrieval": True
        })
        print(f"Response with context: {response.message.content}")

        # Get analytics
        analytics = await client.analytics.get_conversation_stats()
        print(f"Total conversations: {analytics.total_conversations}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
