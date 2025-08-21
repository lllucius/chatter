# Chatter API Documentation & SDK Generation

This directory contains tools and documentation for the Chatter API, including automated OpenAPI documentation generation and Python SDK creation.

## 🚀 Quick Start

### Generate Documentation

Generate OpenAPI documentation in JSON and YAML formats:

```bash
# Generate all formats
python -m chatter docs generate

# Generate specific format
python -m chatter docs generate --format yaml --output custom/path

# Serve documentation locally
python -m chatter docs serve --port 8080
```

### Generate Python SDK

Generate a complete Python SDK from the OpenAPI specification:

```bash
# Generate Python SDK
python -m chatter docs sdk

# Generate to custom location
python -m chatter docs sdk --output custom/sdk/location
```

### Automated Workflow

Use the automated workflow script for CI/CD or batch processing:

```bash
# Generate both docs and SDK
python scripts/generate_all.py

# Generate only documentation
python scripts/generate_all.py --docs-only

# Generate only SDK  
python scripts/generate_all.py --sdk-only

# Clean and regenerate everything
python scripts/generate_all.py --clean
```

## 📁 Directory Structure

```
docs/
├── api/                    # Generated OpenAPI documentation
│   ├── openapi.json       # Latest OpenAPI spec (JSON)
│   ├── openapi.yaml       # Latest OpenAPI spec (YAML)
│   ├── openapi-v0.1.0.json  # Versioned spec (JSON)
│   └── openapi-v0.1.0.yaml  # Versioned spec (YAML)
└── README.md              # This file

sdk/
└── python/                # Generated Python SDK
    ├── chatter_sdk/       # Main SDK package
    ├── examples/          # Usage examples
    ├── docs/              # SDK documentation
    ├── test/              # Generated tests
    ├── setup.py           # Package setup
    ├── README.md          # SDK README
    └── requirements.txt   # Dependencies

scripts/
├── generate_openapi.py    # OpenAPI generation script
├── generate_sdk.py        # SDK generation script
└── generate_all.py        # Automated workflow script
```

## 🛠️ Features

### OpenAPI Documentation

- **Comprehensive API Coverage**: All 54+ endpoints documented
- **Rich Metadata**: Enhanced descriptions, examples, and schemas
- **Multiple Formats**: JSON and YAML export
- **Versioning**: Automatic version tagging
- **Validation**: Schema validation and consistency checks

### Python SDK

- **Async/Await Support**: Modern Python async patterns
- **Type Hints**: Full type annotation coverage  
- **Error Handling**: Comprehensive exception hierarchy
- **Authentication**: Automatic token management
- **Examples**: Ready-to-use code examples
- **Testing**: Generated test suite

### Automation Features

- **CLI Integration**: Built into the main Chatter CLI
- **CI/CD Ready**: Automation scripts for pipelines
- **Clean Builds**: Option to clean and regenerate
- **Flexible Output**: Customizable output directories
- **Format Selection**: Choose specific formats to generate

## 📚 Documentation Details

### API Endpoints Coverage

The generated documentation includes all API endpoints:

- **Health** (3 endpoints): Health checks and system status
- **Authentication** (8 endpoints): User auth, tokens, API keys  
- **Chat** (11 endpoints): Conversations, messages, streaming
- **Documents** (9 endpoints): Upload, search, management
- **Profiles** (10 endpoints): LLM profiles and settings
- **Analytics** (7 endpoints): Usage stats and metrics
- **Tool Servers** (16 endpoints): MCP tool management

### Schema Coverage

59 comprehensive schemas including:
- Request/response models
- Enum definitions  
- Validation rules
- Error responses
- Authentication models

## 🐍 Python SDK Details

### Key Features

- **ChatterClient**: Main client class with authentication
- **Async API**: All methods are async/await compatible
- **Auto-completion**: Full IDE support with type hints
- **Error Handling**: Structured exception hierarchy
- **Streaming**: Support for streaming chat responses
- **File Upload**: Multipart file upload support

### Basic Usage

```python
import asyncio
from chatter_sdk import ChatterClient

async def main():
    client = ChatterClient(base_url="http://localhost:8000")
    
    # Authenticate
    auth = await client.auth.login({
        "email": "user@example.com", 
        "password": "password"
    })
    
    # Start chatting
    response = await client.chat.chat({
        "message": "Hello, how can you help me?"
    })
    
    print(f"Assistant: {response.message.content}")
    await client.close()

asyncio.run(main())
```

### Advanced Features

```python
# Custom profiles
profile = await client.profiles.create_profile({
    "name": "Technical Assistant",
    "llm_provider": "openai",
    "llm_model": "gpt-4",
    "temperature": 0.3
})

# Document upload and RAG
with open("document.pdf", "rb") as f:
    doc = await client.documents.upload_document(file=f, title="Manual")

# RAG-enabled chat
response = await client.chat.chat({
    "message": "What does the manual say about installation?",
    "enable_retrieval": True
})
```

## 🔄 Automation & CI/CD

### GitHub Actions Example

```yaml
name: Generate API Docs and SDK

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          pip install -e .
          npm install -g @openapitools/openapi-generator-cli
      
      - name: Generate documentation and SDK
        run: python scripts/generate_all.py --clean
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: api-docs-and-sdk
          path: |
            docs/api/
            sdk/python/
```

### Manual Workflow

```bash
# 1. Clean previous builds
rm -rf docs/api sdk/

# 2. Generate fresh documentation
python -m chatter docs generate

# 3. Generate Python SDK
python -m chatter docs sdk

# 4. Verify generation
ls -la docs/api/
ls -la sdk/python/

# 5. Test SDK installation
cd sdk/python && pip install -e .

# 6. Run SDK examples
python examples/basic_usage.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for generation
DATABASE_URL=sqlite+aiosqlite:///test.db
ENVIRONMENT=development
OPENAI_API_KEY=fake-key-for-testing

# Optional customization
CHATTER_DOCS_OUTPUT=./custom/docs
CHATTER_SDK_OUTPUT=./custom/sdk
```

### Command Line Options

```bash
# Documentation generation
python -m chatter docs generate \
  --output docs/api \
  --format all

# SDK generation  
python -m chatter docs sdk \
  --language python \
  --output sdk

# Automated workflow
python scripts/generate_all.py \
  --clean \
  --output-dir ./ \
  --docs-format yaml
```

## 🚀 Deployment

### Package the SDK

```bash
cd sdk/python
python -m build
# Creates dist/ with wheel and source distributions
```

### Publish to PyPI

```bash
cd sdk/python
pip install twine
python -m twine upload dist/*
```

### Host Documentation

```bash
# Local development
python -m chatter docs serve --port 8080

# Production (nginx example)
cp docs/api/* /var/www/api-docs/
```

## 🤝 Contributing

When adding new API endpoints or modifying existing ones:

1. Update the endpoint documentation and schemas
2. Regenerate the OpenAPI docs: `python -m chatter docs generate`
3. Regenerate the SDK: `python -m chatter docs sdk`
4. Test the SDK with new features
5. Update examples if needed
6. Commit both the API changes and generated documentation

## 📄 License

Generated documentation and SDK inherit the same MIT license as the main Chatter project.