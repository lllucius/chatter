# Temporary Template Execution API

## Overview

This document describes the new API endpoint for executing temporary workflow templates without persisting them to the database.

## New API Endpoint

### Execute Temporary Workflow Template

**Endpoint:** `POST /api/v1/workflows/templates/execute`

**Description:** Execute a temporary workflow template directly without storing it in the database. This allows you to pass template data and execute it immediately.

**Request Body:** `WorkflowTemplateDirectExecutionRequest`

```json
{
  "template": {
    "name": "My Temporary Template",
    "description": "A template for one-time use",
    "category": "custom",
    "default_params": {
      "model": "gpt-4",
      "temperature": 0.7,
      "system_prompt": "You are a helpful assistant."
    },
    "required_tools": ["search"],
    "required_retrievers": null
  },
  "input_data": {
    "temperature": 0.9,
    "max_tokens": 1000,
    "user_query": "What is the weather today?"
  },
  "debug_mode": false
}
```

**Response:** `WorkflowExecutionResponse`

```json
{
  "execution_id": "01JXXXXXXXXXXXXXXXXXXXXXXX",
  "status": "completed",
  "result": {
    "output": "The response from the workflow execution",
    "metadata": {...}
  },
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:00:05Z"
}
```

## Comparison with Existing Endpoint

### Existing Endpoint: Execute Stored Template

**Endpoint:** `POST /api/v1/workflows/templates/{template_id}/execute`

- Requires a template to be stored in the database first
- Uses `template_id` to reference the stored template
- Template data is loaded from the database

### New Endpoint: Execute Temporary Template

**Endpoint:** `POST /api/v1/workflows/templates/execute`

- Does not require storing the template in the database
- Template data is passed directly in the request body
- Useful for one-time executions or testing templates

## Use Cases

1. **Testing Templates:** Test a template configuration before saving it to the database
2. **One-time Workflows:** Execute a workflow for a specific use case without cluttering the template database
3. **Dynamic Templates:** Generate and execute templates programmatically without persistence
4. **Template Development:** Iterate on template designs without creating multiple stored versions

## Implementation Details

### Schema Changes

- **Added:** `WorkflowTemplateDirectExecutionRequest` in `chatter/schemas/workflows.py`
  - Contains `template` (dict), `input_data` (optional dict), and `debug_mode` (bool)

### Service Changes

- **Added:** `create_workflow_definition_from_template_data()` method in `WorkflowManagementService`
  - Creates a temporary workflow definition from template data
  - Validates required fields (name, description)
  - Generates workflow nodes and edges using the same logic as stored templates
  - Does not persist the template to the database

### API Changes

- **Added:** `execute_temporary_workflow_template()` endpoint in `chatter/api/workflows.py`
  - Accepts `WorkflowTemplateDirectExecutionRequest`
  - Creates a temporary workflow definition
  - Executes the workflow
  - Returns execution results

## Notes

- The temporary template is not saved to the database
- A temporary workflow definition is created for execution tracking purposes
- The workflow definition is marked as temporary in its metadata
- All the same validation and execution logic applies as with stored templates

## SDK Generation

After making these changes, regenerate the SDK to include the new model and endpoint:

```bash
python scripts/generate_sdks.py --all --verbose
```

This will generate:
- Python SDK: `sdk/python/chatter_sdk/models/workflow_template_direct_execution_request.py`
- TypeScript SDK: `frontend/sdk/src/models/WorkflowTemplateDirectExecutionRequest.ts`
