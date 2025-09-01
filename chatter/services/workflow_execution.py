"""Workflow execution service - handles chat workflows and streaming."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from chatter.core.dependencies import get_workflow_manager
from chatter.core.langgraph import ConversationState
from chatter.core.workflow_performance import (
    performance_monitor,
    workflow_cache,
)
from chatter.core.workflow_templates import WorkflowTemplateManager
from chatter.core.workflow_validation import WorkflowValidator
from chatter.models.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.services.streaming import (
    create_stream,
    stream_workflow,
    streaming_service,
)
from chatter.utils.monitoring import record_workflow_metrics
from chatter.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class WorkflowExecutionError(Exception):
    """Workflow execution error."""
    pass


class WorkflowExecutionService:
    """Service for executing chat workflows with various types and streaming."""

    def __init__(self, llm_service: LLMService, message_service: MessageService):
        """Initialize workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = WorkflowTemplateManager()
        self.validator = WorkflowValidator()

    async def execute_workflow(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute a workflow for a chat request.

        Args:
            conversation: Conversation context
            chat_request: Chat request
            correlation_id: Request correlation ID

        Returns:
            Tuple of (response_message, usage_info)

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        start_time = time.time()
        workflow_type = chat_request.workflow_type or "plain"

        try:
            # Validate workflow configuration
            self.validator.validate_workflow_parameters(
                workflow_type, **(chat_request.workflow_config or {})
            )

            # Check cache first
            # TODO: Implement proper workflow result caching
            # cache_key = self._get_cache_key(conversation.id, chat_request)
            # cached_result = await workflow_cache.get(cache_key)
            cached_result = None

            if cached_result:
                logger.debug(
                    "Workflow cache hit",
                    conversation_id=conversation.id,
                    workflow_type=workflow_type,
                    correlation_id=correlation_id
                )

                # Record metrics for cached result
                duration_ms = (time.time() - start_time) * 1000
                record_workflow_metrics(
                    workflow_type=workflow_type,
                    workflow_id=conversation.id,
                    step="cache_hit",
                    duration_ms=duration_ms,
                    success=True,
                    error_type=None,
                    correlation_id=correlation_id
                )

                return cached_result

            # Execute workflow based on type
            workflow_execution_id = f"{correlation_id}_{workflow_type}"
            performance_monitor.start_workflow(workflow_execution_id, workflow_type)
            
            if workflow_type == "plain":
                result = await self._execute_plain_workflow(
                    conversation, chat_request, correlation_id
                )
            elif workflow_type == "rag":
                result = await self._execute_rag_workflow(
                    conversation, chat_request, correlation_id
                )
            elif workflow_type == "tools":
                result = await self._execute_tools_workflow(
                    conversation, chat_request, correlation_id
                )
            elif workflow_type == "full":
                result = await self._execute_full_workflow(
                    conversation, chat_request, correlation_id
                )
            else:
                raise WorkflowExecutionError(f"Unknown workflow type: {workflow_type}")

            # Cache the result
            # TODO: Implement proper result caching with correct parameters
            # await workflow_cache.set(cache_key, result, ttl=300)  # 5 minutes

            # Record successful execution metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=workflow_type,
                workflow_id=conversation.id,
                step="complete",
                duration_ms=duration_ms,
                success=True,
                error_type=None,
                correlation_id=correlation_id
            )

            logger.info(
                "Workflow executed successfully",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                duration_ms=duration_ms,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            # Record failed execution metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=workflow_type,
                workflow_id=conversation.id,
                step="error",
                duration_ms=duration_ms,
                success=False,
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )

            logger.error(
                "Workflow execution failed",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                error=str(e),
                correlation_id=correlation_id
            )
            raise WorkflowExecutionError(f"Workflow execution failed: {e}")
        finally:
            performance_monitor.end_workflow(workflow_execution_id, success=True)

    async def execute_workflow_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a workflow with streaming response.

        Args:
            conversation: Conversation context
            chat_request: Chat request
            correlation_id: Request correlation ID

        Yields:
            Streaming chat chunks

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        start_time = time.time()
        workflow_type = chat_request.workflow_type or "plain"

        # Create streaming session
        stream_id = await create_stream(workflow_type, correlation_id)

        try:
            # Validate workflow configuration
            try:
                self.validator.validate_workflow_parameters(
                    workflow_type, **(chat_request.workflow_config or {})
                )
            except Exception as e:
                raise WorkflowExecutionError(f"Invalid workflow configuration for {workflow_type}: {e}")

            logger.info(
                "Starting streaming workflow execution",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                stream_id=stream_id,
                correlation_id=correlation_id
            )

            # Create workflow event generator
            workflow_generator = self._create_workflow_generator(
                workflow_type, conversation, chat_request, correlation_id
            )

            # Stream with heartbeat, token chunking, etc.
            async for chunk in stream_workflow(
                stream_id,
                workflow_generator,
                enable_heartbeat=True,
                heartbeat_interval=30.0
            ):
                yield chunk

            # Record successful streaming metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=f"{workflow_type}_streaming",
                workflow_id=conversation.id,
                step="complete",
                duration_ms=duration_ms,
                success=True,
                error_type=None,
                correlation_id=correlation_id
            )

            logger.info(
                "Streaming workflow completed successfully",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                stream_id=stream_id,
                duration_ms=duration_ms,
                correlation_id=correlation_id
            )

        except Exception as e:
            # Record failed streaming metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=f"{workflow_type}_streaming",
                workflow_id=conversation.id,
                step="error",
                duration_ms=duration_ms,
                success=False,
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )

            logger.error(
                "Streaming workflow execution failed",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                stream_id=stream_id,
                error=str(e),
                correlation_id=correlation_id
            )

            # Yield error chunk
            yield StreamingChatChunk(
                type="error",
                content=f"Workflow execution failed: {str(e)}",
                correlation_id=correlation_id
            )

    async def _execute_plain_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute plain chat workflow."""
        messages = self.llm_service.convert_conversation_to_messages(
            conversation, await self._get_conversation_messages(conversation)
        )

        # Add user message
        messages.append(BaseMessage(content=chat_request.message, type="human"))

        # Get LLM provider
        provider = await self.llm_service.get_default_provider()

        # Generate response
        response = await provider.ainvoke(messages)

        # Create response message
        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response.content,
            provider=provider.__class__.__name__,
            metadata={"workflow_type": "plain"}
        )

        usage_info = {"tokens": 0, "cost": 0.0}
        return response_message, usage_info

    async def _execute_rag_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute RAG workflow."""
        workflow_manager = get_workflow_manager()

        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )

        # Run RAG workflow
        result = await workflow_manager.run_workflow("rag", state)

        # Extract response
        ai_message = result.get("response")
        if not isinstance(ai_message, AIMessage):
            raise WorkflowExecutionError("Invalid RAG workflow response")

        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_message.content,
            metadata={
                "workflow_type": "rag",
                "sources": result.get("sources", []),
                "documents_used": result.get("documents_used", 0)
            }
        )

        usage_info = result.get("usage", {"tokens": 0, "cost": 0.0})
        return response_message, usage_info

    async def _execute_tools_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute tools workflow."""
        workflow_manager = get_workflow_manager()

        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )

        # Run tools workflow
        result = await workflow_manager.run_workflow("tools", state)

        # Extract response
        ai_message = result.get("response")
        if not isinstance(ai_message, AIMessage):
            raise WorkflowExecutionError("Invalid tools workflow response")

        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_message.content,
            metadata={
                "workflow_type": "tools",
                "tools_used": result.get("tools_used", []),
                "tool_calls": result.get("tool_calls", 0)
            }
        )

        usage_info = result.get("usage", {"tokens": 0, "cost": 0.0})
        return response_message, usage_info

    async def _execute_full_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute full workflow (RAG + tools)."""
        workflow_manager = get_workflow_manager()

        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )

        # Run full workflow
        result = await workflow_manager.run_workflow("full", state)

        # Extract response
        ai_message = result.get("response")
        if not isinstance(ai_message, AIMessage):
            raise WorkflowExecutionError("Invalid full workflow response")

        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_message.content,
            metadata={
                "workflow_type": "full",
                "sources": result.get("sources", []),
                "tools_used": result.get("tools_used", []),
                "documents_used": result.get("documents_used", 0),
                "tool_calls": result.get("tool_calls", 0)
            }
        )

        usage_info = result.get("usage", {"tokens": 0, "cost": 0.0})
        return response_message, usage_info

    async def _create_workflow_generator(
        self,
        workflow_type: str,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Create workflow event generator with detailed streaming.

        Args:
            workflow_type: Type of workflow
            conversation: Conversation context
            chat_request: Chat request
            correlation_id: Request correlation ID

        Yields:
            Workflow events with detailed metadata
        """
        workflow_manager = get_workflow_manager()

        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )

        # Yield start event
        yield {
            "type": "start",
            "workflow_type": workflow_type,
            "conversation_id": conversation.id,
            "timestamp": time.time()
        }

        # Streaming based on workflow type
        if workflow_type == "plain":
            async for event in self._stream_plain_workflow(state):
                yield event
        elif workflow_type in ["rag", "tools", "full"]:
            async for event in workflow_manager.stream_workflow(workflow_type, state):
                # Basic workflow events with additional metadata
                yield self._workflow_event(event, workflow_type)
        else:
            raise WorkflowExecutionError(f"Unknown workflow type: {workflow_type}")

        # Yield completion event
        yield {
            "type": "complete",
            "workflow_type": workflow_type,
            "conversation_id": conversation.id,
            "timestamp": time.time()
        }

    async def _stream_plain_workflow(
        self, state: ConversationState
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream plain workflow with token-level streaming."""
        try:
            # Convert conversation to messages
            messages = self.llm_service.convert_conversation_to_messages(
                None, state.messages  # We'll handle conversation context differently
            )

            # Add user message
            from langchain_core.messages import HumanMessage
            messages.append(HumanMessage(content=state.user_message))

            # Get LLM provider
            provider = await self.llm_service.get_default_provider()

            # Yield thinking event
            yield {
                "type": "thinking",
                "thought": "Processing request with plain workflow...",
                "step": "provider_selection",
                "provider": provider.__class__.__name__
            }

            # Stream response tokens
            token_count = 0
            response_content = ""

            # For demonstration, we'll simulate token streaming
            # In a real implementation, this would use the provider's streaming capabilities
            async for token in self._simulate_token_streaming(provider, messages):
                token_count += 1
                response_content += token

                yield {
                    "type": "token",
                    "content": token,
                    "token_index": token_count,
                    "accumulated_content": response_content,
                    "provider": provider.__class__.__name__
                }

                # Add small delay to simulate realistic streaming
                await asyncio.sleep(0.01)

            # Yield completion with usage
            yield {
                "type": "complete",
                "content": response_content,
                "usage": {
                    "tokens": token_count,
                    "input_tokens": sum(len(msg.content.split()) for msg in messages),
                    "output_tokens": token_count,
                    "cost": token_count * 0.00001  # Rough estimate
                },
                "provider": provider.__class__.__name__
            }

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "step": "plain_workflow_execution"
            }

    async def _simulate_token_streaming(
        self, provider, messages
    ) -> AsyncGenerator[str, None]:
        """Simulate token-level streaming for providers that don't support it natively."""
        try:
            # Get complete response first
            response = await provider.ainvoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Split into tokens (simple word-based tokenization for demo)
            tokens = response_text.split()

            for i, token in enumerate(tokens):
                # Add space before token (except first)
                if i > 0:
                    yield " "
                yield token

        except Exception as e:
            yield f"[Error: {str(e)}]"

    def _workflow_event(
        self, event: dict[str, Any], workflow_type: str
    ) -> dict[str, Any]:
        """Basic workflow event with additional metadata."""
        workflow_event = event.copy()

        # Add common metadata
        workflow_event["workflow_type"] = workflow_type
        workflow_event["timestamp"] = time.time()

        # Specific event types
        event_type = event.get("type")

        if event_type == "token":
            # Add token metadata
            workflow_event["token_metadata"] = {
                "character_count": len(event.get("content", "")),
                "is_punctuation": event.get("content", "").strip() in ".,!?;:",
                "is_whitespace": event.get("content", "").isspace()
            }

        elif event_type == "tool_call":
            # Add tool execution metadata
            workflow_event["tool_metadata"] = {
                "tool_category": self._categorize_tool(event.get("tool_name", "")),
                "expected_duration": self._estimate_tool_duration(event.get("tool_name", "")),
                "risk_level": self._assess_tool_risk(event.get("tool_name", ""))
            }

        elif event_type == "source":
            # Add source metadata
            workflow_event["source_metadata"] = {
                "domain": self._extract_domain(event.get("source_url", "")),
                "content_type": self._detect_content_type(event.get("source_title", "")),
                "quality_score": self._assess_source_quality(event)
            }

        return workflow_event

    def _categorize_tool(self, tool_name: str) -> str:
        """Categorize tool by type."""
        tool_categories = {
            "search": ["search", "google", "bing"],
            "computation": ["calculator", "math", "compute"],
            "data": ["database", "query", "fetch"],
            "file": ["file", "read", "write", "download"],
            "communication": ["email", "slack", "notify"]
        }

        tool_name_lower = tool_name.lower()
        for category, keywords in tool_categories.items():
            if any(keyword in tool_name_lower for keyword in keywords):
                return category

        return "general"

    def _estimate_tool_duration(self, tool_name: str) -> float:
        """Estimate tool execution duration in seconds."""
        duration_estimates = {
            "search": 2.0,
            "computation": 0.1,
            "data": 1.0,
            "file": 0.5,
            "communication": 3.0
        }

        category = self._categorize_tool(tool_name)
        return duration_estimates.get(category, 1.0)

    def _assess_tool_risk(self, tool_name: str) -> str:
        """Assess risk level of tool execution."""
        high_risk_tools = ["delete", "remove", "execute", "shell", "admin"]
        medium_risk_tools = ["write", "update", "modify", "send", "post"]

        tool_name_lower = tool_name.lower()

        if any(risk in tool_name_lower for risk in high_risk_tools):
            return "high"
        elif any(risk in tool_name_lower for risk in medium_risk_tools):
            return "medium"
        else:
            return "low"

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "unknown"

    def _detect_content_type(self, title: str) -> str:
        """Detect content type from title."""
        content_indicators = {
            "article": ["article", "blog", "post", "news"],
            "documentation": ["docs", "documentation", "guide", "manual"],
            "academic": ["paper", "research", "study", "journal"],
            "reference": ["wiki", "encyclopedia", "reference", "definition"]
        }

        title_lower = title.lower()
        for content_type, indicators in content_indicators.items():
            if any(indicator in title_lower for indicator in indicators):
                return content_type

        return "general"

    def _assess_source_quality(self, source_event: dict[str, Any]) -> float:
        """Assess quality score of a source (0.0 to 1.0)."""
        score = 0.5  # Base score

        # Factors that increase quality
        url = source_event.get("source_url", "")
        title = source_event.get("source_title", "")

        # Domain reputation
        trusted_domains = [".edu", ".gov", ".org", "wikipedia.org", "stackoverflow.com"]
        if any(domain in url for domain in trusted_domains):
            score += 0.3

        # Title quality indicators
        if len(title) > 10 and len(title) < 200:  # Reasonable title length
            score += 0.1

        # Relevance score from the event
        relevance = source_event.get("relevance_score", 0.5)
        score = (score + relevance) / 2

        return min(1.0, max(0.0, score))

    async def get_streaming_stats(self) -> dict[str, Any]:
        """Get streaming statistics."""
        base_stats = await self.get_workflow_performance_stats()

        # Add streaming stats
        streaming_stats = streaming_service.get_global_streaming_stats()

        return {
            "workflow_performance": base_stats,
            "streaming_stats": streaming_stats,
            "streaming_service_status": "active"
        }

    async def execute_streaming_workflow(
        self,
        workflow_type: str,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute streaming workflow."""
        workflow_manager = get_workflow_manager()

        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )

        # Stream workflow execution
        async for event in workflow_manager.stream_workflow(workflow_type, state):
            # Convert workflow events to streaming chunks
            if event.get("type") == "token":
                yield StreamingChatChunk(
                    type="token",
                    content=event.get("content", ""),
                    correlation_id=correlation_id
                )
            elif event.get("type") == "tool_call":
                yield StreamingChatChunk(
                    type="tool_call",
                    content=event.get("tool_name", ""),
                    correlation_id=correlation_id,
                    metadata={"tool_args": event.get("tool_args", {})}
                )
            elif event.get("type") == "source":
                yield StreamingChatChunk(
                    type="source",
                    content=event.get("source_title", ""),
                    correlation_id=correlation_id,
                    metadata={"source_url": event.get("source_url", "")}
                )
            elif event.get("type") == "complete":
                yield StreamingChatChunk(
                    type="done",
                    content="",
                    correlation_id=correlation_id,
                    metadata={
                        "usage": event.get("usage", {}),
                        "message_id": event.get("message_id")
                    }
                )

    async def _get_conversation_messages(self, conversation: Conversation) -> list[Message]:
        """Get messages for conversation in workflow format."""
        if hasattr(conversation, 'messages') and conversation.messages:
            return conversation.messages

        # Fallback to loading messages
        messages = await self.message_service.get_conversation_messages(
            conversation.id, conversation.user_id, limit=50
        )
        return list(messages)

    def _get_cache_key(self, conversation_id: str, chat_request: ChatRequest) -> str:
        """Generate cache key for workflow result."""
        import hashlib

        key_data = f"{conversation_id}:{chat_request.message}:{chat_request.workflow_type}:{chat_request.workflow_config}"
        return f"workflow:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def get_workflow_performance_stats(self) -> dict[str, Any]:
        """Get workflow performance statistics."""
        return {
            "performance_monitor": performance_monitor.get_performance_stats(),
            "cache_stats": await workflow_cache.get_stats() if hasattr(workflow_cache, 'get_stats') else {},
            "template_stats": self.template_manager.get_stats() if hasattr(self.template_manager, 'get_stats') else {}
        }
