"""Test streaming workflow optimization that bypasses create_workflow().call_model() for plain workflows."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from unittest import mock

from chatter.core.unified_workflow_executor import UnifiedWorkflowExecutor
from chatter.models.conversation import Conversation
from chatter.schemas.chat import ChatRequest
from langchain_core.messages import AIMessage


class MockStreamingMessage:
    """Mock streaming message for testing."""
    
    def __init__(self, content="Test response"):
        self.content = content


class MockProvider:
    """Mock LLM provider that simulates streaming."""
    
    def __init__(self, response="Hello, this is a streaming response!"):
        self.response = response
    
    async def astream(self, messages):
        """Simulate streaming response from LLM."""
        for i, char in enumerate(self.response):
            chunk = MagicMock()
            chunk.content = char
            yield chunk


class MockWorkflow:
    """Mock LangGraph workflow that simulates workflow events."""
    
    def __init__(self, response_content="Workflow response"):
        self.response_content = response_content
    
    async def astream(self, state, config):
        """Simulate LangGraph workflow streaming with orchestration overhead."""
        # Simulate memory management node
        yield {'manage_memory': None}
        
        # Simulate call_model node  
        yield {'call_model': {'messages': [AIMessage(content=self.response_content)]}}


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    llm_service = AsyncMock()
    message_service = AsyncMock()
    template_manager = MagicMock()
    
    # Mock message service
    mock_message = MagicMock()
    mock_message.id = "msg_123"
    message_service.add_message_to_conversation = AsyncMock(return_value=mock_message)
    message_service.get_recent_messages = AsyncMock(return_value=[])
    message_service.update_message_content = AsyncMock()
    
    return llm_service, message_service, template_manager


@pytest.fixture
def conversation():
    """Create test conversation."""
    conv = MagicMock(spec=Conversation)
    conv.id = "conv_123"
    conv.user_id = "user_123"
    conv.workspace_id = "workspace_123"
    return conv


@pytest.fixture
def plain_chat_request():
    """Create plain workflow chat request."""
    return ChatRequest(
        message="Hello test",
        workflow="plain",
        workflow_type="plain",
    )


@pytest.fixture
def rag_chat_request():
    """Create RAG workflow chat request."""
    return ChatRequest(
        message="Hello test with RAG",
        workflow="rag",
        workflow_type="rag",
    )


class TestStreamingOptimization:
    """Test that streaming optimization correctly routes workflows."""
    
    @pytest.mark.asyncio
    async def test_plain_workflow_uses_direct_streaming(self, mock_services, conversation, plain_chat_request):
        """Test that plain workflows bypass LangGraph orchestration."""
        llm_service, message_service, template_manager = mock_services
        
        # Mock LLM service to provide direct provider access
        mock_provider = MockProvider("Direct streaming response!")
        llm_service._create_custom_provider = AsyncMock(return_value=mock_provider)
        
        # Create executor
        executor = UnifiedWorkflowExecutor(llm_service, message_service, template_manager)
        
        # Mock internal methods to verify they're called
        executor._setup_execution = AsyncMock(return_value=("workflow_123", None))
        executor._get_workflow_config = MagicMock(return_value={"memory_window": 20})
        executor._prepare_messages = AsyncMock(return_value=[])
        executor._create_streaming_message = AsyncMock(return_value=MockStreamingMessage())
        executor._send_streaming_start_chunk = AsyncMock(return_value={"type": "start"})
        executor._send_streaming_token_chunk = AsyncMock(return_value={"type": "token"})
        executor._finalize_streaming_message = AsyncMock(return_value={"type": "complete"})
        executor._record_metrics = AsyncMock()
        
        # Mock performance monitor
        with patch('chatter.core.streamlined_workflow_performance.performance_monitor') as mock_perf:
            mock_perf.start_workflow = MagicMock()
            
            # Execute streaming
            chunks = []
            async for chunk in executor.execute_streaming(conversation, plain_chat_request, "corr_123", "user_123"):
                chunks.append(chunk)
            
            # Verify direct provider was used (not workflow creation)
            llm_service._create_custom_provider.assert_called_once()
            
            # Verify LangGraph workflow was NOT created
            llm_service.create_langgraph_workflow.assert_not_called()
            
            # Verify we got streaming chunks
            assert len(chunks) >= 1, "Should receive streaming chunks from direct streaming"
    
    @pytest.mark.asyncio 
    async def test_rag_workflow_uses_full_orchestration(self, mock_services, conversation, rag_chat_request):
        """Test that RAG workflows still use full LangGraph orchestration."""
        llm_service, message_service, template_manager = mock_services
        
        # Mock workflow creation
        mock_workflow = MockWorkflow("RAG workflow response")
        llm_service.create_langgraph_workflow = AsyncMock(return_value=mock_workflow)
        
        # Create executor
        executor = UnifiedWorkflowExecutor(llm_service, message_service, template_manager)
        
        # Mock internal methods
        executor._setup_execution = AsyncMock(return_value=("workflow_123", None))
        executor._get_workflow_config = MagicMock(return_value={
            "memory_window": 30, 
            "retriever": None,
            "tools": None,
            "enable_memory": True
        })
        executor._prepare_messages = AsyncMock(return_value=[])
        executor._create_streaming_message = AsyncMock(return_value=MockStreamingMessage())
        executor._send_streaming_start_chunk = AsyncMock(return_value={"type": "start"})
        executor._send_streaming_token_chunk = AsyncMock(return_value={"type": "token"})
        executor._finalize_streaming_message = AsyncMock(return_value={"type": "complete"})
        executor._record_metrics = AsyncMock()
        
        # Mock dependencies
        with patch('chatter.core.dependencies.get_workflow_manager') as mock_get_manager:
            mock_workflow_manager = MagicMock()
            mock_workflow_manager.get_retriever.return_value = None
            mock_get_manager.return_value = mock_workflow_manager
            
            with patch('chatter.core.streamlined_workflow_performance.performance_monitor') as mock_perf:
                mock_perf.start_workflow = MagicMock()
                
                # Execute streaming
                chunks = []
                async for chunk in executor.execute_streaming(conversation, rag_chat_request, "corr_123", "user_123"):
                    chunks.append(chunk)
                
                # Verify LangGraph workflow WAS created for complex workflow
                llm_service.create_langgraph_workflow.assert_called_once()
                
                # Verify direct provider was NOT used
                llm_service._create_custom_provider.assert_not_called()
                
                # Verify we got streaming chunks  
                assert len(chunks) >= 1, "Should receive streaming chunks from workflow orchestration"
    
    @pytest.mark.asyncio
    async def test_performance_difference_simulation(self, mock_services, conversation):
        """Simulate performance difference between direct and orchestrated streaming."""
        llm_service, message_service, template_manager = mock_services
        
        # Setup for plain workflow (direct streaming)
        plain_request = ChatRequest(message="Hello", workflow="plain")
        mock_provider = MockProvider("Quick response")
        llm_service._create_custom_provider = AsyncMock(return_value=mock_provider)
        
        # Setup for RAG workflow (orchestrated streaming)
        rag_request = ChatRequest(message="Hello", workflow="rag")
        mock_workflow = MockWorkflow("Complex response")
        llm_service.create_langgraph_workflow = AsyncMock(return_value=mock_workflow)
        
        executor = UnifiedWorkflowExecutor(llm_service, message_service, template_manager)
        
        # Mock shared methods
        for method_name in ['_setup_execution', '_prepare_messages', '_create_streaming_message', 
                           '_send_streaming_start_chunk', '_send_streaming_token_chunk', 
                           '_finalize_streaming_message', '_record_metrics']:
            setattr(executor, method_name, AsyncMock(return_value=MagicMock()))
        
        executor._get_workflow_config = MagicMock(return_value={"memory_window": 20})
        
        with patch('chatter.core.dependencies.get_workflow_manager'):
            with patch('chatter.core.streamlined_workflow_performance.performance_monitor') as mock_perf:
                mock_perf.start_workflow = MagicMock()
                
                # Test plain workflow
                plain_chunks = []
                async for chunk in executor.execute_streaming(conversation, plain_request, "corr_123", "user_123"):
                    plain_chunks.append(chunk)
                
                # Test RAG workflow  
                rag_chunks = []
                async for chunk in executor.execute_streaming(conversation, rag_request, "corr_123", "user_123"):
                    rag_chunks.append(chunk)
                
                # Verify different code paths were taken
                assert llm_service._create_custom_provider.called, "Plain workflow should use direct provider"
                assert llm_service.create_langgraph_workflow.called, "RAG workflow should use orchestration"
                
                # Both should produce streaming output
                assert len(plain_chunks) >= 1, "Plain workflow should produce chunks"
                assert len(rag_chunks) >= 1, "RAG workflow should produce chunks"
    
    def test_code_architecture_verification(self):
        """Verify the code architecture correctly implements the optimization."""
        import inspect
        
        # Check that execute_streaming has the routing logic
        source = inspect.getsource(UnifiedWorkflowExecutor.execute_streaming)
        assert 'if workflow_type == "plain":' in source, "Should route plain workflows differently"
        assert '_execute_direct_streaming' in source, "Should call direct streaming method"
        assert '_execute_workflow_streaming' in source, "Should call workflow streaming method"
        
        # Check that direct streaming method exists
        assert hasattr(UnifiedWorkflowExecutor, '_execute_direct_streaming'), "Direct streaming method should exist"
        
        # Check that workflow streaming method exists
        assert hasattr(UnifiedWorkflowExecutor, '_execute_workflow_streaming'), "Workflow streaming method should exist"
        
        # Verify direct streaming bypasses workflow creation
        direct_source = inspect.getsource(UnifiedWorkflowExecutor._execute_direct_streaming)
        assert 'provider.astream' in direct_source, "Direct streaming should use provider.astream"
        assert 'create_langgraph_workflow' not in direct_source, "Direct streaming should not create workflows"
        
        # Verify workflow streaming uses orchestration
        workflow_source = inspect.getsource(UnifiedWorkflowExecutor._execute_workflow_streaming)
        assert 'workflow.astream' in workflow_source, "Workflow streaming should use workflow.astream"
        assert 'create_langgraph_workflow' in workflow_source, "Workflow streaming should create workflows"