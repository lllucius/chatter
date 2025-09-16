"""Test enhanced LangGraph streaming support."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from unittest import mock

from chatter.core.langgraph import LangGraphWorkflowManager
from chatter.services.llm import LLMService
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


class MockLLM(BaseChatModel):
    """Mock LLM for testing."""
    
    def __init__(self, response_content="Mock response"):
        super().__init__()
        self.response_content = response_content
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatGeneration, ChatResult
        message = AIMessage(content=self.response_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatGeneration, ChatResult
        message = AIMessage(content=self.response_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    
    async def ainvoke(self, messages, **kwargs):
        return AIMessage(content=self.response_content)
    
    async def astream(self, messages, **kwargs):
        for char in self.response_content:
            yield AIMessage(content=char)
    
    def invoke(self, messages, **kwargs):
        return AIMessage(content=self.response_content)
    
    def stream(self, messages, **kwargs):
        for char in self.response_content:
            yield AIMessage(content=char)
    
    @property
    def _llm_type(self) -> str:
        return "mock"


class TestLangGraphStreamingEnhancement:
    """Test LangGraph streaming enhancements."""
    
    def test_langgraph_workflow_manager_has_get_tools_method(self):
        """Test that LangGraphWorkflowManager has the get_tools method."""
        manager = LangGraphWorkflowManager()
        assert hasattr(manager, 'get_tools'), "LangGraphWorkflowManager should have get_tools method"
        
        # Test the method is callable
        tools = manager.get_tools("test_workspace")
        assert isinstance(tools, list), "get_tools should return a list"
    
    def test_langgraph_workflow_manager_has_get_retriever_method(self):
        """Test that LangGraphWorkflowManager has the get_retriever method."""
        manager = LangGraphWorkflowManager()
        assert hasattr(manager, 'get_retriever'), "LangGraphWorkflowManager should have get_retriever method"
        
        # Test the method is callable (will return None if no embeddings available)
        retriever = manager.get_retriever("test_workspace")
        # This can be None if no embeddings service is available, which is fine for this test
        assert retriever is None or hasattr(retriever, 'invoke'), "get_retriever should return None or a retriever object"
    
    @pytest.mark.asyncio
    async def test_langgraph_workflow_supports_streaming(self):
        """Test that LangGraph workflows support streaming."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()
        
        # Create a simple workflow
        llm = MockLLM("Hello streaming world!")
        workflow = await manager.create_workflow(
            llm=llm,
            mode="plain",
            system_message="You are a helpful assistant."
        )
        
        # Test that the workflow has astream method (LangGraph streaming interface)
        assert hasattr(workflow, 'astream'), "LangGraph workflow should have astream method"
        assert hasattr(workflow, 'ainvoke'), "LangGraph workflow should have ainvoke method"
    
    @pytest.mark.asyncio
    async def test_workflow_streaming_with_different_modes(self):
        """Test that all workflow modes support streaming."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()
        
        llm = MockLLM("Test response for different modes")
        
        # Test all workflow modes
        modes = ["plain", "rag", "tools", "full"]
        
        for mode in modes:
            workflow = await manager.create_workflow(
                llm=llm,
                mode=mode,
                system_message=f"Test mode: {mode}"
            )
            
            assert hasattr(workflow, 'astream'), f"Workflow mode '{mode}' should support streaming"
            assert hasattr(workflow, 'ainvoke'), f"Workflow mode '{mode}' should support regular execution"
    
    @pytest.mark.asyncio
    async def test_llm_service_create_langgraph_workflow_with_streaming(self):
        """Test that LLM service creates workflows that support streaming."""
        # Mock the LLM service dependencies
        with mock.patch('chatter.services.llm.get_mcp_service') as mock_mcp, \
             mock.patch('chatter.services.llm.get_builtin_tools') as mock_tools, \
             mock.patch('chatter.core.langgraph.workflow_manager') as mock_manager:
            
            # Setup mocks
            mock_mcp.return_value.get_tools = AsyncMock(return_value=[])
            mock_tools.return_value = []
            
            mock_workflow = MagicMock()
            mock_workflow.astream = AsyncMock()
            mock_workflow.ainvoke = AsyncMock()
            mock_manager.create_workflow = AsyncMock(return_value=mock_workflow)
            
            # Create LLM service
            llm_service = LLMService()
            
            # Mock provider creation
            llm_service.get_default_provider = AsyncMock(return_value=MockLLM())
            
            # Test workflow creation
            workflow = await llm_service.create_langgraph_workflow(
                provider_name=None,
                workflow_type="plain",
                system_message="Test streaming",
                enable_memory=True,
                memory_window=10
            )
            
            # Verify streaming methods are available
            assert hasattr(workflow, 'astream'), "Workflow should have astream method"
            assert hasattr(workflow, 'ainvoke'), "Workflow should have ainvoke method"
            
            # Verify the workflow manager was called with correct parameters
            mock_manager.create_workflow.assert_called_once()
            call_args = mock_manager.create_workflow.call_args
            assert call_args[1]['mode'] == 'plain'
            assert call_args[1]['enable_memory'] == True
            assert call_args[1]['memory_window'] == 10
    
    @pytest.mark.asyncio
    async def test_enhanced_workflow_streaming_with_tools(self):
        """Test enhanced streaming support with tools workflow."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()
        
        # Mock tools
        mock_tools = [MagicMock(name="test_tool")]
        
        llm = MockLLM("Tool workflow response")
        workflow = await manager.create_workflow(
            llm=llm,
            mode="tools",
            tools=mock_tools,
            enable_memory=True,
            memory_window=50
        )
        
        # Test that workflow supports streaming
        assert hasattr(workflow, 'astream'), "Tools workflow should support streaming"
        
        # Create test state
        from chatter.core.langgraph import ConversationState
        test_state = ConversationState(
            messages=[HumanMessage(content="Test message")],
            user_id="test_user",
            conversation_id="test_conv",
            retrieval_context=None,
            tool_calls=[],
            metadata={},
            conversation_summary=None,
            parent_conversation_id=None,
            branch_id=None,
            memory_context={},
            workflow_template=None,
            a_b_test_group=None
        )
        
        # Test streaming execution
        events = []
        async for event in workflow.astream(test_state, {"configurable": {"thread_id": "test_thread"}}):
            events.append(event)
            
        # Should have gotten some events
        assert len(events) > 0, "Streaming should produce events"
    
    @pytest.mark.asyncio
    async def test_enhanced_workflow_streaming_with_rag(self):
        """Test enhanced streaming support with RAG workflow."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()
        
        # Mock retriever
        mock_retriever = MagicMock()
        mock_retriever.ainvoke = AsyncMock(return_value=[])
        
        llm = MockLLM("RAG workflow response")
        workflow = await manager.create_workflow(
            llm=llm,
            mode="rag",
            retriever=mock_retriever,
            enable_memory=True,
            memory_window=30,
            max_documents=5
        )
        
        # Test that workflow supports streaming
        assert hasattr(workflow, 'astream'), "RAG workflow should support streaming"
        
        # Create test state
        from chatter.core.langgraph import ConversationState
        test_state = ConversationState(
            messages=[HumanMessage(content="What is the answer?")],
            user_id="test_user",
            conversation_id="test_conv",
            retrieval_context=None,
            tool_calls=[],
            metadata={},
            conversation_summary=None,
            parent_conversation_id=None,
            branch_id=None,
            memory_context={},
            workflow_template=None,
            a_b_test_group=None
        )
        
        # Test streaming execution
        events = []
        async for event in workflow.astream(test_state, {"configurable": {"thread_id": "test_thread"}}):
            events.append(event)
            
        # Should have gotten some events
        assert len(events) > 0, "RAG streaming should produce events"