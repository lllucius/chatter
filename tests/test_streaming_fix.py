#!/usr/bin/env python3
"""Test that the streaming fix is working correctly."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatter.core.workflow_execution_engine import ExecutionEngine
from chatter.schemas.execution import ExecutionRequest


class TestStreamingFix:
    """Test that streaming is now enabled correctly."""

    @pytest.mark.asyncio
    async def test_execute_streaming_calls_stream_workflow_with_enable_llm_streaming(
        self, monkeypatch
    ):
        """Test that _execute_streaming calls stream_workflow with enable_llm_streaming=True."""
        # Create mock session and llm_service
        mock_session = MagicMock()
        mock_llm_service = MagicMock()
        mock_llm_service.get_llm = AsyncMock()

        # Create engine
        engine = ExecutionEngine(
            session=mock_session, llm_service=mock_llm_service
        )

        # Create mock context
        from chatter.core.workflow_execution_context import (
            ExecutionConfig,
            ExecutionContext,
            WorkflowType,
        )

        mock_llm = MagicMock()
        config = ExecutionConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            enable_tools=False,
            enable_retrieval=False,
            enable_memory=False,
        )

        context = ExecutionContext(
            execution_id="test_id",
            user_id="user_123",
            workflow_type=WorkflowType.CHAT,
            config=config,
            llm=mock_llm,
        )

        # Mock workflow manager's stream_workflow
        from chatter.core.langgraph import workflow_manager

        stream_workflow_calls = []

        async def mock_stream_workflow(*args, **kwargs):
            # Record the call parameters
            stream_workflow_calls.append(kwargs)
            # Yield a token event
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": {"content": "test"}},
            }
            # Yield an end event
            yield {
                "event": "on_chat_model_end",
                "data": {
                    "output": {
                        "usage_metadata": {
                            "total_tokens": 10,
                            "input_tokens": 5,
                            "output_tokens": 5,
                        }
                    }
                },
            }

        # Patch stream_workflow
        with patch.object(
            workflow_manager, "stream_workflow", side_effect=mock_stream_workflow
        ):
            # Mock tracker to avoid database calls
            engine.tracker.start = AsyncMock()
            engine.tracker.complete = AsyncMock()

            # Create a mock graph
            mock_graph = MagicMock()

            # Call _execute_streaming
            chunks = []
            async for chunk in engine._execute_streaming(mock_graph, context):
                chunks.append(chunk)

        # Verify that stream_workflow was called
        assert len(stream_workflow_calls) > 0, "stream_workflow should be called"

        # Verify that enable_llm_streaming=True was passed
        call_kwargs = stream_workflow_calls[0]
        assert (
            "enable_llm_streaming" in call_kwargs
        ), "enable_llm_streaming should be in kwargs"
        assert (
            call_kwargs["enable_llm_streaming"] is True
        ), "enable_llm_streaming should be True"

        # Verify that we got streaming chunks
        assert len(chunks) > 0, "Should generate streaming chunks"

        # Verify token chunk was received
        token_chunks = [c for c in chunks if c.type == "token"]
        assert len(token_chunks) > 0, "Should have token chunks"
        assert token_chunks[0].content == "test", "Should have correct content"
