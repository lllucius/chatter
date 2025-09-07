"""Workflow execution strategy pattern implementation.

This module provides focused executor classes for each workflow type,
decomposing the monolithic WorkflowExecutionService into manageable components.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessage

from chatter.core.dependencies import get_workflow_manager
from chatter.core.langgraph import ConversationState
from chatter.core.monitoring import record_workflow_metrics
from chatter.core.workflow_limits import (
    WorkflowLimits,
    WorkflowResourceLimitError,
    workflow_limit_manager,
)
from chatter.core.workflow_performance import performance_monitor
from chatter.models.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService

logger = logging.getLogger(__name__)


class WorkflowExecutionError(Exception):
    """Workflow execution error."""

    pass


class BaseWorkflowExecutor(ABC):
    """Base class for workflow executors using strategy pattern."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        template_manager,
    ):
        """Initialize base workflow executor."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = template_manager
        self.limit_manager = workflow_limit_manager

    @property
    @abstractmethod
    def workflow_type(self) -> str:
        """Get the workflow type this executor handles."""
        pass

    @abstractmethod
    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute the workflow for this type."""
        pass

    @abstractmethod
    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute the workflow with streaming for this type."""
        pass

    async def _setup_execution(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[str, WorkflowLimits]:
        """Common setup for workflow execution."""
        workflow_id = f"{correlation_id}_{self.workflow_type}"

        # Use provided limits or get defaults
        if limits is None:
            limits = self.limit_manager.get_default_limits()

        # Start resource tracking if user_id provided
        if user_id:
            try:
                self.limit_manager.start_workflow_tracking(
                    workflow_id, user_id, limits
                )
            except WorkflowResourceLimitError as e:
                logger.warning(
                    "Workflow rejected due to resource limits",
                    extra={
                        "user_id": user_id,
                        "error": str(e),
                        "correlation_id": correlation_id,
                    },
                )
                raise WorkflowExecutionError(
                    f"Resource limit exceeded: {e}"
                ) from e

        return workflow_id, limits

    async def _record_metrics(
        self,
        workflow_id: str,
        step: str,
        start_time: float,
        success: bool,
        error_type: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Record workflow execution metrics."""
        duration_ms = (time.time() - start_time) * 1000
        record_workflow_metrics(
            workflow_type=self.workflow_type,
            workflow_id=workflow_id,
            step=step,
            duration_ms=duration_ms,
            success=success,
            error_type=error_type,
            correlation_id=correlation_id,
        )


class PlainWorkflowExecutor(BaseWorkflowExecutor):
    """Executor for plain chat workflows (no tools, no RAG)."""

    @property
    def workflow_type(self) -> str:
        return "plain"

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute plain workflow."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Create and execute plain workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                enable_memory=True,
                memory_window=20,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation context
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=20
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            # Add current message
            messages.append(
                {"role": "human", "content": chat_request.message}
            )

            # Execute workflow
            state = ConversationState(messages=messages)
            result = await workflow.ainvoke(
                state, {"configurable": {"thread_id": conversation.id}}
            )

            # Extract response
            if isinstance(result["messages"][-1], AIMessage):
                response_content = result["messages"][-1].content
            else:
                response_content = str(result["messages"][-1])

            # Create response message
            assistant_message = (
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=response_content,
                )
            )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                True,
                correlation_id=correlation_id,
            )

            return assistant_message, {"usage": result.get("usage", {})}

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"Plain workflow execution failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute plain workflow with streaming."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Create streaming workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                enable_memory=True,
                memory_window=20,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation state
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=20
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            messages.append(
                {"role": "human", "content": chat_request.message}
            )
            state = ConversationState(messages=messages)

            # Stream workflow execution
            content_buffer = ""
            async for event in workflow.astream(
                state, {"configurable": {"thread_id": conversation.id}}
            ):
                if "messages" in event:
                    message = event["messages"][-1]
                    if hasattr(message, "content") and message.content:
                        # Extract new content since last chunk
                        if len(message.content) > len(content_buffer):
                            new_content = message.content[
                                len(content_buffer) :
                            ]
                            content_buffer = message.content

                            yield StreamingChatChunk(
                                id=correlation_id,
                                content=new_content,
                                role="assistant",
                                conversation_id=conversation.id,
                            )

            # Create final message
            if content_buffer:
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=content_buffer,
                )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                True,
                correlation_id=correlation_id,
            )

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"Plain workflow streaming failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )


