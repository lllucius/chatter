# LangGraph Workflow API Refactoring

This document describes the recent refactoring of the LangGraph workflow APIs to provide a unified interface.

## Overview

The three separate workflow creation methods (`create_basic_conversation_workflow`, `create_rag_conversation_workflow`, and `create_tool_calling_workflow`) have been unified into a single interface that automatically determines the workflow type based on the provided parameters.

## New Unified Methods

### LangGraphWorkflowManager

#### `create_workflow(llm, system_message=None, retriever=None, tools=None)`

Creates a workflow based on provided parameters with automatic type detection:

- **No additional parameters**: Creates a basic conversation workflow
- **`retriever` provided**: Creates a RAG (Retrieval-Augmented Generation) workflow
- **`tools` provided**: Creates a tool-calling workflow
- **Both `retriever` and `tools` provided**: Creates a RAG workflow (RAG takes precedence)

#### `create_streaming_workflow(llm, system_message=None, retriever=None, tools=None)`

Creates a streaming-optimized workflow with the same parameter-based detection logic.

### LLMService

#### `create_langgraph_workflow(provider_name, workflow_type="basic", system_message=None, retriever=None, tools=None)`

Updated to use the unified workflow creation method internally while maintaining backward compatibility with the `workflow_type` parameter.

#### `create_langgraph_streaming_workflow(provider_name, workflow_type="basic", system_message=None, retriever=None, tools=None)`

New method for creating streaming workflows with the same interface as the regular workflow creation method.

## Unified API

The workflow API has been simplified to use a single unified method:

- `create_workflow(mode="plain"|"rag"|"tools"|"full")`
- Existing API endpoints continue to work with the unified backend

## Usage Examples

### Direct Workflow Manager Usage

```python
from chatter.core.langgraph import workflow_manager

# Basic workflow
basic_workflow = workflow_manager.create_workflow(llm=my_llm)

# RAG workflow  
rag_workflow = workflow_manager.create_workflow(
    llm=my_llm, 
    retriever=my_retriever
)

# Tools workflow
tools_workflow = workflow_manager.create_workflow(
    llm=my_llm,
    tools=my_tools
)

# Streaming workflow
streaming_workflow = workflow_manager.create_streaming_workflow(
    llm=my_llm,
    retriever=my_retriever
)
```

### LLMService Usage

```python
from chatter.services.llm import llm_service

# Using new unified approach
workflow = await llm_service.create_langgraph_workflow(
    provider_name="openai",
    workflow_type="rag",
    retriever=my_retriever
)

# Using new streaming method
streaming_workflow = await llm_service.create_langgraph_streaming_workflow(
    provider_name="openai", 
    workflow_type="tools",
    tools=my_tools
)
```

## Benefits

1. **Simplified API**: Single method for all workflow types
2. **Automatic Detection**: No need to specify workflow type explicitly
3. **Streaming Support**: Dedicated streaming workflow creation
4. **Reduced Code Duplication**: Unified implementation reduces maintenance overhead

## Future Enhancements

The unified API design makes it possible to create a single REST endpoint (e.g., `/workflows`) that could accept workflow configuration in the request body, eliminating the need for separate endpoints for each workflow type.