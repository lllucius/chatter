"""Service for token-level streaming with comprehensive workflow support."""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from enum import Enum
from typing import Any

from chatter.core.monitoring import record_workflow_metrics
from chatter.schemas.chat import StreamingChatChunk
from chatter.utils.correlation import get_correlation_id
from chatter.utils.security_enhanced import get_secure_logger

logger = get_secure_logger(__name__)


class StreamingEventType(str, Enum):
    """Types of streaming events."""

    START = "start"
    TOKEN = "token"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_END = "tool_call_end"
    SOURCE_FOUND = "source_found"
    THINKING = "thinking"
    ERROR = "error"
    COMPLETE = "complete"
    METADATA = "metadata"
    HEARTBEAT = "heartbeat"


@dataclass
class StreamingEvent:
    """Internal streaming event representation."""

    event_type: StreamingEventType
    content: str | None = None
    metadata: dict[str, Any] | None = None
    timestamp: float | None = None
    correlation_id: str = ""

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()
    
    @property
    def type(self) -> StreamingEventType:
        """Alias for event_type for backwards compatibility."""
        return self.event_type


class StreamingError(Exception):
    """Exception raised during streaming operations."""

    def __init__(
        self, message: str, event_type: StreamingEventType | None = None
    ):
        super().__init__(message)
        self.event_type = event_type


