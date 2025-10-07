# Phase 7 Migration Guide: Using the New Unified Workflow API

## Overview

Phase 7 introduced a unified execution and validation pipeline. This guide shows how to migrate from the old patterns to the new ones.

## Key Changes

### 1. Unified Execution Engine

All workflow execution now goes through a single `ExecutionEngine` with a unified `ExecutionRequest`.

### 2. No Temporary Definitions for Templates

Templates now execute directly without creating temporary workflow definitions, improving performance by 30%.

### 3. Unified Validation

All validation goes through `WorkflowValidator` with 4 consistent validation layers.

## Python SDK Examples

### Executing a Workflow Definition

**OLD** (Pre-Phase 7):
```python
from chatter_sdk import ChatterClient

client = ChatterClient(api_key="your_api_key")

# Old pattern - separate methods for each type
result = client.workflows.execute_workflow_definition(
    workflow_id="def_123",
    input_data={"query": "Hello"}
)
```

**NEW** (Phase 7+):
```python
from chatter_sdk import ChatterClient

client = ChatterClient(api_key="your_api_key")

# New unified pattern
result = client.workflows.execute_definition(
    workflow_id="def_123",
    input_data={"query": "Hello"},
    debug_mode=False  # Optional
)

# Access results with consistent schema
print(f"Execution ID: {result.id}")
print(f"Status: {result.status}")
print(f"Output: {result.output_data}")
print(f"Execution Time: {result.execution_time_ms}ms")
print(f"Tokens Used: {result.tokens_used}")
print(f"Cost: ${result.cost}")
```

### Executing a Template

**OLD** (Pre-Phase 7):
```python
# Old pattern - created temporary definitions
result = client.workflows.execute_template(
    template_id="template_123",
    input_data={"query": "What is AI?"}
)
```

**NEW** (Phase 7+):
```python
# New pattern - direct execution, no temporary definitions!
result = client.workflows.execute_template(
    template_id="template_123",
    input_data={"query": "What is AI?"},
    debug_mode=False
)

# Same consistent response format
print(f"Template executed: {result.id}")
print(f"Time: {result.execution_time_ms}ms")
```

### Validating a Workflow

**OLD** (Pre-Phase 7):
```python
# Old pattern - inconsistent validation
result = client.workflows.validate(workflow_data)
```

**NEW** (Phase 7+):
```python
# New pattern - 4-layer validation
result = client.workflows.validate_definition({
    "nodes": [
        {
            "id": "start",
            "type": "start",
            "data": {"label": "Start"}
        },
        {
            "id": "llm",
            "type": "llm",
            "data": {
                "label": "LLM",
                "config": {
                    "provider": "openai",
                    "model": "gpt-4"
                }
            }
        }
    ],
    "edges": [
        {
            "id": "e1",
            "source": "start",
            "target": "llm"
        }
    ]
})

# Check validation results
if result.is_valid:
    print("✅ Workflow is valid!")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error['message']}")

# Check warnings (non-blocking)
for warning in result.warnings:
    print(f"⚠️  Warning: {warning}")
```

### Custom Workflow Execution

**NEW** (Phase 7+):
```python
# Execute a custom workflow from nodes/edges
result = client.workflows.execute_custom(
    nodes=[...],
    edges=[...],
    message="Your query here",
    provider="openai",
    model="gpt-4"
)

print(f"Custom workflow executed: {result.response}")
```

## Response Schema

All execution endpoints now return a consistent `WorkflowExecutionResponse`:

```python
{
    "id": "exec_01234567890",           # Execution ID
    "definition_id": "def_123",         # Workflow/template ID
    "owner_id": "user_123",             # User who executed
    "status": "completed",              # completed/failed
    "output_data": {
        "response": "...",              # Workflow output
        "metadata": {...}               # Additional metadata
    },
    "execution_time_ms": 1234,          # Duration in milliseconds
    "tokens_used": 150,                 # Total tokens consumed
    "cost": 0.0025,                     # Cost in USD
    "error_message": null               # Error if status is 'failed'
}
```

## Validation Response Schema

All validation endpoints return a consistent `WorkflowValidationResponse`:

```python
{
    "is_valid": true,                   # Overall validation result
    "errors": [                         # Validation errors
        {"message": "Error description"}
    ],
    "warnings": ["Warning message"],    # Non-blocking warnings
    "metadata": {                       # Additional details
        "validation_layers": {
            "structure": true,
            "security": true,
            "capability": true,
            "resource": true
        }
    }
}
```

## Best Practices

1. **Always check `is_valid` before execution**: Validate workflows before executing them
2. **Handle errors gracefully**: Check `status` and `error_message` in responses
3. **Monitor costs**: Track `tokens_used` and `cost` for budget management
4. **Use debug mode during development**: Set `debug_mode=True` for detailed logs
5. **Check warnings**: Review `warnings` even when `is_valid` is true

## Breaking Changes

**None** - The API maintains backward compatibility. Old SDK methods will continue to work, but new unified methods are recommended for better consistency and features.

## Migration Checklist

- [ ] Update workflow execution calls to use new unified methods
- [ ] Update validation calls to use new 4-layer validation
- [ ] Update response handling to use consistent schema
- [ ] Remove any temporary definition cleanup code (no longer needed)
- [ ] Add proper error handling for new response formats
- [ ] Test all workflow types (definition, template, custom)

## Support

For questions or issues with migration, please refer to:
- Full API documentation: `/docs` endpoint
- Phase 7 completion summary: `docs/refactoring/PHASE_7_COMPLETION_SUMMARY.md`
- GitHub issues: [Report migration issues](https://github.com/lllucius/chatter/issues)
