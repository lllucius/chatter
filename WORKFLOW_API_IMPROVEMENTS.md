# 🔧 Workflow API Technical Improvements

This document provides specific technical recommendations and implementation examples for improving the workflow APIs.

## 🚨 Critical Fixes Required

### 1. Complete Streaming Implementation

**Issue**: `chat_workflow_streaming` method is referenced but not implemented in `ChatService`.

**Solution**:
```python
# In chatter/core/chat.py

async def chat_workflow_streaming(
    self, user_id: str, chat_request: ChatRequest, workflow_type: str = "basic"
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream workflow execution with real-time updates."""
    
    # Normalize workflow_type
    mode = self._normalize_workflow(workflow_type)
    
    # Setup conversation and initial state (similar to chat_with_workflow)
    conversation = await self._ensure_conversation(user_id, chat_request)
    user_msg = await self.add_message_to_conversation(
        conversation.id, user_id, chat_request.message, role="user"
    )
    
    # Prepare workflow
    provider_name = await self._resolve_provider_name(conversation, chat_request)
    retriever = await self._maybe_get_retriever(conversation, chat_request) if mode in ("rag", "full") else None
    tools = await self._maybe_get_tools(conversation, chat_request) if mode in ("tools", "full") else None
    
    workflow = await self.llm_service.create_langgraph_workflow(
        provider_name=provider_name,
        workflow_type=self._to_public_mode(mode),
        system_message=chat_request.system_prompt_override or getattr(conversation, "system_prompt", None),
        retriever=retriever,
        tools=tools,
        enable_memory=False,
    )
    
    # Prepare initial state
    history_msgs = self.llm_service.convert_conversation_to_messages(
        conversation, conversation.messages + [user_msg]
    )
    
    initial_state: ConversationState = {
        "messages": history_msgs,
        "user_id": user_id,
        "conversation_id": conversation.id,
        "retrieval_context": None,
        "tool_calls": [],
        "metadata": {},
        "conversation_summary": None,
        "parent_conversation_id": None,
        "branch_id": None,
        "memory_context": {},
        "workflow_template": None,
        "a_b_test_group": None,
    }
    
    # Stream workflow execution
    full_content = ""
    try:
        async for event in workflow_manager.stream_workflow(
            workflow=workflow, 
            initial_state=initial_state, 
            thread_id=conversation.id
        ):
            # Extract AI messages from workflow events
            if isinstance(event, dict):
                for node_name, node_data in event.items():
                    if "messages" in node_data:
                        for msg in node_data["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                content_chunk = msg.content
                                full_content += content_chunk
                                yield {
                                    "type": "token",
                                    "content": content_chunk,
                                    "node": node_name
                                }
            
        # Final usage information
        yield {
            "type": "usage",
            "usage": {
                "workflow_type": workflow_type,
                "full_content": full_content,
                "conversation_id": conversation.id
            }
        }
        
        # Persist final assistant message
        if full_content:
            await self.add_message_to_conversation(
                conversation.id, user_id, full_content, role="assistant"
            )
            await self.session.flush()
            
    except Exception as e:
        yield {"type": "error", "error": str(e)}
    finally:
        yield {"type": "end"}
```

### 2. Standardize Error Handling

**Issue**: Inconsistent exception types across layers.

**Solution**: Create a unified exception hierarchy:
```python
# In chatter/core/exceptions.py (new file)

class WorkflowError(Exception):
    """Base exception for workflow-related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.error_code = error_code or "WORKFLOW_ERROR"
        self.details = details or {}

class WorkflowConfigurationError(WorkflowError):
    """Raised when workflow configuration is invalid."""
    
    def __init__(self, message: str, workflow_type: str = None, missing_param: str = None):
        super().__init__(message, "WORKFLOW_CONFIG_ERROR", {
            "workflow_type": workflow_type,
            "missing_parameter": missing_param
        })

class WorkflowExecutionError(WorkflowError):
    """Raised when workflow execution fails."""
    
    def __init__(self, message: str, workflow_id: str = None, step: str = None):
        super().__init__(message, "WORKFLOW_EXECUTION_ERROR", {
            "workflow_id": workflow_id,
            "failed_step": step
        })

class WorkflowValidationError(WorkflowError):
    """Raised when workflow parameters are invalid."""
    
    def __init__(self, message: str, invalid_params: list[str] = None):
        super().__init__(message, "WORKFLOW_VALIDATION_ERROR", {
            "invalid_parameters": invalid_params or []
        })
```

### 3. Input Validation System

**Issue**: No validation for workflow parameters and compatibility.

