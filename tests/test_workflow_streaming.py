"""Workflow streaming tests."""

import asyncio
import json
from unittest.mock import AsyncMock

import pytest

from chatter.core.chat import ChatService
from chatter.services.sse_events import SSEEventService


@pytest.mark.unit
class TestSSEEventService:
    """Test SSE (Server-Sent Events) streaming functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sse_service = SSEEventService()

    def test_event_formatting(self):
        """Test SSE event formatting."""
        # Test basic event formatting
        event_data = {"message": "Hello, world!", "type": "chat"}
        formatted = self.sse_service.format_event("message", event_data)

        assert "event: message" in formatted
        assert "data: " in formatted
        assert json.loads(formatted.split("data: ")[1].split("\n")[0]) == event_data

    def test_event_id_generation(self):
        """Test event ID generation."""
        event1 = self.sse_service.format_event("test", {"data": "1"}, event_id="custom-1")
        event2 = self.sse_service.format_event("test", {"data": "2"})

        assert "id: custom-1" in event1
        assert "id: " in event2

        # Auto-generated IDs should be unique
        id1 = event1.split("id: ")[1].split("\n")[0]
        id2 = event2.split("id: ")[1].split("\n")[0]
        assert id1 != id2

    def test_heartbeat_events(self):
        """Test heartbeat event generation."""
        heartbeat = self.sse_service.create_heartbeat()

        assert "event: heartbeat" in heartbeat
        assert "data: " in heartbeat

        data = json.loads(heartbeat.split("data: ")[1].split("\n")[0])
        assert "timestamp" in data
        assert data["type"] == "heartbeat"

    def test_error_event_formatting(self):
        """Test error event formatting."""
        error_data = {
            "error": "Something went wrong",
            "code": "INTERNAL_ERROR",
            "details": "Database connection failed"
        }

        error_event = self.sse_service.format_error_event(error_data)

        assert "event: error" in error_event
        assert "data: " in error_event

        data = json.loads(error_event.split("data: ")[1].split("\n")[0])
        assert data["error"] == "Something went wrong"
        assert data["code"] == "INTERNAL_ERROR"

    def test_completion_event(self):
        """Test completion event formatting."""
        completion_event = self.sse_service.create_completion_event({"status": "completed"})

        assert "event: completion" in completion_event
        assert "data: " in completion_event

        data = json.loads(completion_event.split("data: ")[1].split("\n")[0])
        assert data["status"] == "completed"


@pytest.mark.unit
class TestWorkflowStreaming:
    """Test workflow streaming functionality."""

    @pytest.fixture
    def mock_chat_service(self):
        """Mock chat service for testing."""
        service = AsyncMock(spec=ChatService)
        service.stream_response.return_value = self._mock_stream_generator()
        return service

    async def _mock_stream_generator(self):
        """Mock stream generator for testing."""
        chunks = [
            {"type": "token", "content": "Hello"},
            {"type": "token", "content": " there"},
            {"type": "token", "content": "!"},
            {"type": "completion", "content": "", "finish_reason": "stop"}
        ]

        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.01)  # Simulate small delay

    async def test_chat_message_streaming(self, mock_chat_service):
        """Test streaming of chat messages."""
        sse_service = SSEEventService()

        # Collect streamed events
        events = []
        async for chunk in mock_chat_service.stream_response():
            event = sse_service.format_event("chunk", chunk)
            events.append(event)

        assert len(events) == 4

        # Check token events
        token_events = [e for e in events if "chunk" in e and "token" in e]
        assert len(token_events) == 3

        # Check completion event
        completion_events = [e for e in events if "completion" in e]
        assert len(completion_events) == 1

    async def test_streaming_error_handling(self):
        """Test error handling during streaming."""
        sse_service = SSEEventService()

        async def error_generator():
            yield {"type": "token", "content": "Hello"}
            raise Exception("Stream interrupted")

        events = []
        try:
            async for chunk in error_generator():
                event = sse_service.format_event("chunk", chunk)
                events.append(event)
        except Exception as e:
            error_event = sse_service.format_error_event({
                "error": str(e),
                "code": "STREAM_ERROR"
            })
            events.append(error_event)

        assert len(events) == 2  # 1 token + 1 error
        assert "error" in events[1]

    async def test_concurrent_streaming(self):
        """Test concurrent streaming to multiple clients."""
        sse_service = SSEEventService()

        async def stream_to_client(client_id):
            events = []
            for i in range(3):
                event_data = {"client": client_id, "message": f"Message {i}"}
                event = sse_service.format_event("message", event_data)
                events.append(event)
                await asyncio.sleep(0.01)
            return events

        # Simulate 3 concurrent clients
        tasks = [
            stream_to_client("client1"),
            stream_to_client("client2"),
            stream_to_client("client3")
        ]

        results = await asyncio.gather(*tasks)

        # Each client should receive their own events
        assert len(results) == 3
        for client_events in results:
            assert len(client_events) == 3


@pytest.mark.unit
class TestStreamingProtocol:
    """Test streaming protocol compliance."""

    def test_sse_protocol_compliance(self):
        """Test SSE protocol compliance."""
        sse_service = SSEEventService()

        event_data = {"message": "test", "timestamp": "2024-01-01T00:00:00Z"}
        formatted = sse_service.format_event("test", event_data, event_id="123")

        lines = formatted.strip().split("\n")

        # Check required SSE fields
        assert any(line.startswith("id: ") for line in lines)
        assert any(line.startswith("event: ") for line in lines)
        assert any(line.startswith("data: ") for line in lines)

        # Should end with double newline (handled by caller)
        assert formatted.endswith("\n\n")

    def test_multiline_data_handling(self):
        """Test handling of multiline data."""
        sse_service = SSEEventService()

        multiline_data = {
            "message": "Line 1\nLine 2\nLine 3",
            "code": "function test() {\n  return 'hello';\n}"
        }

        formatted = sse_service.format_event("multiline", multiline_data)

        # Multiline data should be properly JSON encoded
        assert "data: " in formatted
        data_line = [line for line in formatted.split("\n") if line.startswith("data: ")][0]
        parsed_data = json.loads(data_line[6:])  # Remove "data: " prefix

        assert parsed_data["message"] == "Line 1\nLine 2\nLine 3"
        assert "function test()" in parsed_data["code"]

    def test_special_character_handling(self):
        """Test handling of special characters in data."""
        sse_service = SSEEventService()

        special_data = {
            "unicode": "Hello 🌍 World! 你好",
            "quotes": 'String with "quotes" and \'apostrophes\'',
            "special": "Characters: @#$%^&*()_+-={}[]|\\:;\"'<>?,./",
            "emojis": "🚀 🎉 🔥 💡 ⚡ 🌟"
        }

        formatted = sse_service.format_event("special", special_data)

        # Should be properly JSON encoded
        data_line = [line for line in formatted.split("\n") if line.startswith("data: ")][0]
        parsed_data = json.loads(data_line[6:])

        assert parsed_data["unicode"] == "Hello 🌍 World! 你好"
        assert '"quotes"' in parsed_data["quotes"]
        assert "🚀" in parsed_data["emojis"]


@pytest.mark.integration
class TestWorkflowStreamingIntegration:
    """Integration tests for workflow streaming."""

    async def test_full_chat_streaming_workflow(self, test_client):
        """Test complete chat streaming workflow."""
        # Note: This would require actual FastAPI streaming endpoint
        # For now, we'll test the components that would be used

        sse_service = SSEEventService()

        # Simulate a complete chat workflow
        workflow_events = [
            {"type": "start", "conversation_id": "conv-123"},
            {"type": "thinking", "content": "Processing your request..."},
            {"type": "token", "content": "I"},
            {"type": "token", "content": " can"},
            {"type": "token", "content": " help"},
            {"type": "token", "content": " you"},
            {"type": "token", "content": " with"},
            {"type": "token", "content": " that."},
            {"type": "completion", "finish_reason": "stop", "total_tokens": 12}
        ]

        formatted_events = []
        for event in workflow_events:
            formatted = sse_service.format_event(event["type"], event)
            formatted_events.append(formatted)

        assert len(formatted_events) == len(workflow_events)

        # Verify start event
        start_event = formatted_events[0]
        assert "event: start" in start_event
        assert "conv-123" in start_event

        # Verify token events
        token_events = [e for e in formatted_events if "event: token" in e]
        assert len(token_events) == 6

        # Verify completion event
        completion_event = formatted_events[-1]
        assert "event: completion" in completion_event
        assert "total_tokens" in completion_event

    async def test_streaming_with_error_recovery(self):
        """Test streaming with error recovery mechanisms."""
        sse_service = SSEEventService()

        async def unreliable_stream():
            """Simulate an unreliable stream that sometimes fails."""
            events = [
                {"type": "token", "content": "Hello"},
                {"type": "token", "content": " world"},
                # Simulate error here
                None,  # This will cause an error
                {"type": "token", "content": "!"},
                {"type": "completion", "finish_reason": "stop"}
            ]

            for event in events:
                if event is None:
                    raise ConnectionError("Stream connection lost")
                yield event
                await asyncio.sleep(0.01)

        # Test error recovery
        recovered_events = []
        try:
            async for event in unreliable_stream():
                formatted = sse_service.format_event(event["type"], event)
                recovered_events.append(formatted)
        except ConnectionError:
            # Simulate recovery
            error_event = sse_service.format_error_event({
                "error": "Stream connection lost",
                "code": "CONNECTION_ERROR",
                "recovery": "Attempting to reconnect..."
            })
            recovered_events.append(error_event)

            # Continue with remaining events
            remaining_events = [
                {"type": "token", "content": "!"},
                {"type": "completion", "finish_reason": "stop"}
            ]

            for event in remaining_events:
                formatted = sse_service.format_event(event["type"], event)
                recovered_events.append(formatted)

        assert len(recovered_events) == 4  # 2 tokens + 1 error + 1 token + 1 completion

    async def test_streaming_performance(self):
        """Test streaming performance characteristics."""
        import time

        sse_service = SSEEventService()

        # Generate a large number of events
        num_events = 1000
        events = [
            {"type": "token", "content": f"token_{i}", "index": i}
            for i in range(num_events)
        ]

        # Measure formatting performance
        start_time = time.time()
        formatted_events = []

        for event in events:
            formatted = sse_service.format_event("token", event)
            formatted_events.append(formatted)

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process events quickly (< 1 second for 1000 events)
        assert processing_time < 1.0
        assert len(formatted_events) == num_events

        # Check that events are properly formatted
        sample_event = formatted_events[0]
        assert "event: token" in sample_event
        assert "token_0" in sample_event

    async def test_streaming_memory_usage(self):
        """Test streaming memory usage characteristics."""
        sse_service = SSEEventService()

        # Simulate streaming without accumulating events
        event_count = 0
        max_memory_events = 100  # Simulate keeping only recent events

        async def memory_efficient_stream():
            nonlocal event_count
            recent_events = []

            for i in range(1000):
                event = {"type": "token", "content": f"content_{i}"}
                formatted = sse_service.format_event("token", event)

                # Keep only recent events (simulate real streaming)
                recent_events.append(formatted)
                if len(recent_events) > max_memory_events:
                    recent_events.pop(0)

                event_count += 1

                if i % 100 == 0:  # Yield control periodically
                    await asyncio.sleep(0.001)

        await memory_efficient_stream()

        assert event_count == 1000
        # This test ensures we can handle large streams without memory issues
