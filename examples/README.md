# Examples

This directory contains example scripts demonstrating how to use various Chatter API features.

## Temporary Template Execution

**File:** `temporary_template_execution_example.py`

Demonstrates how to execute workflow templates without storing them in the database first. This is useful for:
- Testing template configurations
- One-time workflow executions
- Dynamic, programmatically generated templates
- Development and debugging

**Run the example:**
```bash
python examples/temporary_template_execution_example.py
```

The script shows:
1. Basic temporary template execution
2. Comparison with stored template execution
3. Testing different template configurations

For more details, see [TEMPORARY_TEMPLATE_EXECUTION.md](../TEMPORARY_TEMPLATE_EXECUTION.md)
