"""Tests for workflow preparation service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.services.workflow_preparation import (
    PreparedWorkflow,
    WorkflowPreparationService,
)
from chatter.services.workflow_types import (
    WorkflowConfig,
    WorkflowSource,
    WorkflowSourceType,
)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    service = MagicMock()
    service.get_llm = AsyncMock(return_value=MagicMock())
    return service


@pytest.fixture
def mock_session():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def preparation_service(mock_llm_service, mock_session):
    """Create preparation service with mocks."""
    return WorkflowPreparationService(mock_llm_service, mock_session)


def test_prepared_workflow_creation():
    """Test PreparedWorkflow dataclass creation."""
    mock_workflow = MagicMock()
    mock_definition = MagicMock()
    mock_llm = MagicMock()
    mock_tools = [MagicMock()]
    mock_retriever = MagicMock()
    mock_config = WorkflowConfig()

    prepared = PreparedWorkflow(
        workflow=mock_workflow,
        definition=mock_definition,
        llm=mock_llm,
        tools=mock_tools,
        retriever=mock_retriever,
        config=mock_config,
    )

    assert prepared.workflow == mock_workflow
    assert prepared.definition == mock_definition
    assert prepared.llm == mock_llm
    assert prepared.tools == mock_tools
    assert prepared.retriever == mock_retriever
    assert prepared.config == mock_config


@pytest.mark.asyncio
async def test_prepare_workflow_template_source(preparation_service):
    """Test preparing workflow from template source."""
    source = WorkflowSource(
        source_type=WorkflowSourceType.TEMPLATE,
        source_id="template_123",
    )
    config = WorkflowConfig(
        provider="openai",
        model="gpt-4",
    )

    # Mock the internal methods
    mock_definition = MagicMock()
    mock_workflow = MagicMock()
    
    with patch.object(
        preparation_service, '_prepare_from_template', 
        AsyncMock(return_value=mock_definition)
    ), patch.object(
        preparation_service, '_get_tools',
        AsyncMock(return_value=None)
    ), patch.object(
        preparation_service, '_get_retriever',
        AsyncMock(return_value=None)
    ), patch.object(
        preparation_service, '_create_workflow',
        AsyncMock(return_value=mock_workflow)
    ):
        result = await preparation_service.prepare_workflow(
            source=source,
            config=config,
            user_id="user_123",
            conversation_id="conv_456",
        )

        assert isinstance(result, PreparedWorkflow)
        assert result.workflow == mock_workflow
        assert result.definition == mock_definition
        assert result.config == config


@pytest.mark.asyncio
async def test_prepare_workflow_definition_source(preparation_service):
    """Test preparing workflow from definition source."""
    source = WorkflowSource(
        source_type=WorkflowSourceType.DEFINITION,
        source_id="def_123",
    )
    config = WorkflowConfig()

    mock_definition = MagicMock()
    mock_workflow = MagicMock()

    with patch.object(
        preparation_service, '_prepare_from_definition',
        AsyncMock(return_value=mock_definition)
    ), patch.object(
        preparation_service, '_get_tools',
        AsyncMock(return_value=None)
    ), patch.object(
        preparation_service, '_get_retriever',
        AsyncMock(return_value=None)
    ), patch.object(
        preparation_service, '_create_workflow',
        AsyncMock(return_value=mock_workflow)
    ):
        result = await preparation_service.prepare_workflow(
            source=source,
            config=config,
            user_id="user_123",
            conversation_id="conv_456",
        )

        assert isinstance(result, PreparedWorkflow)
        assert result.workflow == mock_workflow


@pytest.mark.asyncio
async def test_prepare_workflow_dynamic_source(preparation_service):
    """Test preparing workflow from dynamic source."""
    source = WorkflowSource(source_type=WorkflowSourceType.DYNAMIC)
    config = WorkflowConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        enable_tools=True,
    )

    mock_definition = MagicMock()
    mock_workflow = MagicMock()
    mock_tools = [MagicMock()]

    with patch.object(
        preparation_service, '_prepare_dynamic',
        AsyncMock(return_value=mock_definition)
    ), patch.object(
        preparation_service, '_get_tools',
        AsyncMock(return_value=mock_tools)
    ), patch.object(
        preparation_service, '_get_retriever',
        AsyncMock(return_value=None)
    ), patch.object(
        preparation_service, '_create_workflow',
        AsyncMock(return_value=mock_workflow)
    ):
        result = await preparation_service.prepare_workflow(
            source=source,
            config=config,
            user_id="user_123",
            conversation_id="conv_456",
        )

        assert isinstance(result, PreparedWorkflow)
        assert result.tools == mock_tools


@pytest.mark.asyncio
async def test_prepare_workflow_with_retrieval(preparation_service):
    """Test preparing workflow with retrieval enabled."""
    source = WorkflowSource(source_type=WorkflowSourceType.DYNAMIC)
    config = WorkflowConfig(
        enable_retrieval=True,
        document_ids=["doc1", "doc2"],
    )

    mock_definition = MagicMock()
    mock_workflow = MagicMock()
    mock_retriever = MagicMock()

    with patch.object(
        preparation_service, '_prepare_dynamic',
        AsyncMock(return_value=mock_definition)
    ), patch.object(
        preparation_service, '_get_tools',
        AsyncMock(return_value=None)
    ), patch.object(
        preparation_service, '_get_retriever',
        AsyncMock(return_value=mock_retriever)
    ), patch.object(
        preparation_service, '_create_workflow',
        AsyncMock(return_value=mock_workflow)
    ):
        result = await preparation_service.prepare_workflow(
            source=source,
            config=config,
            user_id="user_123",
            conversation_id="conv_456",
        )

        assert result.retriever == mock_retriever


@pytest.mark.asyncio
async def test_get_tools_with_filtering(preparation_service):
    """Test tool loading with filtering."""
    config = WorkflowConfig(
        enable_tools=True,
        allowed_tools=["calculator", "search"],
    )

    mock_tool_1 = MagicMock()
    mock_tool_2 = MagicMock()
    mock_tool_3 = MagicMock()

    with patch('chatter.services.workflow_preparation.tool_registry') as mock_registry:
        mock_registry.get_enabled_tools_for_workspace = AsyncMock(
            return_value=[mock_tool_1, mock_tool_2, mock_tool_3]
        )
        mock_registry._get_tool_name = lambda tool: {
            mock_tool_1: "calculator",
            mock_tool_2: "search",
            mock_tool_3: "other",
        }[tool]

        tools = await preparation_service._get_tools(config, "user_123")

        # Should filter to only calculator and search
        assert len(tools) == 2
        assert mock_tool_1 in tools
        assert mock_tool_2 in tools
        assert mock_tool_3 not in tools
