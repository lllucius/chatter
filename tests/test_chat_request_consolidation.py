"""Test consolidation of ChatRequest and ChatWorkflowRequest."""

import pytest

from chatter.schemas.chat import ChatRequest
from chatter.schemas.workflows import ChatWorkflowRequest


class TestChatRequestConsolidation:
    """Test that ChatRequest now supports all workflow features."""

    def test_chat_workflow_request_is_alias(self):
        """Test that ChatWorkflowRequest is an alias to ChatRequest."""
        assert ChatWorkflowRequest is ChatRequest

    def test_basic_chat_request(self):
        """Test creating a basic chat request."""
        request = ChatRequest(message="Hello, world!")
        assert request.message == "Hello, world!"
        assert request.conversation_id is None
        assert request.enable_retrieval is False
        assert request.enable_tools is False
        assert request.enable_memory is True
        assert request.enable_tracing is False

    def test_chat_request_with_workflow_definition(self):
        """Test creating a chat request with workflow definition ID."""
        request = ChatRequest(
            message="Test message",
            workflow_definition_id="def-123",
            conversation_id="conv-456"
        )
        assert request.message == "Test message"
        assert request.workflow_definition_id == "def-123"
        assert request.conversation_id == "conv-456"

    def test_chat_request_with_workflow_template(self):
        """Test creating a chat request with workflow template name."""
        request = ChatRequest(
            message="Test message",
            workflow_template_name="rag-template",
            enable_retrieval=True
        )
        assert request.message == "Test message"
        assert request.workflow_template_name == "rag-template"
        assert request.enable_retrieval is True

    def test_chat_request_with_all_fields(self):
        """Test creating a chat request with all available fields."""
        request = ChatRequest(
            message="Test message",
            conversation_id="conv-123",
            profile_id="profile-456",
            workflow_config={"nodes": [], "edges": []},
            workflow_definition_id="def-789",
            workflow_template_name="template-abc",
            enable_retrieval=True,
            enable_tools=True,
            enable_memory=True,
            enable_web_search=True,
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            context_limit=4096,
            document_ids=["doc-1", "doc-2"],
            prompt_id="prompt-123",
            system_prompt_override="Custom system prompt",
            enable_tracing=True
        )
        assert request.message == "Test message"
        assert request.conversation_id == "conv-123"
        assert request.profile_id == "profile-456"
        assert request.workflow_config == {"nodes": [], "edges": []}
        assert request.workflow_definition_id == "def-789"
        assert request.workflow_template_name == "template-abc"
        assert request.enable_retrieval is True
        assert request.enable_tools is True
        assert request.enable_memory is True
        assert request.enable_web_search is True
        assert request.provider == "openai"
        assert request.model == "gpt-4"
        assert request.temperature == 0.7
        assert request.max_tokens == 1000
        assert request.context_limit == 4096
        assert request.document_ids == ["doc-1", "doc-2"]
        assert request.prompt_id == "prompt-123"
        assert request.system_prompt_override == "Custom system prompt"
        assert request.enable_tracing is True

    def test_backward_compatibility_with_chat_workflow_request(self):
        """Test that ChatWorkflowRequest still works (backward compatibility)."""
        request = ChatWorkflowRequest(
            message="Test message",
            workflow_definition_id="def-123",
            enable_tracing=True
        )
        assert isinstance(request, ChatRequest)
        assert request.message == "Test message"
        assert request.workflow_definition_id == "def-123"
        assert request.enable_tracing is True

    def test_serialization(self):
        """Test that request can be serialized and deserialized."""
        original = ChatRequest(
            message="Test message",
            workflow_definition_id="def-123",
            enable_retrieval=True,
            enable_tracing=True
        )
        
        # Serialize to dict
        data = original.model_dump()
        assert data["message"] == "Test message"
        assert data["workflow_definition_id"] == "def-123"
        assert data["enable_retrieval"] is True
        assert data["enable_tracing"] is True
        
        # Deserialize from dict
        restored = ChatRequest(**data)
        assert restored.message == original.message
        assert restored.workflow_definition_id == original.workflow_definition_id
        assert restored.enable_retrieval == original.enable_retrieval
        assert restored.enable_tracing == original.enable_tracing

    def test_validation_message_required(self):
        """Test that message field is required."""
        with pytest.raises(ValueError):
            ChatRequest()

    def test_validation_temperature_range(self):
        """Test that temperature must be within valid range."""
        with pytest.raises(ValueError):
            ChatRequest(message="Test", temperature=3.0)
        
        with pytest.raises(ValueError):
            ChatRequest(message="Test", temperature=-1.0)
        
        # Valid temperatures
        ChatRequest(message="Test", temperature=0.0)
        ChatRequest(message="Test", temperature=1.0)
        ChatRequest(message="Test", temperature=2.0)

    def test_validation_max_tokens_range(self):
        """Test that max_tokens must be within valid range."""
        with pytest.raises(ValueError):
            ChatRequest(message="Test", max_tokens=0)
        
        with pytest.raises(ValueError):
            ChatRequest(message="Test", max_tokens=10000)
        
        # Valid max_tokens
        ChatRequest(message="Test", max_tokens=1)
        ChatRequest(message="Test", max_tokens=100)
        ChatRequest(message="Test", max_tokens=8192)

    def test_optional_fields_default_to_none(self):
        """Test that optional fields default to None or appropriate values."""
        request = ChatRequest(message="Test")
        assert request.conversation_id is None
        assert request.profile_id is None
        assert request.workflow_config is None
        assert request.workflow_definition_id is None
        assert request.workflow_template_name is None
        assert request.provider is None
        assert request.model is None
        assert request.temperature is None
        assert request.max_tokens is None
        assert request.context_limit is None
        assert request.document_ids is None
        assert request.prompt_id is None
        assert request.system_prompt_override is None
        # Boolean fields have defaults
        assert request.enable_retrieval is False
        assert request.enable_tools is False
        assert request.enable_memory is True
        assert request.enable_web_search is False
        assert request.enable_tracing is False
