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
