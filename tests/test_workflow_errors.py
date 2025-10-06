"""Tests for workflow error handling."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.services.workflow_errors import (
    WorkflowExecutionError,
    WorkflowPreparationError,
    WorkflowRuntimeError,
    WorkflowResultProcessingError,
    handle_workflow_errors,
)
from chatter.services.workflow_events import WorkflowEventType


def test_workflow_error_hierarchy():
    """Test error class hierarchy."""
    prep_error = WorkflowPreparationError("Prep failed", "exec_123")
    runtime_error = WorkflowRuntimeError("Runtime failed", "exec_456")
    result_error = WorkflowResultProcessingError("Result failed", "exec_789")
    
    assert isinstance(prep_error, WorkflowExecutionError)
    assert isinstance(runtime_error, WorkflowExecutionError)
    assert isinstance(result_error, WorkflowExecutionError)
    
    assert prep_error.execution_id == "exec_123"
    assert runtime_error.execution_id == "exec_456"
    assert result_error.execution_id == "exec_789"


@pytest.mark.asyncio
async def test_handle_workflow_errors_preparation():
    """Test error handler with preparation error."""
    @handle_workflow_errors()
    async def test_function(execution_id: str):
        raise WorkflowPreparationError("Prep failed", execution_id)
    
    with patch('chatter.services.workflow_errors.get_event_bus') as mock_bus:
        mock_event_bus = MagicMock()
        mock_event_bus.publish = AsyncMock()
        mock_bus.return_value = mock_event_bus
        
        with pytest.raises(WorkflowPreparationError):
            await test_function(execution_id="exec_123")
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.event_type == WorkflowEventType.EXECUTION_FAILED
        assert event.execution_id == "exec_123"
        assert event.data["error_type"] == "WorkflowPreparationError"


@pytest.mark.asyncio
async def test_handle_workflow_errors_runtime():
    """Test error handler with runtime error."""
    @handle_workflow_errors()
    async def test_function(execution_id: str):
        raise WorkflowRuntimeError("Runtime failed", execution_id)
    
    with patch('chatter.services.workflow_errors.get_event_bus') as mock_bus:
        mock_event_bus = MagicMock()
        mock_event_bus.publish = AsyncMock()
        mock_bus.return_value = mock_event_bus
        
        with pytest.raises(WorkflowRuntimeError):
            await test_function(execution_id="exec_456")
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.event_type == WorkflowEventType.EXECUTION_FAILED
        assert event.execution_id == "exec_456"
        assert event.data["error_type"] == "WorkflowRuntimeError"


@pytest.mark.asyncio
async def test_handle_workflow_errors_result_processing():
    """Test error handler with result processing error."""
    @handle_workflow_errors()
    async def test_function(execution_id: str):
        raise WorkflowResultProcessingError("Result failed", execution_id)
    
    with patch('chatter.services.workflow_errors.get_event_bus') as mock_bus:
        mock_event_bus = MagicMock()
        mock_event_bus.publish = AsyncMock()
        mock_bus.return_value = mock_event_bus
        
        with pytest.raises(WorkflowResultProcessingError):
            await test_function(execution_id="exec_789")
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.event_type == WorkflowEventType.EXECUTION_FAILED
        assert event.execution_id == "exec_789"
        assert event.data["error_type"] == "WorkflowResultProcessingError"


@pytest.mark.asyncio
async def test_handle_workflow_errors_unexpected():
    """Test error handler with unexpected error."""
    @handle_workflow_errors()
    async def test_function(execution_id: str):
        raise ValueError("Unexpected error")
    
    with patch('chatter.services.workflow_errors.get_event_bus') as mock_bus:
        mock_event_bus = MagicMock()
        mock_event_bus.publish = AsyncMock()
        mock_bus.return_value = mock_event_bus
        
        with pytest.raises(ValueError):
            await test_function(execution_id="exec_abc")
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.event_type == WorkflowEventType.EXECUTION_FAILED
        assert event.execution_id == "exec_abc"
        assert event.data["error_type"] == "ValueError"


@pytest.mark.asyncio
async def test_handle_workflow_errors_with_stage():
    """Test error handler with custom error stage."""
    @handle_workflow_errors(error_stage="custom_stage")
    async def test_function(execution_id: str):
        raise WorkflowPreparationError("Prep failed", execution_id)
    
    with patch('chatter.services.workflow_errors.get_event_bus') as mock_bus:
        mock_event_bus = MagicMock()
        mock_event_bus.publish = AsyncMock()
        mock_bus.return_value = mock_event_bus
        
        with pytest.raises(WorkflowPreparationError):
            await test_function(execution_id="exec_123")
        
        # Verify event has custom stage
        event = mock_event_bus.publish.call_args[0][0]
        assert event.data["error_stage"] == "custom_stage"


@pytest.mark.asyncio
async def test_handle_workflow_errors_success():
    """Test error handler with successful execution."""
    @handle_workflow_errors()
    async def test_function():
        return "success"
    
    with patch('chatter.services.workflow_errors.get_event_bus') as mock_bus:
        mock_event_bus = MagicMock()
        mock_event_bus.publish = AsyncMock()
        mock_bus.return_value = mock_event_bus
        
        result = await test_function()
        
        # Verify no event was published
        mock_event_bus.publish.assert_not_called()
        assert result == "success"


@pytest.mark.asyncio
async def test_handle_workflow_errors_no_execution_id():
    """Test error handler without execution_id."""
    @handle_workflow_errors()
    async def test_function():
        raise ValueError("Error without execution_id")
    
    with patch('chatter.services.workflow_errors.get_event_bus') as mock_bus:
        mock_event_bus = MagicMock()
        mock_event_bus.publish = AsyncMock()
        mock_bus.return_value = mock_event_bus
        
        with pytest.raises(ValueError):
            await test_function()
        
        # Event should not be published without execution_id
        mock_event_bus.publish.assert_not_called()
