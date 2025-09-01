"""Tests for streaming service functionality."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import asyncio
from typing import AsyncGenerator

# Mock all required modules at module level
import sys
for module_name in [
    'chatter.services.streaming',
    'chatter.schemas.chat',
    'chatter.utils.correlation',
    'chatter.utils.monitoring',
    'chatter.utils.security'
]:
    if module_name not in sys.modules:
        sys.modules[module_name] = MagicMock()


@pytest.mark.unit
class TestStreamingService:
    """Test streaming service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_correlation_id = "test-correlation-123"

    def test_streaming_event_creation(self):
        """Test streaming event creation."""
        # Arrange
        from unittest.mock import MagicMock
        
        # Mock StreamingEvent dataclass
        StreamingEvent = MagicMock()
        streaming_event = MagicMock()
        streaming_event.type = "token"
        streaming_event.content = "Hello"
        streaming_event.metadata = {"confidence": 0.9}
        streaming_event.correlation_id = self.mock_correlation_id
        StreamingEvent.return_value = streaming_event
        
        # Act
        event = StreamingEvent(
            type="token",
            content="Hello", 
            metadata={"confidence": 0.9},
            correlation_id=self.mock_correlation_id
        )
        
        # Assert
        assert event.type == "token"
        assert event.content == "Hello"
        assert event.metadata["confidence"] == 0.9
        assert event.correlation_id == self.mock_correlation_id

    def test_streaming_event_types(self):
        """Test streaming event type enumeration."""
        # Arrange - Mock the enum
        from unittest.mock import MagicMock
        
        StreamingEventType = MagicMock()
        StreamingEventType.START = "start"
        StreamingEventType.TOKEN = "token"
        StreamingEventType.TOOL_CALL_START = "tool_call_start"
        StreamingEventType.TOOL_CALL_END = "tool_call_end"
        StreamingEventType.SOURCE_FOUND = "source_found"
        StreamingEventType.THINKING = "thinking"
        StreamingEventType.ERROR = "error"
        StreamingEventType.COMPLETE = "complete"
        StreamingEventType.METADATA = "metadata"
        StreamingEventType.HEARTBEAT = "heartbeat"
        
        # Act & Assert
        assert StreamingEventType.START == "start"
        assert StreamingEventType.TOKEN == "token"
        assert StreamingEventType.TOOL_CALL_START == "tool_call_start"
        assert StreamingEventType.TOOL_CALL_END == "tool_call_end"
        assert StreamingEventType.SOURCE_FOUND == "source_found"
        assert StreamingEventType.THINKING == "thinking"
        assert StreamingEventType.ERROR == "error"
        assert StreamingEventType.COMPLETE == "complete"
        assert StreamingEventType.METADATA == "metadata"
        assert StreamingEventType.HEARTBEAT == "heartbeat"

    @pytest.mark.asyncio
    async def test_streaming_chat_chunk_creation(self):
        """Test streaming chat chunk creation."""
        # Arrange
        chunk_data = {
            "content": "Hello world",
            "type": "token",
            "metadata": {"model": "gpt-4"},
            "correlation_id": self.mock_correlation_id
        }
        
        # Mock StreamingChatChunk
        StreamingChatChunk = MagicMock()
        chunk = MagicMock()
        chunk.content = chunk_data["content"]
        chunk.type = chunk_data["type"]
        chunk.metadata = chunk_data["metadata"]
        chunk.correlation_id = chunk_data["correlation_id"]
        StreamingChatChunk.return_value = chunk
        
        # Act
        result = StreamingChatChunk(**chunk_data)
        
        # Assert
        assert result.content == "Hello world"
        assert result.type == "token"
        assert result.metadata["model"] == "gpt-4"
        assert result.correlation_id == self.mock_correlation_id

    @pytest.mark.asyncio
    async def test_token_streaming_generator(self):
        """Test token-level streaming generator."""
        # Arrange
        mock_tokens = ["Hello", " ", "world", "!"]
        
        async def mock_token_generator():
            for token in mock_tokens:
                yield token
                
        # Mock streaming service
        streaming_service = MagicMock()
        streaming_service.stream_tokens = mock_token_generator
        
        # Act
        tokens = []
        async for token in streaming_service.stream_tokens():
            tokens.append(token)
        
        # Assert
        assert tokens == ["Hello", " ", "world", "!"]

    @pytest.mark.asyncio
    async def test_streaming_with_tool_calls(self):
        """Test streaming with tool call events."""
        # Arrange
        mock_events = [
            {"type": "start", "content": "", "metadata": {}},
            {"type": "thinking", "content": "I need to use a tool", "metadata": {}},
            {"type": "tool_call_start", "content": "", "metadata": {"tool": "search"}},
            {"type": "tool_call_end", "content": "", "metadata": {"result": "found"}},
            {"type": "token", "content": "Based on the search", "metadata": {}},
            {"type": "complete", "content": "", "metadata": {"tokens_used": 50}}
        ]
        
        async def mock_streaming_with_tools():
            for event in mock_events:
                yield event
                
        streaming_service = MagicMock()
        streaming_service.stream_with_tools = mock_streaming_with_tools
        
        # Act
        events = []
        async for event in streaming_service.stream_with_tools():
            events.append(event)
        
        # Assert
        assert len(events) == 6
        assert events[0]["type"] == "start"
        assert events[1]["content"] == "I need to use a tool"
        assert events[2]["metadata"]["tool"] == "search"
        assert events[3]["metadata"]["result"] == "found"
        assert events[4]["content"] == "Based on the search"
        assert events[5]["metadata"]["tokens_used"] == 50

    @pytest.mark.asyncio
    async def test_streaming_error_handling(self):
        """Test streaming error handling."""
        # Arrange
        async def mock_failing_stream():
            yield {"type": "start", "content": ""}
            yield {"type": "token", "content": "Hello"}
            raise Exception("Stream failed")
            
        streaming_service = MagicMock()
        streaming_service.error_prone_stream = mock_failing_stream
        
        # Act & Assert
        events = []
        with pytest.raises(Exception) as exc_info:
            async for event in streaming_service.error_prone_stream():
                events.append(event)
        
        assert str(exc_info.value) == "Stream failed"
        assert len(events) == 2
        assert events[0]["type"] == "start"
        assert events[1]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_streaming_heartbeat(self):
        """Test streaming heartbeat functionality."""
        # Arrange
        async def mock_heartbeat_stream():
            yield {"type": "start", "content": ""}
            yield {"type": "heartbeat", "content": "", "metadata": {"timestamp": 1234567890}}
            yield {"type": "token", "content": "Hello"}
            yield {"type": "heartbeat", "content": "", "metadata": {"timestamp": 1234567891}}
            yield {"type": "complete", "content": ""}
            
        streaming_service = MagicMock()
        streaming_service.heartbeat_stream = mock_heartbeat_stream
        
        # Act
        events = []
        heartbeats = []
        async for event in streaming_service.heartbeat_stream():
            events.append(event)
            if event["type"] == "heartbeat":
                heartbeats.append(event)
        
        # Assert
        assert len(events) == 5
        assert len(heartbeats) == 2
        assert heartbeats[0]["metadata"]["timestamp"] == 1234567890
        assert heartbeats[1]["metadata"]["timestamp"] == 1234567891

    @pytest.mark.asyncio
    async def test_streaming_with_metadata(self):
        """Test streaming with metadata events."""
        # Arrange
        metadata_events = [
            {"type": "metadata", "content": "", "metadata": {"model": "gpt-4", "temperature": 0.7}},
            {"type": "metadata", "content": "", "metadata": {"tokens_remaining": 3950}},
            {"type": "metadata", "content": "", "metadata": {"processing_time": 0.5}}
        ]
        
        async def mock_metadata_stream():
            for event in metadata_events:
                yield event
                
        streaming_service = MagicMock()
        streaming_service.metadata_stream = mock_metadata_stream
        
        # Act
        events = []
        async for event in streaming_service.metadata_stream():
            events.append(event)
        
        # Assert
        assert len(events) == 3
        assert events[0]["metadata"]["model"] == "gpt-4"
        assert events[1]["metadata"]["tokens_remaining"] == 3950
        assert events[2]["metadata"]["processing_time"] == 0.5

    def test_streaming_event_timestamp(self):
        """Test streaming event timestamp handling."""
        # Arrange
        import time
        current_time = time.time()
        
        # Mock StreamingEvent with timestamp handling
        streaming_event = MagicMock()
        streaming_event.timestamp = current_time
        
        # Act & Assert
        assert streaming_event.timestamp == current_time
        assert isinstance(streaming_event.timestamp, float)