**Solution**: Add comprehensive validation:
```python
# In chatter/core/workflow_validation.py (new file)

from typing import Any, List, Dict
from chatter.core.exceptions import WorkflowValidationError, WorkflowConfigurationError

class WorkflowValidator:
    """Validates workflow configurations and parameters."""
    
    REQUIRED_PARAMS = {
        "plain": [],
        "rag": ["retriever"],
        "tools": ["tools"],
        "full": ["retriever", "tools"]
    }
    
    OPTIONAL_PARAMS = {
        "all": ["system_message", "enable_memory", "memory_window"],
        "rag": ["max_documents", "similarity_threshold"],
        "tools": ["max_tool_calls", "tool_timeout"],
        "full": ["max_documents", "similarity_threshold", "max_tool_calls", "tool_timeout"]
    }
    
    @classmethod
    def validate_workflow_request(
        cls, 
        workflow_type: str, 
        retriever: Any = None, 
        tools: List[Any] = None,
        **kwargs
    ) -> None:
        """Validate workflow request parameters."""
        
        # Validate workflow type
        if workflow_type not in cls.REQUIRED_PARAMS:
            raise WorkflowValidationError(
                f"Invalid workflow type: {workflow_type}",
                invalid_params=["workflow_type"]
            )
        
        # Check required parameters
        required = cls.REQUIRED_PARAMS[workflow_type]
        missing_params = []
        
        if "retriever" in required and not retriever:
            missing_params.append("retriever")
        if "tools" in required and not tools:
            missing_params.append("tools")
            
        if missing_params:
            raise WorkflowConfigurationError(
                f"Missing required parameters for {workflow_type} workflow: {missing_params}",
                workflow_type=workflow_type,
                missing_param=", ".join(missing_params)
            )
        
        # Validate tools if provided
        if tools:
            cls._validate_tools(tools)
        
        # Validate optional parameters
        cls._validate_optional_params(workflow_type, **kwargs)
    
    @classmethod
    def _validate_tools(cls, tools: List[Any]) -> None:
        """Validate tool objects."""
        if not isinstance(tools, list):
            raise WorkflowValidationError("Tools must be a list")
        
        for i, tool in enumerate(tools):
            if not hasattr(tool, "name") and not hasattr(tool, "__name__"):
                raise WorkflowValidationError(
                    f"Tool at index {i} missing name attribute",
                    invalid_params=[f"tools[{i}]"]
                )
    
    @classmethod
    def _validate_optional_params(cls, workflow_type: str, **kwargs) -> None:
        """Validate optional parameters."""
        valid_params = set(cls.OPTIONAL_PARAMS.get("all", []))
        valid_params.update(cls.OPTIONAL_PARAMS.get(workflow_type, []))
        
        invalid_params = []
        for param in kwargs:
            if param not in valid_params:
                invalid_params.append(param)
        
        if invalid_params:
            raise WorkflowValidationError(
                f"Invalid parameters for {workflow_type} workflow: {invalid_params}",
                invalid_params=invalid_params
            )
```

## 🔄 Enhanced Workflow Features

### 1. Workflow Templates

Create pre-configured workflow templates for common use cases:

```python
# In chatter/core/workflow_templates.py (new file)

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class WorkflowTemplate:
    """Pre-configured workflow template."""
    name: str
    workflow_type: str
    description: str
    default_params: Dict[str, Any]
    required_tools: Optional[List[str]] = None
    required_retrievers: Optional[List[str]] = None

# Built-in templates
WORKFLOW_TEMPLATES = {
    "customer_support": WorkflowTemplate(
        name="customer_support",
        workflow_type="full",
        description="Customer support with knowledge base and tools",
        default_params={
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 5,
            "system_message": "You are a helpful customer support assistant."
        },
        required_tools=["search_kb", "create_ticket", "escalate"],
        required_retrievers=["support_docs"]
    ),
    
    "code_assistant": WorkflowTemplate(
        name="code_assistant",
        workflow_type="tools",
        description="Programming assistant with code tools",
        default_params={
            "enable_memory": True,
            "memory_window": 100,
            "max_tool_calls": 10,
            "system_message": "You are an expert programming assistant."
        },
        required_tools=["execute_code", "search_docs", "generate_tests"]
    ),
    
    "research_assistant": WorkflowTemplate(
        name="research_assistant",
        workflow_type="rag",
        description="Research assistant with document retrieval",
        default_params={
            "enable_memory": True,
            "memory_window": 30,
            "max_documents": 10,
            "system_message": "You are a research assistant. Use the provided documents to answer questions."
        },
        required_retrievers=["research_docs"]
    )
}

class WorkflowTemplateManager:
    """Manages workflow templates."""
    
    @classmethod
    def get_template(cls, template_name: str) -> WorkflowTemplate:
        """Get a workflow template by name."""
        if template_name not in WORKFLOW_TEMPLATES:
            raise WorkflowConfigurationError(f"Template '{template_name}' not found")
        return WORKFLOW_TEMPLATES[template_name]
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List available template names."""
        return list(WORKFLOW_TEMPLATES.keys())
    
    @classmethod
    async def create_workflow_from_template(
        cls, 
        template_name: str, 
        llm_service: Any,
        provider_name: str,
        overrides: Dict[str, Any] = None
    ):
        """Create a workflow from a template."""
        template = cls.get_template(template_name)
        params = template.default_params.copy()
        if overrides:
            params.update(overrides)
        
        return await llm_service.create_langgraph_workflow(
            provider_name=provider_name,
            workflow_type=template.workflow_type,
            **params
        )
```