class RAGWorkflowExecutor(BaseWorkflowExecutor):
    """Executor for RAG workflows (retrieval-augmented generation)."""

    @property
    def workflow_type(self) -> str:
        return "rag"

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute RAG workflow."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Get retriever from workflow manager
            workflow_manager = get_workflow_manager()
            retriever = workflow_manager.get_retriever(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )

            # Create RAG workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                retriever=retriever,
                enable_memory=True,
                memory_window=30,
                max_documents=10,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation context
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=30
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            messages.append(
                {"role": "human", "content": chat_request.message}
            )

            # Execute workflow
            state = ConversationState(messages=messages)
            result = await workflow.ainvoke(
                state, {"configurable": {"thread_id": conversation.id}}
            )

            # Extract response
            if isinstance(result["messages"][-1], AIMessage):
                response_content = result["messages"][-1].content
            else:
                response_content = str(result["messages"][-1])

            # Create response message
            assistant_message = (
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=response_content,
                )
            )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                True,
                correlation_id=correlation_id,
            )

            return assistant_message, {"usage": result.get("usage", {})}

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"RAG workflow execution failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute RAG workflow with streaming."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Get retriever from workflow manager
            workflow_manager = get_workflow_manager()
            retriever = workflow_manager.get_retriever(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )

            # Create streaming RAG workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                retriever=retriever,
                enable_memory=True,
                memory_window=30,
                max_documents=10,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation state
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=30
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            messages.append(
                {"role": "human", "content": chat_request.message}
            )
            state = ConversationState(messages=messages)

            # Stream workflow execution
            content_buffer = ""
            async for event in workflow.astream(
                state, {"configurable": {"thread_id": conversation.id}}
            ):
                if "messages" in event:
                    message = event["messages"][-1]
                    if hasattr(message, "content") and message.content:
                        # Extract new content since last chunk
                        if len(message.content) > len(content_buffer):
                            new_content = message.content[
                                len(content_buffer) :
                            ]
                            content_buffer = message.content

                            yield StreamingChatChunk(
                                id=correlation_id,
                                content=new_content,
                                role="assistant",
                                conversation_id=conversation.id,
                            )

            # Create final message
            if content_buffer:
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=content_buffer,
                )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                True,
                correlation_id=correlation_id,
            )

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"RAG workflow streaming failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )


class ToolsWorkflowExecutor(BaseWorkflowExecutor):
    """Executor for tools-based workflows."""

    @property
    def workflow_type(self) -> str:
        return "tools"

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute tools workflow."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Get tools from workflow manager
            workflow_manager = get_workflow_manager()
            tools = workflow_manager.get_tools(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )

            # Create tools workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                tools=tools,
                enable_memory=True,
                memory_window=100,
                max_tool_calls=10,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation context
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=100
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            messages.append(
                {"role": "human", "content": chat_request.message}
            )

            # Execute workflow
            state = ConversationState(messages=messages)
            result = await workflow.ainvoke(
                state, {"configurable": {"thread_id": conversation.id}}
            )

            # Extract response
            if isinstance(result["messages"][-1], AIMessage):
                response_content = result["messages"][-1].content
            else:
                response_content = str(result["messages"][-1])

            # Create response message
            assistant_message = (
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=response_content,
                )
            )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                True,
                correlation_id=correlation_id,
            )

            return assistant_message, {"usage": result.get("usage", {})}

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"Tools workflow execution failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute tools workflow with streaming."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Get tools from workflow manager
            workflow_manager = get_workflow_manager()
            tools = workflow_manager.get_tools(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )

            # Create streaming tools workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                tools=tools,
                enable_memory=True,
                memory_window=100,
                max_tool_calls=10,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation state
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=100
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            messages.append(
                {"role": "human", "content": chat_request.message}
            )
            state = ConversationState(messages=messages)

            # Stream workflow execution
            content_buffer = ""
            async for event in workflow.astream(
                state, {"configurable": {"thread_id": conversation.id}}
            ):
                if "messages" in event:
                    message = event["messages"][-1]
                    if hasattr(message, "content") and message.content:
                        # Extract new content since last chunk
                        if len(message.content) > len(content_buffer):
                            new_content = message.content[
                                len(content_buffer) :
                            ]
                            content_buffer = message.content

                            yield StreamingChatChunk(
                                id=correlation_id,
                                content=new_content,
                                role="assistant",
                                conversation_id=conversation.id,
                            )

            # Create final message
            if content_buffer:
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=content_buffer,
                )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                True,
                correlation_id=correlation_id,
            )

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"Tools workflow streaming failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )


