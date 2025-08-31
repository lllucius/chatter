"""DEPRECATED: Legacy chat service - moved to chat_deprecated.py

The ChatService in this module has been replaced by RefactoredChatService
which uses a microservice architecture with specialized services:

- ConversationService: CRUD operations for conversations
- MessageService: CRUD operations for messages  
- WorkflowExecutionService: Workflow execution and streaming

Use RefactoredChatService from chatter.services.chat_refactored instead.
"""

# This file contains the original ChatService implementation for reference only.
# It should not be imported or used in production code.

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.dependencies import get_workflow_manager
from chatter.core.langgraph import ConversationState
from chatter.core.workflow_performance import (
    lazy_tool_loader,
    performance_monitor,
    workflow_cache,
)
from chatter.core.workflow_templates import WorkflowTemplateManager
from chatter.core.workflow_validation import WorkflowValidator
from chatter.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.schemas.chat import (
    ConversationCreate as ConversationCreateSchema,
)
from chatter.schemas.chat import (
    ConversationUpdate as ConversationUpdateSchema,
)
from chatter.services.llm import LLMProviderError, LLMService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# (Original ChatService implementation would be here for reference)
# This has been moved to preserve it while transitioning to RefactoredChatService