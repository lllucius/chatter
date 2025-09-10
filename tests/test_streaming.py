"""Tests for streaming service."""

import asyncio
import time
from unittest.mock import patch

import pytest

from chatter.services.streaming import (
    StreamingError,
    StreamingEvent,
    StreamingEventType,
    StreamingService,
)


class TestStreamingEventType:
    """Test StreamingEventType enum."""

    def test_streaming_event_types(self):
        """Test all streaming event types are defined."""
        assert StreamingEventType.START == "start"
        assert StreamingEventType.TOKEN == "token"
        assert StreamingEventType.TOOL_CALL_START == "tool_call_start"
        assert StreamingEventType.TOOL_CALL_END == "tool_call_end"
        assert StreamingEventType.SOURCE_FOUND == "source_found"
        assert StreamingEventType.THINKING == "thinking"
        assert StreamingEventType.ERROR == "error"
        assert StreamingEventType.COMPLETE == "complete"
        assert StreamingEventType.METADATA == "metadata"

    def test_streaming_event_type_string_values(self):
        """Test that event types are proper strings."""
        for event_type in StreamingEventType:
            assert isinstance(event_type.value, str)
            assert len(event_type.value) > 0


class TestStreamingEvent:
    """Test StreamingEvent dataclass."""

    def test_streaming_event_data_creation(self):
        """Test creating StreamingEvent."""
        event_data = StreamingEvent(
            type=StreamingEventType.TOKEN,
            content="Hello",
            metadata={"token_id": 123},
            timestamp=1234567890.0,
        )

        assert event_data.type == StreamingEventType.TOKEN
        assert event_data.content == "Hello"
        assert event_data.metadata == {"token_id": 123}
        assert event_data.timestamp == 1234567890.0

    def test_streaming_event_data_minimal(self):
        """Test creating StreamingEvent with minimal fields."""
        event_data = StreamingEvent(event_type=StreamingEventType.START)

        assert event_data.event_type == StreamingEventType.START
        assert event_data.content is None
        assert event_data.metadata is None
        assert event_data.timestamp is not None

    def test_streaming_event_data_auto_timestamp(self):
        """Test that timestamp is automatically set if not provided."""
        before = time.time()
        event_data = StreamingEvent(
            event_type=StreamingEventType.COMPLETE
        )
        after = time.time()

        assert before <= event_data.timestamp <= after

    def test_streaming_event_data_with_metadata(self):
        """Test StreamingEvent with complex metadata."""
        metadata = {
            "tool_name": "calculator",
            "input": {"a": 1, "b": 2},
            "result": {"sum": 3},
            "execution_time": 0.5,
        }

        event_data = StreamingEvent(
            event_type=StreamingEventType.TOOL_CALL_END,
            content="Tool execution completed",
            metadata=metadata,
        )

        assert event_data.metadata == metadata
        assert event_data.metadata["tool_name"] == "calculator"


class TestStreamingError:
    """Test StreamingError exception."""

    def test_streaming_error_basic(self):
        """Test basic StreamingError creation."""
        error = StreamingError("Test streaming error")

        assert str(error) == "Test streaming error"
        assert error.event_type is None
        assert isinstance(error, Exception)

    def test_streaming_error_with_event_type(self):
        """Test StreamingError with event type."""
        error = StreamingError(
            "Token processing failed",
            event_type=StreamingEventType.TOKEN,
        )

        assert str(error) == "Token processing failed"
        assert error.event_type == StreamingEventType.TOKEN

    def test_streaming_error_inheritance(self):
        """Test StreamingError inheritance from Exception."""
        error = StreamingError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, StreamingError)


