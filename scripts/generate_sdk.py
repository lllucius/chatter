#!/usr/bin/env python3
"""
Script to generate Python SDK from OpenAPI specification.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.generate_openapi import generate_openapi_spec


def generate_python_sdk():
    """Generate Python SDK using OpenAPI Generator."""
    print("🐍 Generating Python SDK...")
    
    # Create output directories
    sdk_output_dir = project_root / "sdk" / "python"
    sdk_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate fresh OpenAPI spec
    spec = generate_openapi_spec()
    
    # Save the spec to a temporary file
    temp_spec_path = sdk_output_dir / "temp_openapi.json"
    with open(temp_spec_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    # Configuration for the SDK generation
    config = {
        "packageName": "chatter_sdk",
        "projectName": "chatter-sdk",
        "packageVersion": spec.get("info", {}).get("version", "0.1.0"),
        "packageUrl": "https://github.com/lllucius/chatter",
        "packageCompany": "Chatter Team",
        "packageAuthor": "Chatter Team",
        "packageDescription": "Python SDK for Chatter AI Chatbot API",
        "infoEmail": "support@chatter.ai",
        "generateSourceCodeOnly": False,
        "packageSource": "https://github.com/lllucius/chatter",
        "appName": "ChatterSDK",
        "appDescription": "Python SDK for Chatter AI Chatbot API",
        "library": "asyncio",
        "useAsyncio": True,
    }
    
    # Save config to a file
    config_path = sdk_output_dir / "generator_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    try:
        # Generate the SDK using openapi-generator-cli
        cmd = [
            "openapi-generator-cli", "generate",
            "-i", str(temp_spec_path),
            "-g", "python",
            "-o", str(sdk_output_dir),
            "-c", str(config_path),
            "--additional-properties", f"pythonPackageName={config['packageName']}",
            "--skip-validate-spec"
        ]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
        
        if result.returncode != 0:
            print(f"❌ SDK generation failed:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
        
        print(f"✅ Python SDK generated successfully!")
        print(f"📁 SDK location: {sdk_output_dir}")
        
        # Clean up temporary files
        temp_spec_path.unlink(missing_ok=True)
        config_path.unlink(missing_ok=True)
        
        # Create a proper setup.py with better metadata
        create_enhanced_setup_py(sdk_output_dir, config)
        
        # Create examples
        create_sdk_examples(sdk_output_dir)
        
        # Create README for the SDK
        create_sdk_readme(sdk_output_dir, config)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating SDK: {e}")
        return False


def create_enhanced_setup_py(sdk_dir: Path, config: Dict[str, Any]):
    """Create an enhanced setup.py file for the SDK."""
    setup_py_content = f'''"""Setup configuration for Chatter Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{config['projectName']}",
    version="{config['packageVersion']}",
    author="{config['packageAuthor']}",
    author_email="{config['infoEmail']}",
    description="{config['packageDescription']}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="{config['packageUrl']}",
    project_urls={{
        "Bug Tracker": "{config['packageUrl']}/issues",
        "Documentation": "{config['packageUrl']}#readme",
        "Source Code": "{config['packageUrl']}",
    }},
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={{
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
        ],
    }},
    keywords="api, sdk, chatbot, ai, langchain, openai, anthropic",
    include_package_data=True,
    zip_safe=False,
)
'''
    
    setup_py_path = sdk_dir / "setup.py"
    with open(setup_py_path, 'w', encoding='utf-8') as f:
        f.write(setup_py_content)
    
    print(f"✅ Enhanced setup.py created at: {setup_py_path}")


def create_sdk_examples(sdk_dir: Path):
    """Create example usage files for the SDK."""
    examples_dir = sdk_dir / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    # Basic usage example
    basic_example = '''"""Basic usage example for Chatter SDK."""

import asyncio
from chatter_sdk import ChatterClient
from chatter_sdk.models import UserCreate, ChatRequest


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
'''
    
    with open(examples_dir / "basic_usage.py", 'w', encoding='utf-8') as f:
        f.write(basic_example)
    
    # Advanced example with documents and profiles
    advanced_example = '''"""Advanced usage example with document upload and profiles."""

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
'''
    
    with open(examples_dir / "advanced_usage.py", 'w', encoding='utf-8') as f:
        f.write(advanced_example)
    
    print(f"✅ SDK examples created in: {examples_dir}")


def create_sdk_readme(sdk_dir: Path, config: Dict[str, Any]):
    """Create a comprehensive README for the SDK."""
    readme_content = f'''# Chatter Python SDK

{config['packageDescription']}

## Installation

```bash
pip install {config['projectName']}
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
        print(f"Assistant: {{response.message.content}}")
        
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
    await client.auth.login({{
        "email": "user@example.com",
        "password": "password"
    }})
    
    # Send a message
    response = await client.chat.chat({{
        "message": "What's the weather like today?"
    }})
    
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
    results = await client.documents.search_documents({{
        "query": "vacation policy",
        "limit": 5
    }})
    
    for result in results.results:
        print(f"Found: {{result.document.title}} (score: {{result.score}})")
    
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
    profile = await client.profiles.create_profile({{
        "name": "Code Assistant",
        "llm_provider": "openai",
        "llm_model": "gpt-4",
        "temperature": 0.1,
        "system_prompt": "You are a senior software engineer assistant."
    }})
    
    # Use the profile in a conversation
    response = await client.chat.chat({{
        "message": "Explain async/await in Python",
        "profile_id": profile.id
    }})
    
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
        await client.auth.login({{
            "email": "invalid@email.com",
            "password": "wrong_password"
        }})
    except AuthenticationError as e:
        print(f"Authentication failed: {{e}}")
    except ValidationError as e:
        print(f"Validation error: {{e}}")
    except RateLimitError as e:
        print(f"Rate limited: {{e}}")
    except ChatterAPIError as e:
        print(f"API error: {{e}}")
```

## Development

To set up for development:

```bash
git clone {config['packageUrl']}
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

- GitHub Issues: {config['packageUrl']}/issues
- Documentation: {config['packageUrl']}#readme
- Email: {config['infoEmail']}
'''
    
    readme_path = sdk_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ SDK README created at: {readme_path}")


def main():
    """Main function to generate the Python SDK."""
    success = generate_python_sdk()
    
    if success:
        print("\n🎉 Python SDK generated successfully!")
        print("\n📋 Next steps:")
        print("1. Review the generated SDK code")
        print("2. Test the examples")
        print("3. Install the SDK: pip install -e ./sdk/python")
        print("4. Package for distribution: python -m build")
    else:
        print("\n❌ SDK generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()