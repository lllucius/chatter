# Examples

This directory contains example scripts demonstrating how to use various Chatter API features.

## Temporary Template Execution

These examples demonstrate how to execute workflow templates without storing them in the database first. This is useful for:
- Testing template configurations
- One-time workflow executions
- Dynamic, programmatically generated templates
- Development and debugging

### Working Examples

#### 1. Python SDK Example

**File:** `sdk_temporary_template_example.py`

Shows how to use the Chatter Python SDK to execute temporary templates.

**Prerequisites:**
- Chatter API server running (default: http://localhost:8000)
- Valid credentials set in `CHATTER_USERNAME` and `CHATTER_PASSWORD` environment variables
  (or uses defaults: user@example.com/secure_password)
- Python SDK installed (automatically available in development)

**Run the example:**
```bash
export CHATTER_USERNAME="your-username"
export CHATTER_PASSWORD="your-password"
python examples/sdk_temporary_template_example.py
```

#### 2. Direct API Example

**File:** `api_temporary_template_example.py`

Shows how to use direct HTTP requests (using the `requests` library) to execute temporary templates.

**Prerequisites:**
- Chatter API server running (default: http://localhost:8000)
- Valid credentials set in `CHATTER_USERNAME` and `CHATTER_PASSWORD` environment variables
  (or uses defaults: user@example.com/secure_password)
- requests library (`pip install requests`)

**Run the example:**
```bash
export CHATTER_USERNAME="your-username"
export CHATTER_PASSWORD="your-password"
pip install requests
python examples/api_temporary_template_example.py
```

#### 3. Conceptual Example

**File:** `temporary_template_execution_example.py`

Shows the conceptual structure and request/response formats (non-executable demo).

**Run the example:**
```bash
python examples/temporary_template_execution_example.py
```

### What Each Example Shows

All examples demonstrate:
1. Basic temporary template execution
2. Comparison with stored template execution
3. Benefits of temporary templates

### Additional Information

For more details, see [TEMPORARY_TEMPLATE_EXECUTION.md](../TEMPORARY_TEMPLATE_EXECUTION.md)
