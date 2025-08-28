#!/usr/bin/env python3
"""
Script to generate TypeScript SDK from OpenAPI specification.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.generate_openapi import generate_openapi_spec  # noqa: E402


def generate_typescript_sdk():
    """Generate TypeScript SDK using OpenAPI Generator."""
    print("📦 Generating TypeScript SDK...")

    # Create output directories
    sdk_output_dir = project_root / "frontend" / "src" / "sdk"
    sdk_output_dir.mkdir(parents=True, exist_ok=True)

    # Generate fresh OpenAPI spec
    spec = generate_openapi_spec()

    # Save the spec to a temporary file
    temp_spec_path = sdk_output_dir / "temp_openapi.json"
    with open(temp_spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

#        "modelPackage": "models"
    # Configuration for the SDK generation
    config = {
        "npmName": "chatter-sdk",
        "npmVersion": spec.get("info", {}).get("version", "0.1.0"),
        "npmRepository": "https://github.com/lllucius/chatter",
        "npmDescription": "TypeScript SDK for Chatter AI Chatbot API",
        "apiPackage": "api",
        "withInterfaces": True,
        "useSingleRequestParameter": True,
        "supportsES6": True,
        "enumNameSuffix": "",
        "enumPropertyNaming": "original",
    }

    # Save config to a file
    config_path = sdk_output_dir / "generator_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    try:
        # Generate the SDK using openapi-generator-cli
        cmd = [
            "openapi-generator-cli",
            "generate",
            "-i",
            str(temp_spec_path),
            "-g",
            "typescript-axios",
            "-o",
            str(sdk_output_dir),
            "-c",
            str(config_path),
            "--skip-validate-spec",
        ]

        print(f"🔧 Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(project_root)
        )

        if result.returncode != 0:
            print("❌ SDK generation failed:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False

        print("✅ TypeScript SDK generated successfully!")
        print(f"📁 SDK location: {sdk_output_dir}")

        # Clean up temporary files
        temp_spec_path.unlink(missing_ok=True)
        config_path.unlink(missing_ok=True)

        # Create package.json for the SDK
        create_sdk_package_json(sdk_output_dir, config)

        # Create a barrel export index.ts
        create_sdk_index(sdk_output_dir)

        # Create README for the SDK
        create_sdk_readme(sdk_output_dir, config)

        return True

    except Exception as e:
        print(f"❌ Error generating SDK: {e}")
        return False


def create_sdk_package_json(sdk_dir: Path, config: dict[str, Any]):
    """Create a package.json file for the SDK."""
    package_json_content = {
        "name": config["npmName"],
        "version": config["npmVersion"],
        "description": config["npmDescription"],
        "main": "index.ts",
        "types": "index.ts",
        "repository": {
            "type": "git",
            "url": config["npmRepository"]
        },
        "keywords": [
            "api",
            "sdk",
            "chatbot",
            "ai",
            "typescript",
            "axios"
        ],
        "author": "Chatter Team",
        "license": "MIT",
        "dependencies": {
            "axios": "^1.11.0"
        },
        "devDependencies": {
            "typescript": "^4.9.5",
            "@types/node": "^16.18.126"
        }
    }

    package_json_path = sdk_dir / "package.json"
    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(package_json_content, f, indent=2)

    print(f"✅ Package.json created at: {package_json_path}")


def create_sdk_index(sdk_dir: Path):
    """Create a main index.ts file that exports everything."""
    # Check what files were generated
    list((sdk_dir / "api").glob("*.ts")) if (sdk_dir / "api").exists() else []
    list((sdk_dir / "models").glob("*.ts")) if (sdk_dir / "models").exists() else []

    index_content = '''/**
 * Chatter TypeScript SDK
 * Generated from OpenAPI specification
 */

// Export all APIs
export * from './api';

// Export all models
export * from './models';

// Export configuration and base types
export { Configuration, ConfigurationParameters } from './configuration';
export { BaseAPI } from './base';
'''

    # If there's a direct api.ts file, export from it
    if (sdk_dir / "api.ts").exists():
        index_content += "export * from './api';\n"

    # If there's a direct models.ts file, export from it
    if (sdk_dir / "models.ts").exists():
        index_content += "export * from './models';\n"

    index_path = sdk_dir / "index.ts"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"✅ SDK index.ts created at: {index_path}")


def create_sdk_readme(sdk_dir: Path, config: dict[str, Any]):
    """Create a README for the TypeScript SDK."""
    readme_content = f"""# Chatter TypeScript SDK