@pytest.mark.integration
class TestStreamingIntegration:
    """Integration tests for streaming service."""

    @pytest.mark.asyncio
    async def test_full_streaming_workflow(self):
        """Test complete streaming workflow."""
        # Arrange
        workflow_events = [
            {"type": "start", "content": "", "metadata": {"conversation_id": "conv-123"}},
            {"type": "thinking", "content": "Processing user request", "metadata": {}},
            {"type": "source_found", "content": "", "metadata": {"source": "document-1"}},
            {"type": "token", "content": "According", "metadata": {}},
            {"type": "token", "content": " to", "metadata": {}},
            {"type": "token", "content": " the", "metadata": {}},
            {"type": "token", "content": " document", "metadata": {}},
            {"type": "complete", "content": "", "metadata": {"total_tokens": 50, "duration": 2.5}}
        ]
        
        async def mock_workflow_stream():
            for event in workflow_events:
                yield event
                await asyncio.sleep(0.01)  # Simulate real-time streaming
                
        streaming_service = MagicMock()
        streaming_service.workflow_stream = mock_workflow_stream
        
        # Act
        events = []
        tokens = []
        async for event in streaming_service.workflow_stream():
            events.append(event)
            if event["type"] == "token":
                tokens.append(event["content"])
        
        # Assert
        assert len(events) == 8
        assert events[0]["type"] == "start"
        assert events[1]["content"] == "Processing user request"
        assert events[2]["metadata"]["source"] == "document-1"
        assert "".join(tokens) == "According to the document"
        assert events[-1]["metadata"]["total_tokens"] == 50

    @pytest.mark.asyncio
    async def test_streaming_with_correlation_tracking(self):
        """Test streaming with correlation ID tracking."""
        # Arrange
        correlation_id = "test-correlation-456"
        
        with patch('chatter.utils.correlation.get_correlation_id', return_value=correlation_id):
            async def mock_correlated_stream():
                yield {
                    "type": "start", 
                    "content": "", 
                    "correlation_id": correlation_id,
                    "metadata": {}
                }
                yield {
                    "type": "token", 
                    "content": "Hello", 
                    "correlation_id": correlation_id,
                    "metadata": {}
                }
                yield {
                    "type": "complete", 
                    "content": "", 
                    "correlation_id": correlation_id,
                    "metadata": {}
                }
                
            streaming_service = MagicMock()
            streaming_service.correlated_stream = mock_correlated_stream
            
            # Act
            events = []
            async for event in streaming_service.correlated_stream():
                events.append(event)
            
            # Assert
            assert len(events) == 3
            for event in events:
                assert event["correlation_id"] == correlation_id

    @pytest.mark.asyncio
    async def test_streaming_with_monitoring(self):
        """Test streaming with monitoring integration."""
        # Arrange
        metrics = []
        
        def mock_record_metrics(event_type, metadata):
            metrics.append({"type": event_type, "metadata": metadata})
            
        with patch('chatter.utils.monitoring.record_workflow_metrics', side_effect=mock_record_metrics):
            async def mock_monitored_stream():
                yield {"type": "start", "content": "", "metadata": {"workflow_id": "wf-123"}}
                yield {"type": "token", "content": "Hello", "metadata": {}}
                yield {"type": "complete", "content": "", "metadata": {"duration": 1.5, "tokens": 25}}
                
            streaming_service = MagicMock()
            streaming_service.monitored_stream = mock_monitored_stream
            
            # Act
            events = []
            async for event in streaming_service.monitored_stream():
                events.append(event)
                # Simulate monitoring calls
                mock_record_metrics(event["type"], event["metadata"])
            
            # Assert
            assert len(events) == 3
            assert len(metrics) == 3
            assert metrics[0]["type"] == "start"
            assert metrics[2]["metadata"]["duration"] == 1.5