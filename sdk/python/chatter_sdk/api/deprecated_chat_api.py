"""
DEPRECATED: Chat API Endpoints

This module is DEPRECATED and scheduled for removal in v2.0.0.
Use the new workflow-based chat system instead:

BEFORE (deprecated):
```python
from chatter_sdk import ChatApi
chat_api = ChatApi()
response = await chat_api.chat_chat({
    "message": "Hello",
    "workflow": "rag",
    "enable_retrieval": True
})
```

AFTER (recommended):
```python  
from chatter_sdk import WorkflowsApi
workflows_api = WorkflowsApi()
response = await workflows_api.execute_chat_workflow_api_v1_workflows_execute_chat_post({
    "message": "Hello",
    "workflow_config": {
        "enable_retrieval": True,
        "enable_tools": False,
        "retrieval_config": {
            "enabled": True,
            "max_documents": 5,
            "rerank": False
        }
    }
})
```

Benefits of the new workflow system:
- Dynamic workflow creation vs hardcoded types
- Fine-grained configuration control
- Unlimited custom workflow types
- Visual workflow builder integration
- Unified execution architecture

Migration Guide:
1. Replace ChatApi with WorkflowsApi
2. Convert hardcoded workflow types to dynamic configurations  
3. Use workflow templates for common patterns
4. Update to new response format

For detailed migration instructions, see:
docs/chat_to_workflow_migration_analysis.md
"""

import warnings
from typing import Any, Dict, Optional
from chatter_sdk.api.workflows_api import WorkflowsApi

# Issue deprecation warning when module is imported
warnings.warn(
    "ChatApi is deprecated and will be removed in v2.0.0. "
    "Use WorkflowsApi.execute_chat_workflow_* methods instead. "
    "See migration guide for details.",
    DeprecationWarning,
    stacklevel=2
)


class DeprecatedChatApi:
    """
    DEPRECATED: Use WorkflowsApi instead.
    
    This class provides backward compatibility but is scheduled for removal.
    All methods will issue deprecation warnings.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ChatApi is deprecated. Use WorkflowsApi for chat functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        self._workflows_api = WorkflowsApi(*args, **kwargs)
    
    async def chat_chat(self, chat_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        DEPRECATED: Use WorkflowsApi.execute_chat_workflow_* instead.
        """
        warnings.warn(
            "chat_chat() is deprecated. Use WorkflowsApi.execute_chat_workflow_api_v1_workflows_execute_chat_post() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Convert legacy request to new workflow format
        workflow_request = self._convert_legacy_request(chat_request)
        return await self._workflows_api.execute_chat_workflow_api_v1_workflows_execute_chat_post(
            workflow_request
        )
    
    async def streaming_chat(self, chat_request: Dict[str, Any]):
        """
        DEPRECATED: Use WorkflowsApi.execute_chat_workflow_streaming_* instead.
        """
        warnings.warn(
            "streaming_chat() is deprecated. Use WorkflowsApi.execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Convert legacy request to new workflow format
        workflow_request = self._convert_legacy_request(chat_request)
        return await self._workflows_api.execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post(
            workflow_request
        )
    
    def _convert_legacy_request(self, chat_request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy ChatRequest to new ChatWorkflowRequest format."""
        # Extract legacy workflow type
        workflow = chat_request.get("workflow", "plain")
        enable_retrieval = chat_request.get("enable_retrieval", False)
        enable_tools = chat_request.get("enable_tools", False)
        
        # Map to dynamic workflow configuration
        workflow_config = {
            "enable_retrieval": enable_retrieval,
            "enable_tools": enable_tools,
            "enable_memory": True,  # Default for chat
        }
        
        # Add model configuration if present
        if any(key in chat_request for key in ["temperature", "max_tokens"]):
            workflow_config["model_config"] = {}
            if "temperature" in chat_request:
                workflow_config["model_config"]["temperature"] = chat_request["temperature"]
            if "max_tokens" in chat_request:
                workflow_config["model_config"]["max_tokens"] = chat_request["max_tokens"]
        
        # Add retrieval configuration if enabled
        if enable_retrieval:
            workflow_config["retrieval_config"] = {
                "enabled": True,
                "max_documents": 5,
                "similarity_threshold": 0.7,
                "rerank": False,
            }
            if "document_ids" in chat_request:
                workflow_config["retrieval_config"]["document_ids"] = chat_request["document_ids"]
        
        # Build new workflow request
        workflow_request = {
            "message": chat_request["message"],
            "workflow_config": workflow_config,
        }
        
        # Copy optional fields
        for field in ["conversation_id", "profile_id", "system_prompt_override"]:
            if field in chat_request:
                workflow_request[field] = chat_request[field]
        
        return workflow_request


# Provide backward compatibility alias
ChatApi = DeprecatedChatApi