### 2. Workflow Middleware System

Add middleware for cross-cutting concerns:

```python
# In chatter/core/workflow_middleware.py (new file)

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from chatter.core.langgraph import ConversationState

class WorkflowMiddleware(ABC):
    """Base class for workflow middleware."""
    
    @abstractmethod
    async def before_execution(self, state: ConversationState) -> ConversationState:
        """Process state before workflow execution."""
        pass
    
    @abstractmethod
    async def after_execution(self, state: ConversationState) -> ConversationState:
        """Process state after workflow execution."""
        pass

class LoggingMiddleware(WorkflowMiddleware):
    """Logs workflow executions."""
    
    async def before_execution(self, state: ConversationState) -> ConversationState:
        logger.info(
            "Workflow execution started",
            conversation_id=state.get("conversation_id"),
            user_id=state.get("user_id"),
            message_count=len(state.get("messages", []))
        )
        return state
    
    async def after_execution(self, state: ConversationState) -> ConversationState:
        logger.info(
            "Workflow execution completed",
            conversation_id=state.get("conversation_id"),
            final_message_count=len(state.get("messages", []))
        )
        return state

class RateLimitingMiddleware(WorkflowMiddleware):
    """Apply rate limiting per user."""
    
    def __init__(self, max_requests_per_hour: int = 100):
        self.max_requests = max_requests_per_hour
        self.request_counts: Dict[str, List[float]] = {}
    
    async def before_execution(self, state: ConversationState) -> ConversationState:
        user_id = state.get("user_id")
        now = time.time()
        
        # Clean old requests
        if user_id in self.request_counts:
            self.request_counts[user_id] = [
                req_time for req_time in self.request_counts[user_id]
                if now - req_time < 3600  # 1 hour
            ]
        else:
            self.request_counts[user_id] = []
        
        # Check rate limit
        if len(self.request_counts[user_id]) >= self.max_requests:
            raise WorkflowExecutionError(
                f"Rate limit exceeded for user {user_id}",
                workflow_id=state.get("conversation_id")
            )
        
        # Record request
        self.request_counts[user_id].append(now)
        return state
    
    async def after_execution(self, state: ConversationState) -> ConversationState:
        return state

class ContentFilterMiddleware(WorkflowMiddleware):
    """Filter inappropriate content."""
    
    def __init__(self, blocked_words: List[str] = None):
        self.blocked_words = blocked_words or []
    
    async def before_execution(self, state: ConversationState) -> ConversationState:
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "content"):
                for word in self.blocked_words:
                    if word.lower() in last_message.content.lower():
                        raise WorkflowExecutionError(
                            "Content violates content policy",
                            workflow_id=state.get("conversation_id")
                        )
        return state
    
    async def after_execution(self, state: ConversationState) -> ConversationState:
        return state

class MiddlewareManager:
    """Manages workflow middleware."""
    
    def __init__(self):
        self.middleware: List[WorkflowMiddleware] = []
    
    def add_middleware(self, middleware: WorkflowMiddleware):
        """Add middleware to the stack."""
        self.middleware.append(middleware)
    
    async def process_before(self, state: ConversationState) -> ConversationState:
        """Process all before middleware."""
        for middleware in self.middleware:
            state = await middleware.before_execution(state)
        return state
    
    async def process_after(self, state: ConversationState) -> ConversationState:
        """Process all after middleware."""
        for middleware in reversed(self.middleware):
            state = await middleware.after_execution(state)
        return state
```

### 3. Performance Optimizations

Add caching and optimization features:

```python
# In chatter/core/workflow_cache.py (new file)

import hashlib
import pickle
from functools import lru_cache
from typing import Any, Dict, Optional
from langgraph.pregel import Pregel

class WorkflowCache:
    """Cache for compiled workflows."""
    
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Pregel] = {}
        self.max_size = max_size
        self.access_order: List[str] = []
    
    def _generate_cache_key(
        self, 
        provider_name: str, 
        workflow_type: str, 
        config: Dict[str, Any]
    ) -> str:
        """Generate cache key for workflow configuration."""
        # Create deterministic hash of configuration
        config_str = f"{provider_name}:{workflow_type}:{sorted(config.items())}"
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def get(
        self, 
        provider_name: str, 
        workflow_type: str, 
        config: Dict[str, Any]
    ) -> Optional[Pregel]:
        """Get cached workflow."""
        cache_key = self._generate_cache_key(provider_name, workflow_type, config)
        
        if cache_key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(cache_key)
            self.access_order.append(cache_key)
            return self.cache[cache_key]
        
        return None
    
    def put(
        self, 
        provider_name: str, 
        workflow_type: str, 
        config: Dict[str, Any], 
        workflow: Pregel
    ):
        """Cache compiled workflow."""
        cache_key = self._generate_cache_key(provider_name, workflow_type, config)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[cache_key] = workflow
        if cache_key not in self.access_order:
            self.access_order.append(cache_key)
    
    def clear(self):
        """Clear all cached workflows."""
        self.cache.clear()
        self.access_order.clear()

# Global cache instance
workflow_cache = WorkflowCache()

class LazyToolLoader:
    """Lazy loading for tools to improve performance."""
    
    def __init__(self):
        self._tool_cache: Dict[str, Any] = {}
    
    async def get_tools(self, required_tools: List[str] = None) -> List[Any]:
        """Get tools, loading only what's needed."""
        if not required_tools:
            # Load all tools (current behavior)
            return await self._load_all_tools()
        
        tools = []
        for tool_name in required_tools:
            if tool_name not in self._tool_cache:
                self._tool_cache[tool_name] = await self._load_tool(tool_name)
            tools.append(self._tool_cache[tool_name])
        
        return tools
    
    async def _load_all_tools(self) -> List[Any]:
        """Load all available tools."""
        from chatter.services.mcp import mcp_service, BuiltInTools
        
        mcp_tools = await mcp_service.get_tools()
        builtin_tools = BuiltInTools.create_builtin_tools()
        return mcp_tools + builtin_tools
    
    async def _load_tool(self, tool_name: str) -> Any:
        """Load a specific tool by name."""
        # Implementation depends on tool registry structure
        all_tools = await self._load_all_tools()
        for tool in all_tools:
            if getattr(tool, "name", None) == tool_name:
                return tool
        raise ValueError(f"Tool '{tool_name}' not found")
```

## 📝 API Improvements

### Enhanced Request Schema

```python
# In chatter/schemas/chat.py - Enhanced ChatRequest

class ChatRequest(BaseModel):
    """Enhanced schema for chat request."""
    
    message: str = Field(..., description="User message")
    conversation_id: str | None = Field(None, description="Conversation ID")
    profile_id: str | None = Field(None, description="Profile ID")
    stream: bool = Field(default=False, description="Enable streaming")
    
    # Workflow configuration
    workflow: WorkflowType = Field(default="plain", description="Workflow type")
    workflow_template: str | None = Field(None, description="Use predefined template")
    workflow_config: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")
    
    # Advanced options
    provider: str | None = Field(None, description="LLM provider override")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int | None = Field(None, ge=1, le=8192, description="Max tokens")
    
    # Context options
    system_prompt_override: str | None = Field(None, description="System prompt override")
    document_ids: List[str] | None = Field(None, description="Document IDs for context")
    enable_memory: bool = Field(default=False, description="Enable conversation memory")
    memory_window: int = Field(default=20, ge=1, le=200, description="Memory window size")
    
    # Tool options
    allowed_tools: List[str] | None = Field(None, description="Allowed tools for this request")
    max_tool_calls: int = Field(default=5, ge=1, le=20, description="Max tool calls")
    
    @validator("workflow_config")
    def validate_workflow_config(cls, v, values):
        """Validate workflow configuration."""
        workflow_type = values.get("workflow", "plain")
        if workflow_type and v:
            WorkflowValidator.validate_workflow_request(workflow_type, **v)
        return v
```

This technical improvement document provides concrete implementation examples for addressing the critical issues identified in the main analysis report. The solutions focus on maintainability, performance, and extensibility while preserving backward compatibility.