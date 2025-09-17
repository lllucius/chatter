# LangGraph astream_events() Workflow Streaming Implementation

This document describes the complete rewrite of the workflow streaming process using LangGraph's `astream_events()` method to provide real token-by-token streaming and node-level tracing capabilities.

## Overview

The new implementation replaces the previous simulation-based approach with LangGraph's native `astream_events()` streaming, providing:

- **Real token-by-token streaming** from LLM providers (not simulation)
- **Node-level tracing** for workflow development and debugging
- **Configurable event filtering** for production vs development modes
- **Backward compatible interfaces** with existing code

## Key Components

### 1. LangGraphWorkflowManager.stream_workflow()

**New Signature:**
```python
async def stream_workflow(
    self,
    workflow: Pregel,
    initial_state: ConversationState,
    thread_id: str | None = None,
    enable_llm_streaming: bool = False,
    enable_node_tracing: bool = False,
) -> Any:
```

**Key Changes:**
- Added `enable_node_tracing` parameter for development mode
- Uses `_stream_with_astream_events()` instead of old custom logic
- Provides fine-grained control over event types

### 2. Event Conversion System

The new `_convert_astream_event()` method converts LangGraph's native events to the expected workflow format:

**Token Streaming Events:**
```python
# Input: astream_events() token
{
    "event": "on_chat_model_stream",
    "name": "gpt-4",
    "data": {"chunk": AIMessageChunk(content="Hello")},
    "run_id": "abc123",
}

# Output: Workflow event
{
    "_token_stream": {
        "content": "Hello",
        "token": True,
        "model": "gpt-4",
        "run_id": "abc123",
    }
}
```

**Node Tracing Events:**
```python
# Input: astream_events() node event
{
    "event": "on_chain_start",
    "name": "call_model",
    "data": {"input": "..."},
    "run_id": "abc123",
}

# Output: Workflow event
{
    "_node_trace": {
        "type": "node_start",
        "node": "call_model",
        "run_id": "abc123",
        "input": "...",
    }
}
```

### 3. UnifiedWorkflowExecutor Updates

**Enhanced execute_streaming():**
- Processes `_token_stream` events for real-time token output
- Maintains backward compatibility with existing event formats
- Improved content buffering for token accumulation

**New execute_streaming_with_tracing():**
- Enables both token streaming AND node tracing
- Generates detailed StreamingChatChunk events for development
- Provides visibility into every workflow step

## Usage Modes

### Production Mode (Token Streaming Only)

```python
# Enable only final LLM token streaming
async for event in workflow_manager.stream_workflow(
    workflow,
    state,
    enable_llm_streaming=True,   # Real tokens from final LLM
    enable_node_tracing=False,   # No node details
):
    if "_token_stream" in event:
        token = event["_token_stream"]["content"]
        # Process individual token
```

**Benefits:**
- Real-time token output from LLM providers
- Minimal event overhead  
- Optimal for user-facing applications

### Development Mode (Full Tracing)

```python
# Enable comprehensive workflow tracing
async for event in workflow_manager.stream_workflow(
    workflow,
    state, 
    enable_llm_streaming=True,   # Token streaming
    enable_node_tracing=True,    # Node execution details
):
    if "_node_trace" in event:
        trace = event["_node_trace"]
        print(f"Node {trace['type']}: {trace['node']}")
    elif "_token_stream" in event:
        token = event["_token_stream"]["content"] 
        print(f"Token: {token}")
```

**Benefits:**
- Complete visibility into workflow execution
- Node timing and performance data
- Debugging capabilities for workflow development
- Input/output tracking for each step

### Hybrid Usage with execute_streaming_with_tracing()

```python
# Use the enhanced executor method
async for chunk in executor.execute_streaming_with_tracing(
    conversation, chat_request, correlation_id
):
    if chunk.type == "node_start":
        print(f"Starting: {chunk.metadata['node_name']}")
    elif chunk.type == "token":
        print(f"Token: {chunk.content}")
    elif chunk.type == "node_end":
        print(f"Completed: {chunk.metadata['node_name']}")
```

## Event Filtering

The implementation uses LangGraph's built-in filtering to optimize performance:

### Production Filtering
```python
# Only final LLM tokens
include_types = ["chat_model"]
include_names = ["call_model"]  # Final model node only
```

### Development Filtering  
```python
# All workflow events
include_types = ["chain", "tool", "chat_model", "runnable"]
include_names = None  # All nodes
```

### Custom Filtering
```python
# Specific tools only
include_types = ["tool"]
include_names = ["web_search", "calculator"]
```

## Benefits Over Previous Implementation

### 1. Real Token Streaming
- **Before:** Simulated token chunking of complete responses
- **After:** Actual token-by-token output from LLM providers
- **Impact:** True real-time streaming experience

### 2. Rich Node Tracing
- **Before:** Limited to node completion events
- **After:** Start/end events with timing and I/O data
- **Impact:** Complete workflow observability

### 3. Better Performance
- **Before:** Manual event parsing and detection
- **After:** Native LangGraph event filtering
- **Impact:** Reduced processing overhead

### 4. Enhanced Debugging
- **Before:** Black box workflow execution
- **After:** Detailed step-by-step execution tracing
- **Impact:** Faster development and troubleshooting

## Backward Compatibility

The new implementation maintains compatibility with existing code:

- `stream_workflow()` method signature preserved (with new optional parameters)
- Existing event formats still supported as fallback
- `UnifiedWorkflowExecutor.execute_streaming()` interface unchanged
- All existing workflow types (plain, rag, tools, full) supported

## Error Handling

The implementation includes robust error handling:

```python
try:
    async for event in workflow.astream_events(...):
        # Process events
except Exception as e:
    logger.error("astream_events streaming failed", error=str(e))
    # Fallback to regular astream
    async for event in workflow.astream(initial_state, config=config):
        yield event
```

This ensures that if `astream_events()` fails for any reason, the system gracefully falls back to the traditional streaming approach.

## Configuration Examples

### Environment-based Configuration
```python
import os

# Enable tracing in development environments
enable_tracing = os.getenv("WORKFLOW_TRACING", "false").lower() == "true"

async for event in workflow_manager.stream_workflow(
    workflow,
    state,
    enable_llm_streaming=True,
    enable_node_tracing=enable_tracing,
):
    # Process events based on mode
```

### Request-based Configuration
```python
# Enable tracing for specific requests
trace_request = chat_request.metadata.get("enable_tracing", False)

if trace_request:
    # Use the enhanced tracing executor
    async for chunk in executor.execute_streaming_with_tracing(...):
        yield chunk
else:
    # Use standard streaming
    async for chunk in executor.execute_streaming(...):
        yield chunk
```

## Migration Guide

For teams migrating from the old implementation:

1. **Update calls to stream_workflow():** Add the new optional parameters as needed
2. **Handle new event types:** Process `_token_stream` and `_node_trace` events
3. **Test both modes:** Verify production and development streaming work correctly
4. **Remove old workarounds:** Delete any custom token simulation code
5. **Update documentation:** Reflect the new streaming capabilities

The migration can be done incrementally since the new implementation maintains backward compatibility with existing event processing code.