{config['npmDescription']}

## Installation

Since this is a local SDK generated from the OpenAPI specification, it's automatically available in your frontend application.

## Usage

```typescript
import {{
  Configuration,
  AuthenticationApi,
  ConversationsApi,
  DocumentsApi,
  ProfilesApi,
  // ... other APIs
}} from './sdk';

// Create configuration
const config = new Configuration({{
  basePath: 'http://localhost:8000',
  accessToken: () => your_token_here,
}});

// Create API instances
const authApi = new AuthenticationApi(config);
const conversationsApi = new ConversationsApi(config);

// Use the APIs
async function example() {{
  try {{
    const user = await authApi.apiV1AuthMeGet();
    console.log('Current user:', user.data);

    const conversations = await conversationsApi.apiV1ConversationsGet();
    console.log('Conversations:', conversations.data);
  }} catch (error) {{
    console.error('API error:', error);
  }}
}}
```

## Features

- **Type Safety**: Full TypeScript support with generated interfaces
- **Axios-based**: Uses Axios HTTP client for all requests
- **OpenAPI Generated**: Automatically generated from the OpenAPI specification
- **Authentication**: Built-in support for JWT token authentication
- **Error Handling**: Proper error handling with typed responses

## API Coverage

This SDK provides TypeScript interfaces and API clients for all Chatter endpoints:

- **Authentication**: Login, register, user management
- **Conversations**: Create, manage, and interact with conversations
- **Documents**: Upload, search, and manage documents
- **Profiles**: Configure LLM profiles and settings
- **Prompts**: Manage prompt templates
- **Agents**: AI agent configuration and management
- **Tool Servers**: MCP tool server integration
- **Analytics**: Usage statistics and metrics
- **Health**: System health monitoring

## Configuration

The SDK uses the `Configuration` class to manage API settings:

```typescript
import {{ Configuration }} from './sdk';

const config = new Configuration({{
  basePath: 'http://localhost:8000',  // API base URL
  accessToken: () => localStorage.getItem('auth_token'),  // Token provider function
  // Additional axios configuration can be passed here
}});
```

## Error Handling

All API methods return promises that can be handled with try/catch:

```typescript
import {{ AuthenticationApi }} from './sdk';

const authApi = new AuthenticationApi(config);

try {{
  const response = await authApi.apiV1AuthLoginPost({{
    email: 'user@example.com',
    password: 'password123'
  }});

  console.log('Login successful:', response.data);
}} catch (error) {{
  if (error.response?.status === 401) {{
    console.error('Invalid credentials');
  }} else {{
    console.error('Login error:', error.message);
  }}
}}
```

## Generated Files

This SDK contains the following generated files:

- `api.ts` or `api/` - API client classes
- `models.ts` or `models/` - TypeScript interfaces for all data models
- `configuration.ts` - Configuration management
- `base.ts` - Base API class with common functionality
- `index.ts` - Main export file

## Regeneration

This SDK is automatically generated from the OpenAPI specification. To regenerate:

```bash
cd /path/to/chatter
python scripts/generate_ts.py
```

Or use the combined workflow:

```bash
python scripts/generate_all.py
```

## Development

The SDK is generated as part of the development workflow and should not be manually edited. All changes should be made to the backend API and OpenAPI specification, then the SDK should be regenerated.
"""

    readme_path = sdk_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ SDK README created at: {readme_path}")


def main():
    """Main function to generate the TypeScript SDK."""
    success = generate_typescript_sdk()

    if success:
        print("\n🎉 TypeScript SDK generated successfully!")
        print("\n📋 Next steps:")
        print("1. Review the generated SDK code")
        print("2. Update frontend imports to use the generated SDK")
        print("3. Test the frontend with the new SDK")
        print("4. Build the frontend to verify TypeScript compilation")
    else:
        print("\n❌ SDK generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
