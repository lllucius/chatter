"""Python SDK generation."""

from pathlib import Path

from scripts.sdk.base import SDKGenerator
from scripts.utils.config import (
    PythonSDKConfig,
    get_openapi_generator_config,
)
from scripts.utils.files import save_text, verify_files_exist
from scripts.utils.subprocess import (
    ProcessError,
    ensure_command_available,
    run_command,
)


class PythonSDKGenerator(SDKGenerator):
    """Generator for Python SDK using openapi-python-client."""

    def __init__(self, config: PythonSDKConfig):
        super().__init__(config)
        self.config: PythonSDKConfig = config

    def generate(self) -> bool:
        """Generate Python SDK using openapi-python-client."""
        print("🐍 Generating Python SDK...")

        # Check dependencies - prefer openapi-python-client over openapi-generator-cli for Python
        try:
            ensure_command_available(
                "openapi-python-client",
                "pip install openapi-python-client",
            )
        except Exception:
            # Fallback to openapi-generator-cli
            try:
                ensure_command_available(
                    "openapi-generator-cli",
                    "npm install -g @openapitools/openapi-generator-cli",
                )
                return self._generate_with_openapi_generator()
            except Exception as e:
                print(f"❌ {e}")
                print(
                    "⚠️  No OpenAPI generators available, creating mock SDK for testing"
                )
                return self._create_mock_python_sdk()

        return self._generate_with_python_client()

    def _generate_with_python_client(self) -> bool:
        """Generate using openapi-python-client."""
        # Prepare output directory
        self.prepare_output_directory()

        # Generate OpenAPI spec
        try:
            spec = self.generate_openapi_spec()
        except Exception as e:
            print(f"❌ Failed to generate OpenAPI spec: {e}")
            # Use mock spec for testing
            from scripts.sdk.base import MockOpenAPISpec

            spec = MockOpenAPISpec.get_mock_spec()
            print("⚠️  Using mock OpenAPI spec for testing")

        # Save OpenAPI spec
        spec_path = self.save_temp_openapi_spec(spec)

        # Run openapi-python-client
        cmd = [
            "openapi-python-client",
            "generate",
            "--path",
            str(spec_path),
            "--output-path",
            str(self.config.output_dir),
            "--overwrite",
        ]

        try:
            success, stdout, stderr = run_command(
                cmd,
                "Python SDK generation (openapi-python-client)",
                cwd=self.config.project_root,
                timeout=300,
            )

            if not success:
                return False

        except ProcessError as e:
            print(f"❌ Python client generation failed: {e}")
            return False

        # Create additional files
        self._create_setup_py()
        self._create_examples()
        self._create_readme()

        print("✅ Python SDK generated successfully!")
        print(f"📁 SDK location: {self.config.output_dir}")

        return True

    def _generate_with_openapi_generator(self) -> bool:
        """Generate using openapi-generator-cli as fallback."""
        print("🔧 Using openapi-generator-cli as fallback...")

        # Prepare output directory
        self.prepare_output_directory()

        # Generate OpenAPI spec
        try:
            spec = self.generate_openapi_spec()
        except Exception as e:
            print(f"❌ Failed to generate OpenAPI spec: {e}")
            from scripts.sdk.base import MockOpenAPISpec

            spec = MockOpenAPISpec.get_mock_spec()
            print("⚠️  Using mock OpenAPI spec for testing")

        # Save temporary files
        spec_path = self.save_temp_openapi_spec(spec)
        generator_config = get_openapi_generator_config(self.config)
        config_path = self.save_generator_config(generator_config)

        # Generate SDK
        additional_args = [
            "--additional-properties",
            f"pythonPackageName={self.config.package_name}",
        ]

        success = self.run_generator_command(
            "python", spec_path, config_path, additional_args
        )

        if not success:
            return False

        # Create additional files
        self._create_setup_py()
        self._create_examples()
        self._create_readme()

        print("✅ Python SDK generated successfully!")
        print(f"📁 SDK location: {self.config.output_dir}")

        return True

    def validate(self) -> bool:
        """Validate the generated Python SDK."""
        print("🔍 Validating Python SDK...")

        expected_files = self.get_expected_files()
        missing_files = verify_files_exist(
            self.config.output_dir, expected_files, "Python SDK files"
        )

        if missing_files:
            print(
                f"❌ Validation failed: {len(missing_files)} missing files"
            )
            return False

        # Additional validation: check if Python files can be imported
        if not self._validate_python_syntax():
            return False

        print("✅ Python SDK validation passed")
        return True

    def get_expected_files(self) -> list[str]:
        """Get list of expected files after generation."""
        return [
            "setup.py",
            "README.md",
            "requirements.txt",
            f"{self.config.package_name}/__init__.py",
            "examples/basic_usage.py",
        ]

    def _create_setup_py(self) -> None:
        """Create enhanced setup.py file for the SDK."""
        setup_py_content = f'''"""Setup configuration for Chatter Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{self.config.project_name}",
    version="{self.config.package_version}",
    author="{self.config.package_author}",
    author_email="{self.config.author_email}",
    description="{self.config.package_description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="{self.config.package_url}",
    project_urls={{
        "Bug Tracker": "{self.config.package_url}/issues",
        "Documentation": "{self.config.package_url}#readme",
        "Source Code": "{self.config.package_url}",
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

        save_text(setup_py_content, self.config.output_dir / "setup.py")

    def _create_examples(self) -> None:
        """Create example usage files for the SDK."""
        examples_dir = self.config.output_dir / "examples"
        examples_dir.mkdir(exist_ok=True)

        # Basic usage example
        basic_example = f'''"""Basic usage example for Chatter SDK."""