class TestStreamingService:
    """Test StreamingService functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.service = StreamingService()

    def test_streaming_service_initialization(self):
        """Test StreamingService initialization."""
        assert isinstance(self.service.active_streams, dict)
        assert isinstance(self.service.stream_metrics, dict)
        assert len(self.service.active_streams) == 0
        assert len(self.service.stream_metrics) == 0

    @pytest.mark.asyncio
    async def test_create_stream(self):
        """Test creating a new stream."""
        stream_id = "test_stream_123"
        workflow_type = "chat_completion"
        correlation_id = "corr_456"

        await self.service.create_stream(
            stream_id=stream_id,
            workflow_type=workflow_type,
            correlation_id=correlation_id,
        )

        assert stream_id in self.service.active_streams
        assert stream_id in self.service.stream_metrics

        stream_info = self.service.active_streams[stream_id]
        assert stream_info["workflow_type"] == workflow_type
        assert stream_info["correlation_id"] == correlation_id
        assert stream_info["token_count"] == 0
        assert stream_info["event_count"] == 0
        assert "start_time" in stream_info
        assert "last_activity" in stream_info

    @pytest.mark.asyncio
    @patch("chatter.services.streaming.get_correlation_id")
    async def test_create_stream_auto_correlation_id(
        self, mock_get_correlation_id
    ):
        """Test creating stream with auto-generated correlation ID."""
        mock_get_correlation_id.return_value = "auto_corr_789"

        stream_id = "test_stream_auto"
        workflow_type = "document_processing"

        await self.service.create_stream(
            stream_id=stream_id, workflow_type=workflow_type
        )

        stream_info = self.service.active_streams[stream_id]
        assert stream_info["correlation_id"] == "auto_corr_789"
        mock_get_correlation_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_stream_metrics_initialization(self):
        """Test that stream metrics are properly initialized."""
        stream_id = "metrics_test_stream"

        await self.service.create_stream(
            stream_id=stream_id, workflow_type="test_workflow"
        )

        metrics = self.service.stream_metrics[stream_id]
        assert metrics["tokens_per_second"] == 0.0
        assert metrics["events_per_second"] == 0.0
        assert metrics["total_duration"] == 0.0
        assert metrics["error_count"] == 0

    @pytest.mark.asyncio
    @patch("chatter.services.streaming.record_workflow_metrics")
    async def test_end_stream(self, mock_record_metrics):
        """Test ending a stream and getting metrics."""
        stream_id = "end_test_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="test_workflow"
        )

        # Simulate some activity
        self.service.active_streams[stream_id]["token_count"] = 100
        self.service.active_streams[stream_id]["event_count"] = 10

        # Wait a bit to have measurable duration
        await asyncio.sleep(0.01)

        # End stream
        metrics = await self.service.end_stream(stream_id)

        assert metrics["total_duration"] > 0
        assert metrics["tokens_per_second"] > 0
        assert metrics["events_per_second"] > 0
        assert stream_id not in self.service.active_streams
        assert stream_id not in self.stream_metrics

        # Verify workflow metrics were recorded
        mock_record_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_end_nonexistent_stream(self):
        """Test ending a stream that doesn't exist."""
        metrics = await self.service.end_stream("nonexistent_stream")

        assert metrics == {}

    @pytest.mark.asyncio
    async def test_stream_event_basic(self):
        """Test streaming a basic event."""
        stream_id = "event_test_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="test_workflow"
        )

        # Create async generator for streaming
        async def stream_events():
            event_data = StreamingEvent(
                event_type=StreamingEventType.TOKEN,
                content="Hello",
                metadata={"token_id": 1},
            )

            async for chunk in self.service.stream_event(
                stream_id, event_data
            ):
                yield chunk

        # Collect streamed events
        events = []
        async for event in stream_events():
            events.append(event)

        assert len(events) > 0

        # Verify stream metrics were updated
        stream_info = self.service.active_streams[stream_id]
        assert stream_info["event_count"] > 0

    @pytest.mark.asyncio
    async def test_stream_token(self):
        """Test streaming a token event."""
        stream_id = "token_test_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="chat_completion"
        )

        token_content = "world"

        # Stream token
        events = []
        async for chunk in self.service.stream_token(
            stream_id, token_content
        ):
            events.append(chunk)

        assert len(events) > 0

        # Find token event
        token_events = [
            e
            for e in events
            if hasattr(e, "event_type")
            and e.event_type == StreamingEventType.TOKEN
        ]
        assert len(token_events) > 0

        # Verify token count was updated
        stream_info = self.service.active_streams[stream_id]
        assert stream_info["token_count"] > 0

    @pytest.mark.asyncio
    async def test_stream_tool_call_lifecycle(self):
        """Test complete tool call streaming lifecycle."""
        stream_id = "tool_call_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="tool_execution"
        )

        tool_name = "calculator"
        tool_input = {"operation": "add", "a": 5, "b": 3}
        tool_result = {"result": 8}

        # Stream tool call start
        start_events = []
        async for chunk in self.service.stream_tool_call_start(
            stream_id, tool_name, tool_input
        ):
            start_events.append(chunk)

        assert len(start_events) > 0

        # Stream tool call end
        end_events = []
        async for chunk in self.service.stream_tool_call_end(
            stream_id, tool_name, tool_result
        ):
            end_events.append(chunk)

        assert len(end_events) > 0

        # Verify events were recorded
        stream_info = self.service.active_streams[stream_id]
        assert stream_info["event_count"] >= 2

    @pytest.mark.asyncio
    async def test_stream_thinking(self):
        """Test streaming thinking event."""
        stream_id = "thinking_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="reasoning"
        )

        thinking_content = "Let me analyze this problem..."

        # Stream thinking
        events = []
        async for chunk in self.service.stream_thinking(
            stream_id, thinking_content
        ):
            events.append(chunk)

        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_stream_source_found(self):
        """Test streaming source found event."""
        stream_id = "source_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="document_search"
        )

        source_info = {
            "title": "Test Document",
            "url": "https://example.com/doc",
            "relevance": 0.95,
        }

        # Stream source found
        events = []
        async for chunk in self.service.stream_source_found(
            stream_id, source_info
        ):
            events.append(chunk)

        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_stream_error(self):
        """Test streaming error event."""
        stream_id = "error_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="test_workflow"
        )

        error_message = "Test error occurred"
        error_details = {"error_code": "TEST_001", "retry": False}

        # Stream error
        events = []
        async for chunk in self.service.stream_error(
            stream_id, error_message, error_details
        ):
            events.append(chunk)

        assert len(events) > 0

        # Verify error count was updated
        metrics = self.service.stream_metrics[stream_id]
        assert metrics["error_count"] > 0

    @pytest.mark.asyncio
    async def test_stream_complete(self):
        """Test streaming completion event."""
        stream_id = "complete_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="test_workflow"
        )

        final_result = {"status": "success", "total_tokens": 150}

        # Stream completion
        events = []
        async for chunk in self.service.stream_complete(
            stream_id, final_result
        ):
            events.append(chunk)

        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_stream_metadata(self):
        """Test streaming metadata event."""
        stream_id = "metadata_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="test_workflow"
        )

        metadata = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 500,
        }

        # Stream metadata
        events = []
        async for chunk in self.service.stream_metadata(
            stream_id, metadata
        ):
            events.append(chunk)

        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_get_stream_metrics(self):
        """Test getting stream metrics."""
        stream_id = "metrics_stream"

        # Create stream
        await self.service.create_stream(
            stream_id=stream_id, workflow_type="test_workflow"
        )

        # Simulate some activity
        self.service.active_streams[stream_id]["token_count"] = 50
        self.service.active_streams[stream_id]["event_count"] = 5

        # Get metrics
        metrics = self.service.get_stream_metrics(stream_id)

        assert metrics is not None
        assert "tokens_per_second" in metrics
        assert "events_per_second" in metrics
        assert "error_count" in metrics

    @pytest.mark.asyncio
    async def test_get_nonexistent_stream_metrics(self):
        """Test getting metrics for nonexistent stream."""
        metrics = self.service.get_stream_metrics("nonexistent")

        assert metrics is None

    @pytest.mark.asyncio
    async def test_list_active_streams(self):
        """Test listing active streams."""
        # Initially no streams
        streams = self.service.list_active_streams()
        assert len(streams) == 0

        # Create multiple streams
        await self.service.create_stream("stream1", "workflow1")
        await self.service.create_stream("stream2", "workflow2")

        streams = self.service.list_active_streams()
        assert len(streams) == 2
        assert "stream1" in streams
        assert "stream2" in streams

    @pytest.mark.asyncio
    async def test_is_stream_active(self):
        """Test checking if stream is active."""
        stream_id = "active_check_stream"

        # Stream doesn't exist
        assert self.service.is_stream_active(stream_id) is False

        # Create stream
        await self.service.create_stream(stream_id, "test_workflow")

        # Stream exists and is active
        assert self.service.is_stream_active(stream_id) is True

        # End stream
        await self.service.end_stream(stream_id)

        # Stream no longer active
        assert self.service.is_stream_active(stream_id) is False

    @pytest.mark.asyncio
    async def test_stream_activity_tracking(self):
        """Test that stream activity is properly tracked."""
        stream_id = "activity_stream"

        # Create stream
        await self.service.create_stream(stream_id, "test_workflow")

        initial_activity = self.service.active_streams[stream_id][
            "last_activity"
        ]

        # Wait a bit
        await asyncio.sleep(0.01)

        # Stream a token (should update last_activity)
        async for _ in self.service.stream_token(stream_id, "test"):
            pass

        updated_activity = self.service.active_streams[stream_id][
            "last_activity"
        ]

        assert updated_activity > initial_activity

    @pytest.mark.asyncio
    async def test_stream_error_handling_invalid_stream(self):
        """Test error handling when streaming to invalid stream."""
        with pytest.raises(StreamingError):
            async for _ in self.service.stream_token(
                "invalid_stream", "test"
            ):
                pass

    @pytest.mark.asyncio
    async def test_concurrent_streams(self):
        """Test handling multiple concurrent streams."""
        stream_ids = ["concurrent1", "concurrent2", "concurrent3"]

        # Create multiple streams concurrently
        create_tasks = [
            self.service.create_stream(stream_id, f"workflow_{i}")
            for i, stream_id in enumerate(stream_ids)
        ]
        await asyncio.gather(*create_tasks)

        # Verify all streams are active
        for stream_id in stream_ids:
            assert self.service.is_stream_active(stream_id)

        # Stream to all concurrently
        stream_tasks = [
            self.service.stream_token(stream_id, f"token_{i}")
            for i, stream_id in enumerate(stream_ids)
        ]

        # Execute streaming tasks
        for task in stream_tasks:
            events = []
            async for event in task:
                events.append(event)
            assert len(events) > 0

    @pytest.mark.asyncio
    async def test_stream_cleanup_on_error(self):
        """Test stream cleanup when errors occur."""
        stream_id = "cleanup_stream"

        # Create stream
        await self.service.create_stream(stream_id, "test_workflow")

        # Simulate an error during streaming
        with patch.object(
            self.service,
            "stream_event",
            side_effect=StreamingError("Test error"),
        ):
            with pytest.raises(StreamingError):
                async for _ in self.service.stream_token(
                    stream_id, "test"
                ):
                    pass

        # Stream should still exist (error doesn't auto-cleanup)
        assert self.service.is_stream_active(stream_id)


