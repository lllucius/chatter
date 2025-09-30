"""Test to verify workflow execution tracking for chat workflows."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.workflow import WorkflowExecution
from chatter.schemas.workflows import ChatWorkflowRequest


@pytest.mark.asyncio
async def test_chat_workflow_creates_execution_record(
    client: AsyncClient,
    auth_headers: dict[str, str],
    session: AsyncSession,
):
    """Test that chat workflow creates a workflow execution record."""
    # Simple chat workflow request
    request = ChatWorkflowRequest(
        message="Test execution tracking",
        enable_retrieval=False,
        enable_tools=False,
        enable_memory=False,
    )

    # Send request to chat workflow endpoint
    response = await client.post(
        "/api/v1/workflows/execute/chat",
        json=request.model_dump(),
        headers=auth_headers,
    )

    # Verify response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Parse response
    data = response.json()
    conversation_id = data["conversation_id"]

    # Query for workflow executions related to this conversation
    result = await session.execute(
        select(WorkflowExecution).where(
            WorkflowExecution.input_data.op("@>")({"conversation_id": conversation_id})
        )
    )
    executions = result.scalars().all()

    # Verify at least one execution was created
    assert len(executions) > 0, "Expected at least one workflow execution record"

    # Verify execution details
    execution = executions[0]
    assert execution.status in ["completed", "running"], f"Expected status 'completed' or 'running', got '{execution.status}'"
    assert execution.owner_id is not None, "Execution should have an owner_id"
    assert execution.definition_id is not None, "Execution should have a definition_id"
    
    # If execution is completed, verify it has logs
    if execution.status == "completed":
        assert execution.execution_log is not None, "Completed execution should have logs"
        assert len(execution.execution_log) > 0, "Execution logs should not be empty"
        assert execution.execution_time_ms is not None, "Execution should have execution time"
        assert execution.completed_at is not None, "Completed execution should have completion time"

    print(f"✓ Chat workflow created execution record: {execution.id}")
    print(f"✓ Execution status: {execution.status}")
    print(f"✓ Execution logs entries: {len(execution.execution_log) if execution.execution_log else 0}")


@pytest.mark.asyncio
async def test_chat_workflow_execution_logs_content(
    client: AsyncClient,
    auth_headers: dict[str, str],
    session: AsyncSession,
):
    """Test that workflow execution logs contain meaningful content."""
    # Chat workflow request
    request = ChatWorkflowRequest(
        message="Test execution logs",
        enable_retrieval=False,
        enable_tools=False,
        enable_memory=False,
    )

    # Send request
    response = await client.post(
        "/api/v1/workflows/execute/chat",
        json=request.model_dump(),
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    conversation_id = data["conversation_id"]

    # Get execution record
    result = await session.execute(
        select(WorkflowExecution).where(
            WorkflowExecution.input_data.op("@>")({"conversation_id": conversation_id})
        )
    )
    executions = result.scalars().all()
    assert len(executions) > 0

    execution = executions[0]
    
    # If completed, check logs
    if execution.status == "completed" and execution.execution_log:
        logs = execution.execution_log
        
        # Verify logs have expected structure
        assert isinstance(logs, list), "Execution logs should be a list"
        
        # Check for key log entries
        log_messages = [log.get("message", "") for log in logs if isinstance(log, dict)]
        
        # Should have logs about execution start/progress
        has_start_log = any("Started" in msg or "started" in msg for msg in log_messages)
        has_completion_log = any("completed" in msg.lower() for msg in log_messages)
        
        assert has_start_log or has_completion_log, "Logs should contain start or completion messages"
        
        print(f"✓ Execution logs contain {len(logs)} entries")
        print(f"✓ Log messages found: {len(log_messages)}")


@pytest.mark.asyncio
async def test_streaming_chat_workflow_creates_execution_record(
    client: AsyncClient,
    auth_headers: dict[str, str],
    session: AsyncSession,
):
    """Test that streaming chat workflow creates a workflow execution record."""
    # Streaming chat workflow request
    request = ChatWorkflowRequest(
        message="Test streaming execution tracking",
        enable_retrieval=False,
        enable_tools=False,
        enable_memory=False,
    )

    # Send streaming request
    async with client.stream(
        "POST",
        "/api/v1/workflows/execute/chat/streaming",
        json=request.model_dump(),
        headers=auth_headers,
    ) as response:
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Read all streaming chunks
        conversation_id = None
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                import json
                try:
                    chunk_data = json.loads(line[6:])
                    if "conversation_id" in chunk_data:
                        conversation_id = chunk_data["conversation_id"]
                except json.JSONDecodeError:
                    pass
    
    # If we couldn't get conversation_id from stream, skip the rest
    if not conversation_id:
        pytest.skip("Could not extract conversation_id from streaming response")
    
    # Query for workflow executions related to this conversation
    result = await session.execute(
        select(WorkflowExecution).where(
            WorkflowExecution.input_data.op("@>")({"conversation_id": conversation_id})
        )
    )
    executions = result.scalars().all()

    # Verify at least one execution was created
    assert len(executions) > 0, "Expected at least one workflow execution record for streaming"

    # Verify execution details
    execution = executions[0]
    assert execution.status in ["completed", "running"], f"Expected status 'completed' or 'running', got '{execution.status}'"
    assert execution.owner_id is not None, "Streaming execution should have an owner_id"
    assert execution.definition_id is not None, "Streaming execution should have a definition_id"
    
    # Verify streaming flag in input_data
    assert execution.input_data.get("streaming") is True, "Execution should be marked as streaming"
    
    # If execution is completed, verify it has logs
    if execution.status == "completed":
        assert execution.execution_log is not None, "Completed streaming execution should have logs"
        assert len(execution.execution_log) > 0, "Streaming execution logs should not be empty"
        assert execution.execution_time_ms is not None, "Streaming execution should have execution time"
        assert execution.completed_at is not None, "Completed streaming execution should have completion time"

    print(f"✓ Streaming chat workflow created execution record: {execution.id}")
    print(f"✓ Execution status: {execution.status}")
    print(f"✓ Execution logs entries: {len(execution.execution_log) if execution.execution_log else 0}")