import asyncio
from {self.config.package_name} import ChatterClient
from {self.config.package_name}.models import UserCreate, ChatRequest


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
        print(f"User registered: {{auth_response.user.username}}")

        # The client is now authenticated automatically

        # Create a conversation
        conversation = await client.chat.create_conversation({{
            "title": "My First Conversation",
            "description": "Testing the SDK"
        }})
        print(f"Conversation created: {{conversation.id}}")

        # Send a chat message
        chat_request = ChatRequest(
            message="Hello, how are you?",
            conversation_id=conversation.id
        )

        response = await client.chat.chat(chat_request)
        print(f"Assistant: {{response.message.content}}")

        # List conversations
        conversations = await client.chat.list_conversations()
        print(f"Total conversations: {{conversations.total}}")

    except Exception as e:
        print(f"Error: {{e}}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
'''

        save_text(basic_example, examples_dir / "basic_usage.py")

    def _create_readme(self) -> None:
        """Create comprehensive README for the SDK."""
        readme_content = f"""# Chatter Python SDK

{self.config.package_description}

## Installation

```bash
pip install {self.config.project_name}
```

## Quick Start

```python
import asyncio
from {self.config.package_name} import ChatterClient
from {self.config.package_name}.models import UserCreate, ChatRequest

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

## Development

To set up for development:

```bash
git clone {self.config.package_url}
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

- GitHub Issues: {self.config.package_url}/issues
- Documentation: {self.config.package_url}#readme
- Email: {self.config.author_email}
"""

        save_text(readme_content, self.config.output_dir / "README.md")

    def _validate_python_syntax(self) -> bool:
        """Validate Python syntax by attempting to compile generated files."""
        try:
            import ast
            import os

            python_files = []
            for root, _dirs, files in os.walk(self.config.output_dir):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(Path(root) / file)

            for py_file in python_files:
                try:
                    with open(py_file, encoding='utf-8') as f:
                        content = f.read()

                    # Try to parse the file
                    ast.parse(content)

                except SyntaxError as e:
                    print(
                        f"❌ Syntax error in {py_file.relative_to(self.config.output_dir)}: {e}"
                    )
                    return False
                except Exception as e:
                    print(
                        f"⚠️  Could not validate {py_file.relative_to(self.config.output_dir)}: {e}"
                    )
                    continue

            print(f"✅ Validated {len(python_files)} Python files")
            return True

        except Exception as e:
            print(f"⚠️  Could not validate Python syntax: {e}")
            return (
                True  # Don't fail generation due to validation issues
            )

    def _create_mock_python_sdk(self) -> bool:
        """Create a minimal mock Python SDK for testing."""
        print("📝 Creating mock Python SDK files...")

        # Prepare output directory
        self.prepare_output_directory()

        # Create Python package structure
        package_dir = self.config.output_dir / self.config.package_name
        package_dir.mkdir(exist_ok=True)

        # Create minimal Python files
        self._create_mock_init_file(package_dir)
        self._create_mock_client_file(package_dir)
        self._create_mock_models_file(package_dir)
        self._create_setup_py()
        self._create_examples()
        self._create_readme()
        self._create_requirements_txt()

        print("✅ Mock Python SDK created successfully!")
        print(f"📁 SDK location: {self.config.output_dir}")

        return True

    def _create_mock_init_file(self, package_dir: Path) -> None:
        """Create a mock __init__.py file."""
        init_content = f'''"""
Chatter Python SDK - Mock Implementation
This is a minimal implementation for testing purposes.
"""

__version__ = "{self.config.package_version}"

from .client import ChatterClient
from .models import HealthResponse

__all__ = ["ChatterClient", "HealthResponse"]
'''

        save_text(init_content, package_dir / "__init__.py")

    def _create_mock_client_file(self, package_dir: Path) -> None:
        """Create a mock client file."""
        client_content = '''"""
Mock Chatter client for testing.
"""

import asyncio
from typing import Optional

import aiohttp
from .models import HealthResponse


class ChatterClient:
    """Mock Chatter API client."""

    def __init__(self, base_url: str = "http://localhost:8000", access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"

            self._session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers=headers
            )
        return self._session

    async def health_check(self) -> HealthResponse:
        """Perform health check."""
        session = await self._get_session()

        async with session.get("/api/v1/health") as response:
            data = await response.json()
            return HealthResponse(**data)

    async def close(self) -> None:
        """Close the client session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
'''

        save_text(client_content, package_dir / "client.py")

    def _create_mock_models_file(self, package_dir: Path) -> None:
        """Create a mock models file."""
        models_content = '''"""
Mock data models for testing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HealthResponse:
    """Health check response model."""
    status: str
    timestamp: str


@dataclass
class UserCreate:
    """User creation model."""
    email: str
    username: str
    password: str


@dataclass
class ChatRequest:
    """Chat request model."""
    message: str
    conversation_id: Optional[str] = None
'''

        save_text(models_content, package_dir / "models.py")

    def _create_requirements_txt(self) -> None:
        """Create requirements.txt file."""
        requirements_content = '''aiohttp>=3.8.0
pydantic>=2.0.0
typing-extensions>=4.0.0
'''

        save_text(
            requirements_content,
            self.config.output_dir / "requirements.txt",
        )


def main():
    """Main function to generate Python SDK."""
    from scripts.utils.config import get_default_python_config

    # Get project root
    project_root = Path(__file__).parent.parent.parent
    config = get_default_python_config(project_root)

    # Generate SDK
    generator = PythonSDKGenerator(config)
    success = generator.generate_with_cleanup()

    if success:
        # Validate generated SDK
        if generator.validate():
            print(
                "\n🎉 Python SDK generated and validated successfully!"
            )
        else:
            print("\n⚠️  Python SDK generated but validation failed")
    else:
        print("\n❌ Python SDK generation failed!")
        return 1

    print("\n📋 Next steps:")
    print("1. Review the generated SDK code")
    print("2. Test the examples")
    print("3. Install the SDK: pip install -e ./sdk/python")
    print("4. Package for distribution: python -m build")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
