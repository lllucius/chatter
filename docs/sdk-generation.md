# SDK Generation

This document explains how to regenerate the Python and TypeScript SDKs for the Chatter API.

## Overview

The Chatter API provides automatically generated SDKs in both Python and TypeScript. These SDKs are generated from the OpenAPI specification using the [OpenAPI Generator CLI](https://openapi-generator.tech/).

## Quick Start

To regenerate both SDKs:

```bash
python scripts/generate_sdks.py
```

## Usage Options

### Generate Both SDKs (Default)
```bash
# All of these commands generate both Python and TypeScript SDKs
python scripts/generate_sdks.py
python scripts/generate_sdks.py --all
python -m scripts --all
```

### Generate Python SDK Only
```bash
python scripts/generate_sdks.py --python
python -m scripts --python
```

### Generate TypeScript SDK Only
```bash
python scripts/generate_sdks.py --typescript
python -m scripts --typescript
```

### Verbose Output
```bash
python scripts/generate_sdks.py --verbose
python scripts/generate_sdks.py --python --verbose
```

## Output Locations

### Python SDK
- **Location**: `sdk/python/`
- **Package Name**: `chatter_sdk`
- **Language**: Python 3.12+
- **Library**: asyncio-based

### TypeScript SDK
- **Location**: `frontend/src/sdk/`
- **Package Name**: `chatter-sdk`
- **Language**: TypeScript
- **Target**: ES6+ with Fetch API

## Prerequisites

- Python 3.12+
- Node.js and npm (for OpenAPI Generator CLI)
- OpenAPI specification files in `docs/api/`

## How It Works

1. The script uses the existing `PythonSDKGenerator` and `TypeScriptSDKGenerator` classes
2. Default configurations are loaded for each SDK type
3. OpenAPI Generator CLI is invoked with the appropriate parameters
4. Generated SDKs are validated to ensure they contain the expected files
5. Temporary files are cleaned up automatically

## Configuration

The default configurations can be found in `scripts/utils/config.py`:

- `get_default_python_config()` - Python SDK configuration
- `get_default_typescript_config()` - TypeScript SDK configuration

These configurations specify:
- Output directories
- Package names and versions
- Author information
- Generator-specific options

## Troubleshooting

### OpenAPI Generator CLI Not Found
If you see an error about the OpenAPI Generator CLI not being found, make sure Node.js and npm are installed. The script will automatically download the generator on first use.

### Permission Errors
Make sure you have write permissions to the output directories:
- `sdk/python/`
- `frontend/src/sdk/`

### Import Errors
If you see module import errors, make sure you're running the script from the project root directory:

```bash
cd /path/to/chatter
python scripts/generate_sdks.py
```

## Integration with Development Workflow

You should regenerate the SDKs whenever:
1. The API endpoints change
2. Request/response models are modified
3. The OpenAPI specification is updated
4. You want to update the SDK version

The generated SDKs will be automatically validated to ensure they contain all expected API endpoints and models.