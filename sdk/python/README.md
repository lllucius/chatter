# Chatter Python SDK

Python SDK for Chatter AI Chatbot API

## Installation

```bash
pip install chatter-sdk
```

## Quick Start

```python
import asyncio
from chatter_sdk import ChatterClient
from chatter_sdk.models import UserCreate, ChatRequest

async def main():
    # Initialize the client
    client = ChatterClient(base_url="http://localhost:8000")

    try:
        # Register and authenticate
        user_data = UserCreate(
            email="user@example.com",
            username="myuser",
            password="securepassword"
        )
        auth_response = await client.auth.register(user_data)

        # Start chatting
        response = await client.chat.chat(ChatRequest(
            message="Hello, how can you help me today?"
        ))
        print(f"Assistant: {response.message.content}")

    finally:
        await client.close()

asyncio.run(main())
```

## Features

### Authentication
- User registration and login
- JWT token management
- API key authentication
- Automatic token refresh

### Chat & Conversations
- Create and manage conversations
- Send messages with streaming support
- Multiple LLM providers (OpenAI, Anthropic, etc.)
- Custom profiles and prompts
- Tool calling and workflows

### Document Management
- Upload and process documents
- Vector search and retrieval
- RAG (Retrieval-Augmented Generation)
- Multiple document formats support

### Analytics
- Usage metrics and statistics
- Performance monitoring
- Cost tracking
- System health metrics

### Tool Servers
- MCP (Model Context Protocol) integration
- Custom tool server management
- Built-in tools (calculator, filesystem, browser)

## Configuration

The SDK can be configured using environment variables or constructor parameters:

```python
from chatter_sdk import ChatterClient

# Using environment variables
# CHATTER_BASE_URL=http://localhost:8000
# CHATTER_ACCESS_TOKEN=your_token_here
client = ChatterClient()

# Using constructor parameters
client = ChatterClient(
    base_url="http://localhost:8000",
    access_token="your_token_here",
    timeout=30.0
)
```

## Examples

### Basic Chat

```python
import asyncio
from chatter_sdk import ChatterClient

async def basic_chat():
    client = ChatterClient(base_url="http://localhost:8000")

    # Login with existing credentials
    await client.auth.login({
        "email": "user@example.com",
        "password": "password"
    })

    # Send a message
    response = await client.chat.chat({
        "message": "What's the weather like today?"
    })

    print(response.message.content)
    await client.close()

asyncio.run(basic_chat())
```

### Document Upload and Search

```python
import asyncio
from chatter_sdk import ChatterClient

async def document_example():
    client = ChatterClient(access_token="your_token")

    # Upload a document
    with open("document.pdf", "rb") as f:
        document = await client.documents.upload_document(
            file=f,
            title="Important Document",
            description="Company policy document"
        )

    # Search documents
    results = await client.documents.search_documents({
        "query": "vacation policy",
        "limit": 5
    })

    for result in results.results:
        print(f"Found: {result.document.title} (score: {result.score})")

    await client.close()

asyncio.run(document_example())
```

### Custom LLM Profile

```python
import asyncio
from chatter_sdk import ChatterClient

async def profile_example():
    client = ChatterClient(access_token="your_token")

    # Create a custom profile
    profile = await client.profiles.create_profile({
        "name": "Code Assistant",
        "llm_provider": "openai",
        "llm_model": "gpt-4",
        "temperature": 0.1,
        "system_prompt": "You are a senior software engineer assistant."
    })

    # Use the profile in a conversation
    response = await client.chat.chat({
        "message": "Explain async/await in Python",
        "profile_id": profile.id
    })

    print(response.message.content)
    await client.close()

asyncio.run(profile_example())
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from chatter_sdk import ChatterClient
from chatter_sdk.exceptions import (
    ChatterAPIError,
    AuthenticationError,
    ValidationError,
    RateLimitError
)

async def error_handling_example():
    client = ChatterClient()

    try:
        await client.auth.login({
            "email": "invalid@email.com",
            "password": "wrong_password"
        })
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except RateLimitError as e:
        print(f"Rate limited: {e}")
    except ChatterAPIError as e:
        print(f"API error: {e}")
```

## Development

To set up for development:

```bash
git clone https://github.com/lllucius/chatter
cd chatter/sdk/python
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Format code:

```bash
black .
isort .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- GitHub Issues: https://github.com/lllucius/chatter/issues
- Documentation: https://github.com/lllucius/chatter#readme
- Email: support@chatter.ai
