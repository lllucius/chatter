# ChatRequest and ChatWorkflowRequest Consolidation

## Overview

The codebase has been refactored to consolidate `ChatRequest` and `ChatWorkflowRequest` into a single unified request type. This eliminates code duplication and simplifies the architecture while maintaining full backward compatibility.

## What Changed?

### Before
- **ChatRequest**: 16 fields for basic chat functionality
- **ChatWorkflowRequest**: 18 fields (15 overlapping + 3 unique) for workflow execution
- **Conversion**: Required `_convert_to_chat_request()` method to bridge the two types
- **Result**: ~120 lines of redundant code across schemas and conversion logic

### After
- **ChatRequest**: 19 fields supporting both chat and workflow execution
- **ChatWorkflowRequest**: Type alias to ChatRequest for backward compatibility
- **Conversion**: None needed - WorkflowExecutionService accepts ChatRequest directly
- **Result**: Single source of truth, cleaner codebase

## Migration Guide

### For Existing Code

No changes required! The consolidation is fully backward compatible.

```python
# Both of these work identically
from chatter.schemas.chat import ChatRequest
from chatter.schemas.workflows import ChatWorkflowRequest

# ChatWorkflowRequest is now an alias to ChatRequest
request1 = ChatRequest(message="Hello", workflow_definition_id="def-123")
request2 = ChatWorkflowRequest(message="Hello", workflow_definition_id="def-123")
# request1 and request2 are exactly the same type
```

### For New Code

Use `ChatRequest` for all chat and workflow operations:

```python
from chatter.schemas.chat import ChatRequest

# Simple chat
basic_request = ChatRequest(
    message="Hello, how are you?",
    enable_memory=True
)

# Chat with retrieval
rag_request = ChatRequest(
    message="What is in my documents?",
    enable_retrieval=True,
    document_ids=["doc-1", "doc-2"]
)

# Workflow execution using a predefined workflow
workflow_request = ChatRequest(
    message="Analyze this data",
    workflow_definition_id="analysis-workflow-123",
    enable_tools=True
)

# Workflow execution using a template
template_request = ChatRequest(
    message="Process this request",
    workflow_template_name="data-processing",
    enable_tracing=True
)

# Complex workflow with all options
complex_request = ChatRequest(
    message="Complex analysis",
    conversation_id="conv-123",
    workflow_config={"nodes": [...], "edges": [...]},
    enable_retrieval=True,
    enable_tools=True,
    enable_web_search=True,
    provider="openai",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000,
    enable_tracing=True
)
```

## Field Reference

### ChatRequest Fields

#### Required
- **message** (str): The user's message

#### Conversation
- **conversation_id** (str | None): Continue an existing conversation
- **profile_id** (str | None): Use a specific profile

#### Workflow Specification (choose one)
- **workflow_config** (dict | None): Dynamic workflow configuration
- **workflow_definition_id** (str | None): ID of existing workflow definition
- **workflow_template_name** (str | None): Name of workflow template

#### Capability Flags
- **enable_retrieval** (bool = False): Enable document retrieval
- **enable_tools** (bool = False): Enable tool calling
- **enable_memory** (bool = True): Enable conversation memory
- **enable_web_search** (bool = False): Enable web search

#### LLM Configuration
- **provider** (str | None): LLM provider override (e.g., "openai", "anthropic")
- **model** (str | None): Model override (e.g., "gpt-4", "claude-3")
- **temperature** (float | None): Temperature (0.0-2.0)
- **max_tokens** (int | None): Max tokens (1-8192)
- **context_limit** (int | None): Context window limit

#### Document Context
- **document_ids** (list[str] | None): Specific documents to include

#### Prompts
- **prompt_id** (str | None): ID of prompt template to use
- **system_prompt_override** (str | None): Override system prompt

#### Debug
- **enable_tracing** (bool = False): Enable detailed execution tracing

## SDK Updates

### Python SDK
```python
from chatter_sdk.models import ChatRequest

# The SDK has been updated to use ChatRequest for all chat/workflow operations
request = ChatRequest(
    message="Hello",
    workflow_definition_id="def-123",
    enable_retrieval=True
)
```

### TypeScript SDK
```typescript
import { ChatRequest } from 'chatter-sdk';

// The SDK has been updated to use ChatRequest for all chat/workflow operations
const request: ChatRequest = {
  message: "Hello",
  workflow_definition_id: "def-123",
  enable_retrieval: true
};
```

## API Endpoints

All workflow endpoints now accept `ChatRequest`:

### Execute Chat Workflow
```http
POST /api/workflows/chat
Content-Type: application/json

{
  "message": "Your message here",
  "workflow_definition_id": "def-123",
  "enable_retrieval": true,
  "enable_tracing": true
}
```

### Execute Chat Workflow (Streaming)
```http
POST /api/workflows/chat/stream
Content-Type: application/json

{
  "message": "Your message here",
  "workflow_template_name": "rag-template",
  "enable_retrieval": true
}
```

## Benefits

1. **Simplified Architecture**: Single request type for all chat/workflow operations
2. **Less Code**: Eliminated ~120 lines of redundant code
3. **Easier Maintenance**: Changes only need to be made in one place
4. **Cleaner SDKs**: Fewer types to understand and maintain
5. **Better DX**: One schema to learn instead of two
6. **Type Safety**: Stronger typing with no runtime conversion needed
7. **Backward Compatible**: Existing code continues to work without changes

## Implementation Details

### Why Keep ChatWorkflowRequest?

The `ChatWorkflowRequest` type alias is maintained for backward compatibility. Any existing code that imports or uses `ChatWorkflowRequest` will continue to work without modification.

```python
# In chatter/schemas/workflows.py
from chatter.schemas.chat import ChatRequest

# Backward compatibility alias
ChatWorkflowRequest = ChatRequest
```

### Why Keep ChatWorkflowConfig?

The `ChatWorkflowConfig`, `ModelConfig`, `RetrievalConfig`, and `ToolConfig` types are still needed as they represent structured configuration objects that can be passed in the `workflow_config` field of `ChatRequest`. These are not duplicates - they serve a different purpose.

```python
# Valid usage
request = ChatRequest(
    message="Test",
    workflow_config={
        "enable_retrieval": True,
        "llm_config": {
            "provider": "openai",
            "model": "gpt-4"
        },
        "retrieval_config": {
            "max_documents": 5
        }
    }
)
```

## Testing

Comprehensive tests have been added to verify:
- ✅ ChatWorkflowRequest is an alias to ChatRequest
- ✅ All fields work correctly
- ✅ Validation works as expected
- ✅ Serialization/deserialization works
- ✅ Backward compatibility is maintained
- ✅ Existing workflow tests still pass

Run tests:
```bash
pytest tests/test_chat_request_consolidation.py -v
```

## Questions?

If you have questions about this consolidation or encounter any issues, please:
1. Check this documentation first
2. Review the test file: `tests/test_chat_request_consolidation.py`
3. Open an issue with details about your use case