@pytest.mark.integration
class TestStreamingServiceIntegration:
    """Integration tests for streaming service."""

    def setup_method(self):
        """Set up test environment."""
        self.service = StreamingService()

    @pytest.mark.asyncio
    async def test_complete_streaming_workflow(self):
        """Test complete streaming workflow from start to finish."""
        stream_id = "complete_workflow_stream"
        workflow_type = "chat_completion"

        # 1. Create stream
        await self.service.create_stream(stream_id, workflow_type)
        assert self.service.is_stream_active(stream_id)

        # 2. Stream various events
        events_collected = []

        # Start event
        async for event in self.service.stream_event(
            stream_id,
            StreamingEvent(
                event_type=StreamingEventType.START,
                content="Starting chat completion",
            ),
        ):
            events_collected.append(event)

        # Thinking event
        async for event in self.service.stream_thinking(
            stream_id, "Analyzing the question..."
        ):
            events_collected.append(event)

        # Multiple tokens
        for token in ["Hello", " ", "world", "!"]:
            async for event in self.service.stream_token(
                stream_id, token
            ):
                events_collected.append(event)

        # Tool call
        async for event in self.service.stream_tool_call_start(
            stream_id, "calculator", {"a": 1, "b": 2}
        ):
            events_collected.append(event)

        async for event in self.service.stream_tool_call_end(
            stream_id, "calculator", {"result": 3}
        ):
            events_collected.append(event)

        # Complete event
        async for event in self.service.stream_complete(
            stream_id, {"total_tokens": 4}
        ):
            events_collected.append(event)

        # 3. End stream and get metrics
        final_metrics = await self.service.end_stream(stream_id)

        # Verify results
        assert len(events_collected) > 0
        assert final_metrics["total_duration"] > 0
        assert final_metrics["tokens_per_second"] >= 0
        assert final_metrics["events_per_second"] > 0
        assert not self.service.is_stream_active(stream_id)

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test streaming workflow with error recovery."""
        stream_id = "error_recovery_stream"

        # Create stream
        await self.service.create_stream(
            stream_id, "error_recovery_test"
        )

        # Stream some successful events
        async for _ in self.service.stream_token(stream_id, "Success"):
            pass

        # Stream an error
        async for _ in self.service.stream_error(
            stream_id, "Something went wrong", {"recoverable": True}
        ):
            pass

        # Continue streaming after error
        async for _ in self.service.stream_token(
            stream_id, "Recovered"
        ):
            pass

        # Complete successfully
        async for _ in self.service.stream_complete(
            stream_id, {"recovered": True}
        ):
            pass

        # End stream
        metrics = await self.service.end_stream(stream_id)

        # Should have recorded the error but still completed
        assert metrics["error_count"] > 0
        assert metrics["total_duration"] > 0

    @pytest.mark.asyncio
    async def test_performance_with_high_volume_streaming(self):
        """Test streaming performance with high volume of events."""
        stream_id = "high_volume_stream"

        # Create stream
        await self.service.create_stream(stream_id, "performance_test")

        # Stream many tokens quickly
        start_time = time.time()

        for i in range(100):  # Stream 100 tokens
            async for _ in self.service.stream_token(
                stream_id, f"token_{i}"
            ):
                pass

        end_time = time.time()
        duration = end_time - start_time

        # End stream
        metrics = await self.service.end_stream(stream_id)

        # Verify performance
        assert metrics["tokens_per_second"] > 0
        assert duration < 1.0  # Should complete in less than 1 second
        assert metrics["total_duration"] > 0

    @pytest.mark.asyncio
    async def test_stream_isolation(self):
        """Test that streams are properly isolated from each other."""
        stream1_id = "isolation_stream_1"
        stream2_id = "isolation_stream_2"

        # Create two streams
        await self.service.create_stream(stream1_id, "workflow1")
        await self.service.create_stream(stream2_id, "workflow2")

        # Stream different content to each
        async for _ in self.service.stream_token(
            stream1_id, "stream1_content"
        ):
            pass
        async for _ in self.service.stream_token(
            stream2_id, "stream2_content"
        ):
            pass

        # Each stream should have its own metrics
        metrics1 = self.service.get_stream_metrics(stream1_id)
        metrics2 = self.service.get_stream_metrics(stream2_id)

        assert metrics1 is not metrics2

        # Each stream should have recorded its own events
        stream1_info = self.service.active_streams[stream1_id]
        stream2_info = self.service.active_streams[stream2_id]

        assert (
            stream1_info["correlation_id"]
            != stream2_info["correlation_id"]
        )