class FullWorkflowExecutor(BaseWorkflowExecutor):
    """Executor for full workflows (tools + RAG)."""

    @property
    def workflow_type(self) -> str:
        return "full"

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute full workflow."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Get tools and retriever from workflow manager
            workflow_manager = get_workflow_manager()
            tools = workflow_manager.get_tools(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )
            retriever = workflow_manager.get_retriever(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )

            # Create full workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                tools=tools,
                retriever=retriever,
                enable_memory=True,
                memory_window=50,
                max_tool_calls=5,
                max_documents=10,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation context
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=50
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            messages.append(
                {"role": "human", "content": chat_request.message}
            )

            # Execute workflow
            state = ConversationState(messages=messages)
            result = await workflow.ainvoke(
                state, {"configurable": {"thread_id": conversation.id}}
            )

            # Extract response
            if isinstance(result["messages"][-1], AIMessage):
                response_content = result["messages"][-1].content
            else:
                response_content = str(result["messages"][-1])

            # Create response message
            assistant_message = (
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=response_content,
                )
            )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                True,
                correlation_id=correlation_id,
            )

            return assistant_message, {"usage": result.get("usage", {})}

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "execute",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"Full workflow execution failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute full workflow with streaming."""
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits
        )

        try:
            # Start performance monitoring
            performance_monitor.start_workflow(
                workflow_id, self.workflow_type
            )

            # Get tools and retriever from workflow manager
            workflow_manager = get_workflow_manager()
            tools = workflow_manager.get_tools(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )
            retriever = workflow_manager.get_retriever(
                conversation.workspace_id
                if conversation.workspace_id
                else "default"
            )

            # Create streaming full workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=self.workflow_type,
                tools=tools,
                retriever=retriever,
                enable_memory=True,
                memory_window=50,
                max_tool_calls=5,
                max_documents=10,
                system_message=chat_request.system_prompt_override,
            )

            # Prepare conversation state
            messages = []
            recent_messages = (
                await self.message_service.get_recent_messages(
                    conversation.id, limit=50
                )
            )

            for msg in recent_messages:
                if msg.role == MessageRole.USER:
                    messages.append(
                        {"role": "human", "content": msg.content}
                    )
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(
                        {"role": "ai", "content": msg.content}
                    )

            messages.append(
                {"role": "human", "content": chat_request.message}
            )
            state = ConversationState(messages=messages)

            # Stream workflow execution
            content_buffer = ""
            async for event in workflow.astream(
                state, {"configurable": {"thread_id": conversation.id}}
            ):
                if "messages" in event:
                    message = event["messages"][-1]
                    if hasattr(message, "content") and message.content:
                        # Extract new content since last chunk
                        if len(message.content) > len(content_buffer):
                            new_content = message.content[
                                len(content_buffer) :
                            ]
                            content_buffer = message.content

                            yield StreamingChatChunk(
                                id=correlation_id,
                                content=new_content,
                                role="assistant",
                                conversation_id=conversation.id,
                            )

            # Create final message
            if content_buffer:
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=content_buffer,
                )

            # Record success metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                True,
                correlation_id=correlation_id,
            )

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id,
                "stream",
                start_time,
                False,
                error_type=type(e).__name__,
                correlation_id=correlation_id,
            )
            raise WorkflowExecutionError(
                f"Full workflow streaming failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(
                    workflow_id, user_id
                )


class WorkflowExecutorFactory:
    """Factory for creating workflow executors based on type."""

    _executors = {
        "plain": PlainWorkflowExecutor,
        "rag": RAGWorkflowExecutor,
        "tools": ToolsWorkflowExecutor,
        "full": FullWorkflowExecutor,
    }

    @classmethod
    def create_executor(
        self,
        workflow_type: str,
        llm_service: LLMService,
        message_service: MessageService,
        template_manager,
    ) -> BaseWorkflowExecutor:
        """Create a workflow executor for the specified type."""
        if workflow_type not in self._executors:
            raise ValueError(
                f"Unsupported workflow type: {workflow_type}"
            )

        executor_class = self._executors[workflow_type]
        return executor_class(
            llm_service, message_service, template_manager
        )

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported workflow types."""
        return list(cls._executors.keys())