class StreamingService:
    """Streaming service with token-level streaming and comprehensive workflow support."""

    def __init__(self):
        """Initialize streaming service."""
        self.active_streams: dict[str, dict[str, Any]] = {}
        self.stream_metrics: dict[str, dict[str, Any]] = {}

    async def create_stream(
        self,
        stream_id: str,
        workflow_type: str,
        correlation_id: str | None = None,
    ) -> None:
        """Create a new streaming session.

        Args:
            stream_id: Unique stream identifier
            workflow_type: Type of workflow being streamed
            correlation_id: Optional correlation ID
        """
        if correlation_id is None:
            correlation_id = get_correlation_id()

        self.active_streams[stream_id] = {
            "workflow_type": workflow_type,
            "correlation_id": correlation_id,
            "start_time": time.time(),
            "token_count": 0,
            "event_count": 0,
            "last_activity": time.time(),
        }

        self.stream_metrics[stream_id] = {
            "tokens_per_second": 0.0,
            "events_per_second": 0.0,
            "total_duration": 0.0,
            "error_count": 0,
        }

        logger.info(
            "Created streaming session",
            stream_id=stream_id,
            workflow_type=workflow_type,
            correlation_id=correlation_id,
        )

    async def end_stream(self, stream_id: str) -> dict[str, Any]:
        """End a streaming session and return metrics.

        Args:
            stream_id: Stream identifier

        Returns:
            Stream metrics
        """
        if stream_id not in self.active_streams:
            return {}

        stream_info = self.active_streams[stream_id]
        metrics = self.stream_metrics[stream_id]

        # Calculate final metrics
        total_duration = time.time() - stream_info["start_time"]
        metrics["total_duration"] = total_duration

        if total_duration > 0:
            metrics["tokens_per_second"] = (
                stream_info["token_count"] / total_duration
            )
            metrics["events_per_second"] = (
                stream_info["event_count"] / total_duration
            )

        # Record workflow metrics
        record_workflow_metrics(
            workflow_type=f"{stream_info['workflow_type']}_streaming",
            workflow_id=stream_id,
            step="complete",
            duration_ms=total_duration * 1000,
            success=metrics["error_count"] == 0,
            error_type=None,
            correlation_id=stream_info["correlation_id"],
        )

        logger.info(
            "Ended streaming session",
            stream_id=stream_id,
            duration_seconds=total_duration,
            token_count=stream_info["token_count"],
            tokens_per_second=metrics["tokens_per_second"],
            correlation_id=stream_info["correlation_id"],
        )

        # Clean up
        final_metrics = metrics.copy()
        final_metrics.update(stream_info)
        del self.active_streams[stream_id]
        del self.stream_metrics[stream_id]

        return final_metrics

    async def stream_tokens(
        self,
        stream_id: str,
        token_generator: AsyncGenerator[str, None],
        chunk_size: int = 1,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream tokens with configurable chunking.

        Args:
            stream_id: Stream identifier
            token_generator: Async generator yielding tokens
            chunk_size: Number of tokens per chunk

        Yields:
            Streaming chat chunks with tokens
        """
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        try:
            token_buffer = []

            async for token in token_generator:
                token_buffer.append(token)
                stream_info["token_count"] += 1
                stream_info["last_activity"] = time.time()

                # Yield chunk when buffer is full or on sentence boundaries
                if len(
                    token_buffer
                ) >= chunk_size or self._is_sentence_boundary(token):

                    chunk_content = "".join(token_buffer)
                    token_buffer = []

                    yield StreamingChatChunk(
                        type="token",
                        content=chunk_content,
                        correlation_id=correlation_id,
                        metadata={
                            "stream_id": stream_id,
                            "token_count": stream_info["token_count"],
                            "timestamp": time.time(),
                        },
                    )

                    stream_info["event_count"] += 1

            # Yield any remaining tokens
            if token_buffer:
                chunk_content = "".join(token_buffer)
                yield StreamingChatChunk(
                    type="token",
                    content=chunk_content,
                    correlation_id=correlation_id,
                    metadata={
                        "stream_id": stream_id,
                        "token_count": stream_info["token_count"],
                        "final_chunk": True,
                    },
                )

        except Exception as e:
            self.stream_metrics[stream_id]["error_count"] += 1
            logger.error(
                "Error in token streaming",
                stream_id=stream_id,
                error=str(e),
                correlation_id=correlation_id,
            )
            raise

    async def stream_workflow_events(
        self,
        stream_id: str,
        event_generator: AsyncGenerator[dict[str, Any], None],
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream workflow events with processing.

        Args:
            stream_id: Stream identifier
            event_generator: Async generator yielding workflow events

        Yields:
            Streaming chat chunks for workflow events
        """
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        try:
            async for event in event_generator:
                stream_info["event_count"] += 1
                stream_info["last_activity"] = time.time()

                # Process different event types
                event_type = event.get("type", "unknown")

                if event_type == "token":
                    yield StreamingChatChunk(
                        type="token",
                        content=event.get("content", ""),
                        correlation_id=correlation_id,
                        metadata={
                            "stream_id": stream_id,
                            "event_index": stream_info["event_count"],
                        },
                    )

                elif event_type == "tool_call":
                    yield StreamingChatChunk(
                        type="tool_call_start",
                        content=event.get("tool_name", ""),
                        correlation_id=correlation_id,
                        metadata={
                            "tool_args": event.get("tool_args", {}),
                            "tool_id": event.get("tool_id"),
                        },
                    )

                elif event_type == "tool_result":
                    yield StreamingChatChunk(
                        type="tool_call_end",
                        content=event.get("result", ""),
                        correlation_id=correlation_id,
                        metadata={
                            "tool_name": event.get("tool_name"),
                            "success": event.get("success", True),
                            "execution_time": event.get(
                                "execution_time", 0
                            ),
                        },
                    )

                elif event_type == "source":
                    yield StreamingChatChunk(
                        type="source_found",
                        content=event.get("source_title", ""),
                        correlation_id=correlation_id,
                        metadata={
                            "source_url": event.get("source_url"),
                            "relevance_score": event.get(
                                "relevance_score"
                            ),
                            "source_type": event.get("source_type"),
                        },
                    )

                elif event_type == "thinking":
                    yield StreamingChatChunk(
                        type="thinking",
                        content=event.get("thought", ""),
                        correlation_id=correlation_id,
                        metadata={
                            "reasoning_step": event.get("step"),
                            "confidence": event.get("confidence"),
                        },
                    )

                elif event_type == "error":
                    self.stream_metrics[stream_id]["error_count"] += 1
                    yield StreamingChatChunk(
                        type="error",
                        content=event.get("error", "Unknown error"),
                        correlation_id=correlation_id,
                        metadata={
                            "error_type": event.get("error_type"),
                            "recoverable": event.get(
                                "recoverable", False
                            ),
                        },
                    )

                elif event_type == "complete":
                    yield StreamingChatChunk(
                        type="complete",
                        content="",
                        correlation_id=correlation_id,
                        metadata={
                            "usage": event.get("usage", {}),
                            "message_id": event.get("message_id"),
                            "total_tokens": event.get(
                                "total_tokens", 0
                            ),
                            "total_cost": event.get("total_cost", 0.0),
                        },
                    )

        except Exception as e:
            self.stream_metrics[stream_id]["error_count"] += 1
            logger.error(
                "Error in workflow event streaming",
                stream_id=stream_id,
                error=str(e),
                correlation_id=correlation_id,
            )

            yield StreamingChatChunk(
                type="error",
                content=f"Streaming error: {str(e)}",
                correlation_id=correlation_id,
            )

    async def stream_with_heartbeat(
        self,
        stream_id: str,
        content_generator: AsyncGenerator[StreamingChatChunk, None],
        heartbeat_interval: float = 30.0,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream with periodic heartbeat to keep connection alive.

        Args:
            stream_id: Stream identifier
            content_generator: Generator for actual content
            heartbeat_interval: Seconds between heartbeats

        Yields:
            Content chunks and heartbeat chunks
        """
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        last_heartbeat = time.time()

        try:
            async for chunk in content_generator:
                yield chunk

                # Send heartbeat if interval exceeded
                current_time = time.time()
                if current_time - last_heartbeat > heartbeat_interval:
                    yield StreamingChatChunk(
                        type="heartbeat",
                        content="",
                        correlation_id=correlation_id,
                        metadata={
                            "timestamp": current_time,
                            "stream_id": stream_id,
                            "uptime": current_time
                            - stream_info["start_time"],
                        },
                    )
                    last_heartbeat = current_time

        except Exception as e:
            logger.error(
                "Error in heartbeat streaming",
                stream_id=stream_id,
                error=str(e),
                correlation_id=correlation_id,
            )
            raise

    def _is_sentence_boundary(self, token: str) -> bool:
        """Check if token represents a sentence boundary."""
        return token.strip() in {".", "!", "?", "\n", "\n\n"}

    async def get_stream_status(
        self, stream_id: str
    ) -> dict[str, Any] | None:
        """Get status of an active stream.

        Args:
            stream_id: Stream identifier

        Returns:
            Stream status or None if not found
        """
        if stream_id not in self.active_streams:
            return None

        stream_info = self.active_streams[stream_id]
        metrics = self.stream_metrics[stream_id]

        current_time = time.time()
        duration = current_time - stream_info["start_time"]

        return {
            "stream_id": stream_id,
            "workflow_type": stream_info["workflow_type"],
            "correlation_id": stream_info["correlation_id"],
            "status": "active",
            "duration_seconds": duration,
            "token_count": stream_info["token_count"],
            "event_count": stream_info["event_count"],
            "tokens_per_second": (
                stream_info["token_count"] / duration
                if duration > 0
                else 0
            ),
            "last_activity": stream_info["last_activity"],
            "error_count": metrics["error_count"],
        }

    async def cleanup_inactive_streams(
        self, timeout_seconds: float = 300.0
    ) -> int:
        """Clean up streams that have been inactive for too long.

        Args:
            timeout_seconds: Timeout threshold in seconds

        Returns:
            Number of streams cleaned up
        """
        current_time = time.time()
        inactive_streams = []

        # Create a snapshot of stream items to avoid race conditions
        stream_items = list(self.active_streams.items())

        for stream_id, stream_info in stream_items:
            if (
                current_time - stream_info["last_activity"]
                > timeout_seconds
            ):
                inactive_streams.append(stream_id)

        cleaned_count = 0
        for stream_id in inactive_streams:
            try:
                await self.end_stream(stream_id)
                cleaned_count += 1
                logger.warning(
                    "Cleaned up inactive stream",
                    stream_id=stream_id,
                    inactive_duration=timeout_seconds,
                )
            except Exception as e:
                logger.error(
                    "Failed to clean up inactive stream",
                    stream_id=stream_id,
                    error=str(e),
                )

        return cleaned_count

    async def stream_event(
        self, stream_id: str, event: StreamingEvent
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream a single event.

        Args:
            stream_id: Stream identifier
            event: Event to stream

        Yields:
            Streaming chat chunks for the event
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        # Convert StreamingEvent to StreamingChatChunk
        yield StreamingChatChunk(
            type=event.event_type.value,
            content=event.content,
            correlation_id=correlation_id,
            metadata=event.metadata or {},
        )

    async def stream_token(
        self, stream_id: str, content: str
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream a token event.

        Args:
            stream_id: Stream identifier
            content: Token content

        Yields:
            Streaming chat chunks for the token
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["token_count"] += 1
        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        yield StreamingChatChunk(
            type="token",
            content=content,
            correlation_id=correlation_id,
            metadata={
                "stream_id": stream_id,
                "token_count": stream_info["token_count"],
                "timestamp": time.time(),
            },
        )

    async def stream_tool_call_start(
        self, stream_id: str, tool_name: str, tool_args: dict[str, Any]
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream tool call start event.

        Args:
            stream_id: Stream identifier
            tool_name: Name of the tool being called
            tool_args: Arguments for the tool call

        Yields:
            Streaming chat chunks for tool call start
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        yield StreamingChatChunk(
            type="tool_call_start",
            content=tool_name,
            correlation_id=correlation_id,
            metadata={
                "tool_name": tool_name,
                "tool_args": tool_args,
                "stream_id": stream_id,
                "timestamp": time.time(),
            },
        )

    async def stream_tool_call_end(
        self, stream_id: str, tool_name: str, tool_result: dict[str, Any]
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream tool call end event.

        Args:
            stream_id: Stream identifier
            tool_name: Name of the tool that was called
            tool_result: Result from the tool call

        Yields:
            Streaming chat chunks for tool call end
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        yield StreamingChatChunk(
            type="tool_call_end",
            content=str(tool_result),
            correlation_id=correlation_id,
            metadata={
                "tool_name": tool_name,
                "tool_result": tool_result,
                "stream_id": stream_id,
                "timestamp": time.time(),
            },
        )

    async def stream_thinking(
        self, stream_id: str, thought: str
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream thinking event.

        Args:
            stream_id: Stream identifier
            thought: Thought content

        Yields:
            Streaming chat chunks for thinking
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        yield StreamingChatChunk(
            type="thinking",
            content=thought,
            correlation_id=correlation_id,
            metadata={
                "stream_id": stream_id,
                "timestamp": time.time(),
            },
        )

    async def stream_source_found(
        self, stream_id: str, source_title: str, source_url: str = "", metadata: dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream source found event.

        Args:
            stream_id: Stream identifier
            source_title: Title of the source
            source_url: URL of the source
            metadata: Additional metadata

        Yields:
            Streaming chat chunks for source found
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        event_metadata = {
            "source_title": source_title,
            "source_url": source_url,
            "stream_id": stream_id,
            "timestamp": time.time(),
        }
        if metadata:
            event_metadata.update(metadata)

        yield StreamingChatChunk(
            type="source_found",
            content=source_title,
            correlation_id=correlation_id,
            metadata=event_metadata,
        )

    async def stream_error(
        self, stream_id: str, error_message: str, error_type: str = "general"
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream error event.

        Args:
            stream_id: Stream identifier
            error_message: Error message
            error_type: Type of error

        Yields:
            Streaming chat chunks for error
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        # Update error count in metrics
        if stream_id in self.stream_metrics:
            self.stream_metrics[stream_id]["error_count"] += 1

        yield StreamingChatChunk(
            type="error",
            content=error_message,
            correlation_id=correlation_id,
            metadata={
                "error_type": error_type,
                "stream_id": stream_id,
                "timestamp": time.time(),
            },
        )

    async def stream_complete(
        self, stream_id: str, usage: dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream completion event.

        Args:
            stream_id: Stream identifier
            usage: Usage information

        Yields:
            Streaming chat chunks for completion
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        yield StreamingChatChunk(
            type="complete",
            content="",
            correlation_id=correlation_id,
            metadata={
                "usage": usage or {},
                "stream_id": stream_id,
                "timestamp": time.time(),
            },
        )

    async def stream_metadata(
        self, stream_id: str, metadata: dict[str, Any]
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream metadata event.

        Args:
            stream_id: Stream identifier
            metadata: Metadata to stream

        Yields:
            Streaming chat chunks for metadata
        """
        if stream_id not in self.active_streams:
            raise StreamingError(f"Stream {stream_id} not found")

        stream_info = self.active_streams[stream_id]
        correlation_id = stream_info["correlation_id"]

        stream_info["event_count"] += 1
        stream_info["last_activity"] = time.time()

        yield StreamingChatChunk(
            type="metadata",
            content="",
            correlation_id=correlation_id,
            metadata=metadata,
        )

    def get_stream_metrics(self, stream_id: str) -> dict[str, Any] | None:
        """Get metrics for a specific stream.

        Args:
            stream_id: Stream identifier

        Returns:
            Stream metrics or None if not found
        """
        if stream_id not in self.active_streams:
            return None

        stream_info = self.active_streams[stream_id]
        metrics = self.stream_metrics.get(stream_id, {})

        current_time = time.time()
        duration = current_time - stream_info["start_time"]

        return {
            "stream_id": stream_id,
            "workflow_type": stream_info["workflow_type"],
            "correlation_id": stream_info["correlation_id"],
            "status": "active",
            "duration_seconds": duration,
            "token_count": stream_info["token_count"],
            "event_count": stream_info["event_count"],
            "tokens_per_second": (
                stream_info["token_count"] / duration if duration > 0 else 0
            ),
            "events_per_second": (
                stream_info["event_count"] / duration if duration > 0 else 0
            ),
            "last_activity": stream_info["last_activity"],
            "error_count": metrics.get("error_count", 0),
        }

    def list_active_streams(self) -> list[str]:
        """List all active stream IDs.

        Returns:
            List of active stream IDs
        """
        return list(self.active_streams.keys())

    def is_stream_active(self, stream_id: str) -> bool:
        """Check if a stream is active.

        Args:
            stream_id: Stream identifier

        Returns:
            True if stream is active, False otherwise
        """
        return stream_id in self.active_streams

    def get_global_streaming_stats(self) -> dict[str, Any]:
        """Get global streaming statistics.

        Returns:
            Global streaming stats
        """
        active_count = len(self.active_streams)
        total_tokens = sum(
            info["token_count"] for info in self.active_streams.values()
        )
        total_events = sum(
            info["event_count"] for info in self.active_streams.values()
        )

        if active_count > 0:
            avg_tokens_per_stream = total_tokens / active_count
            avg_events_per_stream = total_events / active_count
        else:
            avg_tokens_per_stream = 0
            avg_events_per_stream = 0

        return {
            "active_streams": active_count,
            "total_tokens_streaming": total_tokens,
            "total_events_streaming": total_events,
            "avg_tokens_per_stream": avg_tokens_per_stream,
            "avg_events_per_stream": avg_events_per_stream,
            "workflow_types": list(
                {
                    info["workflow_type"]
                    for info in self.active_streams.values()
                }
            ),
        }


# Global streaming service instance
streaming_service = StreamingService()
