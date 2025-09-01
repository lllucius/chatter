"""Tests for streaming service functionality."""

import asyncio
import json
from typing import AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from chatter.services.streaming import (
    StreamingService,
    StreamEvent,
    StreamEventType,
    StreamingError,
)


class TestStreamEvent:
    """Test StreamEvent data class."""

    def test_stream_event_creation(self):
        """Test creating a stream event."""
        event = StreamEvent(
            event_type=StreamEventType.MESSAGE,
            data={"content": "Hello world"},
            id="event-123"
        )
        
        assert event.event_type == StreamEventType.MESSAGE
        assert event.data == {"content": "Hello world"}
        assert event.id == "event-123"
        assert event.retry is None

    def test_stream_event_with_retry(self):
        """Test stream event with retry information."""
        event = StreamEvent(
            event_type=StreamEventType.ERROR,
            data={"error": "Connection lost"},
            retry=5000
        )
        
        assert event.retry == 5000

    def test_stream_event_to_sse_format(self):
        """Test converting stream event to SSE format."""
        event = StreamEvent(
            event_type=StreamEventType.MESSAGE,
            data={"content": "Hello"},
            id="msg-1"
        )
        
        sse_output = event.to_sse()
        
        assert "event: message" in sse_output
        assert "data: " in sse_output
        assert "id: msg-1" in sse_output
        assert "Hello" in sse_output

    def test_stream_event_json_serialization(self):
        """Test stream event JSON serialization."""
        event = StreamEvent(
            event_type=StreamEventType.TOKEN,
            data={"token": "hello", "index": 0}
        )
        
        sse_output = event.to_sse()
        
        # Should contain properly formatted JSON
        assert "data: " in sse_output
        data_line = next(line for line in sse_output.split('\n') if line.startswith('data: '))
        json_data = data_line[6:]  # Remove "data: " prefix
        parsed = json.loads(json_data)
        
        assert parsed["token"] == "hello"
        assert parsed["index"] == 0


class TestStreamEventType:
    """Test StreamEventType enum."""

    def test_stream_event_types(self):
        """Test stream event type values."""
        assert StreamEventType.MESSAGE == "message"
        assert StreamEventType.TOKEN == "token"
        assert StreamEventType.ERROR == "error"
        assert StreamEventType.COMPLETE == "complete"
        assert StreamEventType.START == "start"

    def test_stream_event_type_usage(self):
        """Test using event types in events."""
        event_types = [
            StreamEventType.MESSAGE,
            StreamEventType.TOKEN,
            StreamEventType.ERROR,
            StreamEventType.COMPLETE,
            StreamEventType.START
        ]
        
        for event_type in event_types:
            event = StreamEvent(
                event_type=event_type,
                data={"test": "data"}
            )
            assert event.event_type == event_type


class TestStreamingError:
    """Test StreamingError exception."""

    def test_streaming_error_creation(self):
        """Test creating streaming error."""
        error = StreamingError("Stream failed")
        
        assert str(error) == "Stream failed"
        assert isinstance(error, Exception)

    def test_streaming_error_with_details(self):
        """Test streaming error with additional details."""
        error = StreamingError("Connection failed", error_code="CONN_LOST")
        
        assert "Connection failed" in str(error)


