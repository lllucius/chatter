# Workflow Execution Usage Metadata Flow

## Overview

This document explains how usage metadata (token counts and costs) flows through the workflow execution system, addressing the requirement to "ensure that any result that contains usage information are getting that information from the correct source."

## Data Flow Architecture

### 1. ModelNode Execution (Source)

`ModelNode.execute()` in `workflow_node_factory.py`:
- Calls LLM via `llm.ainvoke(messages)`
- Extracts `usage_metadata` from LLM response
- Returns `usage_metadata` in the node's state update

```python
# ModelNode.execute() returns:
{
    "messages": [response],
    "usage_metadata": {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
    }
}
```

### 2. Workflow State Updates

As the workflow executes:
- Each node can update the `usage_metadata` field in the state
- The workflow state flows through all nodes
- `usage_metadata` in state represents the **last node's** token usage

### 3. LangGraphWorkflowManager.run_workflow() (Aggregator)

`run_workflow()` in `core/langgraph.py`:
- Streams workflow state changes via `workflow.astream()`
- Collects ALL `usage_metadata` from state iterations
- Aggregates tokens across ALL nodes (with deduplication)
- Adds aggregated values as **top-level fields** in the result:
  - `tokens_used`: Total tokens across all nodes
  - `prompt_tokens`: Total input/prompt tokens
  - `completion_tokens`: Total output/completion tokens  
  - `cost`: Estimated cost based on token usage

```python
# run_workflow() returns:
{
    "messages": [...],
    "usage_metadata": {...},  # Last node's usage_metadata
    "tokens_used": 250,       # Aggregated across all nodes
    "prompt_tokens": 175,     # Aggregated across all nodes
    "completion_tokens": 75,  # Aggregated across all nodes
    "cost": 0.01305,          # Calculated from aggregated tokens
    "metadata": {...},
    ...
}
```

### 4. Consumer Code (Services and APIs)

All consumer code should use the **aggregated top-level fields**:

#### ✅ Correct Usage

```python
result = await workflow_manager.run_workflow(...)

# Use aggregated fields from result
tokens_used = result.get("tokens_used", 0)
prompt_tokens = result.get("prompt_tokens", 0)
completion_tokens = result.get("completion_tokens", 0)
cost = result.get("cost", 0.0)
```

#### ❌ Incorrect Usage

```python
# DON'T use raw usage_metadata (only reflects last node)
usage_metadata = result.get("usage_metadata", {})
tokens = usage_metadata.get("total_tokens", 0)  # ❌ Only last node!
```

## Implementation Details

### Aggregation Logic

`run_workflow()` aggregates tokens with these features:

1. **Deduplication**: Same `usage_metadata` dict won't be counted twice
2. **Field Name Flexibility**: Handles both:
   - `input_tokens`/`output_tokens` (standard)
   - `prompt_tokens`/`completion_tokens` (alternative)
3. **Total Calculation**: If `total_tokens` missing, calculates from input + output

### Current Consumers

All verified to use aggregated fields correctly:

- ✅ `workflow_execution.py::_execute_with_universal_template()`
- ✅ `workflow_execution.py::_execute_with_dynamic_workflow()`
- ✅ `workflow_execution.py::execute_workflow_definition()`
- ✅ `api/workflows.py::execute_custom_workflow()` (fixed in this PR)

## Changes Made

### 1. Fixed Custom Workflow Endpoint

**File**: `chatter/api/workflows.py`

Added usage fields to the response of `execute_custom_workflow()`:

```python
return {
    "response": response_content,
    "metadata": result.get("metadata", {}),
    "execution_summary": {...},
    # Added these fields to match other workflow endpoints
    "tokens_used": result.get("tokens_used", 0),
    "prompt_tokens": result.get("prompt_tokens", 0),
    "completion_tokens": result.get("completion_tokens", 0),
    "cost": result.get("cost", 0.0),
}
```

### 2. Enhanced Documentation

**File**: `chatter/core/langgraph.py`

Added comprehensive docstring to `run_workflow()` explaining:
- How usage_metadata flows through the system
- What fields are returned and their meaning
- Guidance for consumer code

### 3. Added Comprehensive Tests

**File**: `tests/test_workflow_usage_metadata_flow.py`

New tests verify:
- `run_workflow()` returns aggregated usage fields
- Aggregation works across multiple nodes
- Deduplication prevents double-counting
- Alternative field names are handled
- Workflows without token usage behave correctly

## Best Practices

### For Service/API Developers

1. **Always use aggregated fields** from `run_workflow()` result
2. **Never use `usage_metadata`** directly for totals (it's per-node only)
3. **Check for field existence** with `.get()` and defaults
4. **Pass through to responses** so clients can track usage

### For Node Developers

1. **Return usage_metadata** when your node uses tokens
2. **Use standard field names**: `input_tokens`, `output_tokens`, `total_tokens`
3. **Let run_workflow() handle aggregation** - don't aggregate yourself

## Testing

All existing tests pass:
- ✅ `test_token_aggregation_across_multiple_nodes`
- ✅ `test_token_aggregation_with_alternative_field_names`
- ✅ `test_no_tokens_returns_zero`

New tests added:
- ✅ `test_run_workflow_returns_aggregated_usage_fields`
- ✅ `test_workflow_result_separates_aggregated_from_node_metadata`
- ✅ `test_workflow_without_usage_metadata`
- ✅ `test_alternative_token_field_names`
- ✅ `test_duplicate_usage_metadata_not_aggregated`

## Summary

**The system correctly implements usage metadata flow:**
1. Nodes extract metadata from LLM responses
2. `run_workflow()` aggregates across all nodes
3. Consumers use aggregated top-level fields
4. Custom workflow endpoint now includes usage information

This ensures consistent, accurate token tracking and cost calculation across all workflow execution paths.
