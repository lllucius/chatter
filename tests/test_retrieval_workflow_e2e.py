"""End-to-end test demonstrating the document retrieval fix."""
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from langchain_core.messages import HumanMessage

from chatter.core.workflow_node_factory import WorkflowNodeContext


@pytest.mark.asyncio
async def test_retrieval_workflow_end_to_end():
    """Test that document retrieval works in a complete workflow."""
    
    # Mock embeddings provider
    mock_embeddings = AsyncMock()
    mock_embeddings.aembed_query = AsyncMock(return_value=[0.1] * 768)
    
    # Mock embedding service
    mock_embedding_service = Mock()
    mock_embedding_service.get_default_provider = AsyncMock(
        return_value=mock_embeddings
    )
    
    # Mock document chunk with realistic data
    mock_chunk = Mock()
    mock_chunk.content = "Python is a high-level programming language. It was created by Guido van Rossum."
    mock_chunk.document_id = "doc_12345"
    mock_chunk.chunk_index = 0
    
    # Mock vector store
    mock_vector_store = AsyncMock()
    mock_vector_store.search_similar = AsyncMock(
        return_value=[(mock_chunk, 0.89)]
    )
    
    # Mock database session
    async def mock_session_generator():
        yield AsyncMock()
    
    with patch(
        'chatter.core.vector_store.get_embedding_service',
        return_value=mock_embedding_service
    ), patch(
        'chatter.core.custom_retriever.get_session_generator',
        return_value=mock_session_generator()
    ), patch(
        'chatter.core.custom_retriever.SimpleVectorStore',
        return_value=mock_vector_store
    ):
        # Import after patches are in place
        from chatter.core.vector_store import get_vector_store_retriever
        from chatter.core.langgraph import workflow_manager
        
        # Create retriever
        retriever = await get_vector_store_retriever(
            user_id="user_123",
            document_ids=["doc_12345"],
        )
        
        # Verify retriever was created
        assert retriever is not None
        
        # Test retriever directly
        results = await retriever.ainvoke("What is Python?")
        
        # Verify results
        assert len(results) == 1
        assert "Python" in results[0].page_content
        assert "programming language" in results[0].page_content
        assert results[0].metadata["document_id"] == "doc_12345"
        
        # Now test in a workflow context
        # Mock LLM
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Python is a programming language created by Guido van Rossum.")
        )
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)
        
        # Create workflow with retrieval
        workflow = await workflow_manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=True,
            retriever=retriever,
            enable_tools=False,
            enable_memory=False,
        )
        
        # Create initial state
        initial_state: WorkflowNodeContext = {
            "messages": [HumanMessage(content="What is Python?")],
            "user_id": "user_123",
            "conversation_id": "conv_123",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }
        
        # Execute workflow
        result = await workflow_manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="thread_123",
        )
        
        # Verify retriever was called
        assert mock_embeddings.aembed_query.called
        assert mock_vector_store.search_similar.called
        
        # Verify retrieval context was set
        assert result.get("retrieval_context") is not None
        assert "Python" in result["retrieval_context"]
        
        # Verify LLM was called with context
        assert mock_llm.ainvoke.called
        call_args = mock_llm.ainvoke.call_args[0][0]
        
        # Check that system message includes retrieval context
        system_messages = [
            msg for msg in call_args 
            if hasattr(msg, '__class__') and msg.__class__.__name__ == 'SystemMessage'
        ]
        assert len(system_messages) > 0
        
        # Verify context was included in system message
        system_content = system_messages[0].content
        assert "Python" in system_content
        assert "programming language" in system_content


@pytest.mark.asyncio
async def test_retrieval_with_no_results():
    """Test that workflow handles no retrieval results gracefully."""
    
    # Mock embeddings provider
    mock_embeddings = AsyncMock()
    mock_embeddings.aembed_query = AsyncMock(return_value=[0.1] * 768)
    
    # Mock embedding service
    mock_embedding_service = Mock()
    mock_embedding_service.get_default_provider = AsyncMock(
        return_value=mock_embeddings
    )
    
    # Mock vector store that returns no results
    mock_vector_store = AsyncMock()
    mock_vector_store.search_similar = AsyncMock(return_value=[])
    
    # Mock database session
    async def mock_session_generator():
        yield AsyncMock()
    
    with patch(
        'chatter.core.vector_store.get_embedding_service',
        return_value=mock_embedding_service
    ), patch(
        'chatter.core.custom_retriever.get_session_generator',
        return_value=mock_session_generator()
    ), patch(
        'chatter.core.custom_retriever.SimpleVectorStore',
        return_value=mock_vector_store
    ):
        # Import after patches
        from chatter.core.vector_store import get_vector_store_retriever
        
        # Create retriever
        retriever = await get_vector_store_retriever(
            user_id="user_123",
            document_ids=["doc_nonexistent"],
        )
        
        # Test retriever with no results
        results = await retriever.ainvoke("Query with no matches")
        
        # Should return empty list, not error
        assert results == []