class TestStreamingService:
    """Test StreamingService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.service = StreamingService(session=self.mock_session)

    @pytest.mark.asyncio
    async def test_create_stream_generator(self):
        """Test creating a basic stream generator."""
        async def mock_generator():
            yield StreamEvent(StreamEventType.START, {"message": "Starting"})
            yield StreamEvent(StreamEventType.TOKEN, {"token": "Hello"})
            yield StreamEvent(StreamEventType.TOKEN, {"token": " world"})
            yield StreamEvent(StreamEventType.COMPLETE, {"message": "Done"})
        
        stream = self.service.create_stream(mock_generator())
        
        events = []
        async for event in stream:
            events.append(event)
        
        assert len(events) == 4
        assert events[0].event_type == StreamEventType.START
        assert events[1].data["token"] == "Hello"
        assert events[2].data["token"] == " world"
        assert events[3].event_type == StreamEventType.COMPLETE

    @pytest.mark.asyncio
    async def test_stream_llm_response(self):
        """Test streaming LLM response."""
        conversation_id = "conv-123"
        message_content = "Tell me a joke"
        
        # Mock LLM service response
        mock_llm_response = [
            {"token": "Why", "index": 0},
            {"token": " did", "index": 1},
            {"token": " the", "index": 2},
            {"token": " chicken", "index": 3},
            {"token": " cross", "index": 4},
            {"token": " the", "index": 5},
            {"token": " road?", "index": 6}
        ]
        
        async def mock_llm_stream():
            for token_data in mock_llm_response:
                yield token_data
        
        with patch('chatter.services.llm.LLMService') as mock_llm:
            mock_llm_instance = Mock()
            mock_llm_instance.stream_generate = AsyncMock(return_value=mock_llm_stream())
            mock_llm.return_value = mock_llm_instance
            
            stream = await self.service.stream_llm_response(
                conversation_id=conversation_id,
                message_content=message_content,
                model="gpt-4"
            )
            
            events = []
            async for event in stream:
                events.append(event)
            
            # Should have start event, token events, and complete event
            assert len(events) >= len(mock_llm_response)
            
            # Check start event
            start_events = [e for e in events if e.event_type == StreamEventType.START]
            assert len(start_events) == 1
            
            # Check token events
            token_events = [e for e in events if e.event_type == StreamEventType.TOKEN]
            assert len(token_events) == len(mock_llm_response)
            
            # Check complete event
            complete_events = [e for e in events if e.event_type == StreamEventType.COMPLETE]
            assert len(complete_events) == 1

    @pytest.mark.asyncio
    async def test_stream_error_handling(self):
        """Test stream error handling."""
        async def failing_generator():
            yield StreamEvent(StreamEventType.START, {"message": "Starting"})
            raise Exception("Stream failed")
        
        stream = self.service.create_stream(failing_generator())
        
        events = []
        try:
            async for event in stream:
                events.append(event)
        except StreamingError:
            pass  # Expected
        
        # Should have received start event before error
        assert len(events) >= 1
        assert events[0].event_type == StreamEventType.START

    @pytest.mark.asyncio
    async def test_stream_with_heartbeat(self):
        """Test stream with heartbeat events."""
        async def slow_generator():
            yield StreamEvent(StreamEventType.START, {"message": "Starting"})
            await asyncio.sleep(0.1)  # Simulate slow processing
            yield StreamEvent(StreamEventType.TOKEN, {"token": "Hello"})
            await asyncio.sleep(0.1)
            yield StreamEvent(StreamEventType.COMPLETE, {"message": "Done"})
        
        stream = self.service.create_stream_with_heartbeat(
            slow_generator(),
            heartbeat_interval=0.05
        )
        
        events = []
        async for event in stream:
            events.append(event)
        
        # Should have heartbeat events in addition to regular events
        heartbeat_events = [e for e in events if e.event_type == "heartbeat"]
        regular_events = [e for e in events if e.event_type != "heartbeat"]
        
        assert len(regular_events) == 3  # start, token, complete
        assert len(heartbeat_events) > 0  # Should have some heartbeat events

    @pytest.mark.asyncio
    async def test_stream_with_buffer(self):
        """Test stream with buffering."""
        async def token_generator():
            tokens = ["Hello", " ", "world", "!", " ", "How", " ", "are", " ", "you", "?"]
            for i, token in enumerate(tokens):
                yield StreamEvent(StreamEventType.TOKEN, {"token": token, "index": i})
        
        # Buffer every 3 tokens
        stream = self.service.create_buffered_stream(
            token_generator(),
            buffer_size=3
        )
        
        events = []
        async for event in stream:
            events.append(event)
        
        # Should have fewer events than original tokens due to buffering
        token_events = [e for e in events if e.event_type == StreamEventType.TOKEN]
        
        # Each buffered event should contain multiple tokens
        for event in token_events:
            if "buffered_tokens" in event.data:
                assert len(event.data["buffered_tokens"]) <= 3

    @pytest.mark.asyncio
    async def test_stream_conversation_update(self):
        """Test streaming with conversation updates."""
        conversation_id = "conv-123"
        user_id = "user-456"
        
        async def message_generator():
            yield StreamEvent(StreamEventType.START, {
                "conversation_id": conversation_id,
                "message": "Processing your request..."
            })
            
            # Simulate tokens
            tokens = ["The", " answer", " is", " 42", "."]
            for i, token in enumerate(tokens):
                yield StreamEvent(StreamEventType.TOKEN, {
                    "token": token,
                    "index": i
                })
            
            yield StreamEvent(StreamEventType.COMPLETE, {
                "conversation_id": conversation_id,
                "final_message": "The answer is 42.",
                "tokens_used": 5
            })
        
        # Mock conversation service
        with patch('chatter.services.conversation.ConversationService') as mock_conv:
            mock_conv_instance = Mock()
            mock_conv_instance.update_conversation = AsyncMock()
            mock_conv.return_value = mock_conv_instance
            
            stream = self.service.stream_with_conversation_update(
                message_generator(),
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            events = []
            async for event in stream:
                events.append(event)
            
            # Should have received all events
            assert len(events) == 7  # start + 5 tokens + complete
            
            # Conversation should be updated on completion
            mock_conv_instance.update_conversation.assert_called()

    @pytest.mark.asyncio
    async def test_stream_rate_limiting(self):
        """Test stream rate limiting."""
        async def fast_generator():
            for i in range(10):
                yield StreamEvent(StreamEventType.TOKEN, {"token": f"token_{i}"})
        
        # Limit to 2 events per second
        stream = self.service.create_rate_limited_stream(
            fast_generator(),
            events_per_second=5
        )
        
        start_time = asyncio.get_event_loop().time()
        events = []
        
        async for event in stream:
            events.append(event)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Should take at least 1 second for 10 events at 5 events/second
        assert duration >= 1.0
        assert len(events) == 10

    @pytest.mark.asyncio
    async def test_stream_client_disconnect_handling(self):
        """Test handling client disconnects."""
        disconnect_event = asyncio.Event()
        
        async def long_generator():
            for i in range(100):
                if disconnect_event.is_set():
                    break
                yield StreamEvent(StreamEventType.TOKEN, {"token": f"token_{i}"})
                await asyncio.sleep(0.01)
        
        stream = self.service.create_stream_with_disconnect_handling(
            long_generator(),
            disconnect_event=disconnect_event
        )
        
        events = []
        async for event in stream:
            events.append(event)
            if len(events) == 5:
                disconnect_event.set()
                break
        
        # Should stop early due to disconnect
        assert len(events) == 5

    @pytest.mark.asyncio
    async def test_stream_metrics_collection(self):
        """Test stream metrics collection."""
        async def metric_generator():
            yield StreamEvent(StreamEventType.START, {"message": "Starting"})
            for i in range(5):
                yield StreamEvent(StreamEventType.TOKEN, {"token": f"token_{i}"})
            yield StreamEvent(StreamEventType.COMPLETE, {"message": "Done"})
        
        with patch('chatter.utils.monitoring.record_stream_metrics') as mock_metrics:
            stream = self.service.create_stream_with_metrics(
                metric_generator(),
                stream_id="stream-123"
            )
            
            events = []
            async for event in stream:
                events.append(event)
            
            # Metrics should be recorded
            mock_metrics.assert_called()
            
            # Should have recorded stream duration, event count, etc.
            call_args = mock_metrics.call_args[1]
            assert "stream_id" in call_args
            assert "event_count" in call_args
            assert "duration_ms" in call_args

    @pytest.mark.asyncio
    async def test_stream_retry_mechanism(self):
        """Test stream retry mechanism."""
        attempt_count = 0
        
        async def unreliable_generator():
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count < 3:
                yield StreamEvent(StreamEventType.START, {"attempt": attempt_count})
                raise Exception(f"Attempt {attempt_count} failed")
            
            # Succeed on third attempt
            yield StreamEvent(StreamEventType.START, {"attempt": attempt_count})
            yield StreamEvent(StreamEventType.TOKEN, {"token": "Success!"})
            yield StreamEvent(StreamEventType.COMPLETE, {"message": "Done"})
        
        stream = self.service.create_stream_with_retry(
            unreliable_generator,
            max_retries=3,
            retry_delay=0.1
        )
        
        events = []
        async for event in stream:
            events.append(event)
        
        # Should eventually succeed
        assert attempt_count == 3
        success_events = [e for e in events if e.event_type == StreamEventType.TOKEN]
        assert len(success_events) == 1
        assert success_events[0].data["token"] == "Success!"

    @pytest.mark.asyncio
    async def test_stream_compression(self):
        """Test stream compression for large payloads."""
        async def large_payload_generator():
            large_content = "A" * 1000  # Large content
            yield StreamEvent(StreamEventType.MESSAGE, {
                "content": large_content,
                "size": len(large_content)
            })
        
        stream = self.service.create_compressed_stream(
            large_payload_generator(),
            compression_threshold=500
        )
        
        events = []
        async for event in stream:
            events.append(event)
        
        # Should have compressed the large payload
        assert len(events) == 1
        event = events[0]
        
        # Should have compression metadata
        if "compressed" in event.data:
            assert event.data["compressed"] is True

    @pytest.mark.asyncio
    async def test_stream_event_filtering(self):
        """Test filtering stream events."""
        async def mixed_event_generator():
            yield StreamEvent(StreamEventType.START, {"message": "Starting"})
            yield StreamEvent(StreamEventType.TOKEN, {"token": "Hello"})
            yield StreamEvent("debug", {"debug_info": "Internal info"})
            yield StreamEvent(StreamEventType.TOKEN, {"token": " world"})
            yield StreamEvent("heartbeat", {"timestamp": "now"})
            yield StreamEvent(StreamEventType.COMPLETE, {"message": "Done"})
        
        # Filter out debug and heartbeat events
        stream = self.service.create_filtered_stream(
            mixed_event_generator(),
            allowed_event_types=[
                StreamEventType.START,
                StreamEventType.TOKEN,
                StreamEventType.COMPLETE
            ]
        )
        
        events = []
        async for event in stream:
            events.append(event)
        
        # Should only have allowed event types
        assert len(events) == 4  # start, 2 tokens, complete
        event_types = [e.event_type for e in events]
        assert "debug" not in event_types
        assert "heartbeat" not in event_types

    @pytest.mark.asyncio
    async def test_stream_concurrent_clients(self):
        """Test streaming to multiple clients concurrently."""
        async def shared_generator():
            for i in range(5):
                yield StreamEvent(StreamEventType.TOKEN, {"token": f"token_{i}"})
        
        # Create multiple client streams
        client_streams = [
            self.service.create_stream(shared_generator())
            for _ in range(3)
        ]
        
        # Collect events from all clients concurrently
        async def collect_events(stream):
            events = []
            async for event in stream:
                events.append(event)
            return events
        
        client_results = await asyncio.gather(*[
            collect_events(stream) for stream in client_streams
        ])
        
        # All clients should receive the same events
        assert len(client_results) == 3
        for events in client_results:
            assert len(events) == 5
            assert all(e.event_type == StreamEventType.TOKEN for e in events)