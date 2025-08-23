"""LLM service for LangChain integration."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from chatter.config import settings

# Delayed imports to avoid circular dependencies - moved to module level
from chatter.core.langchain import orchestrator
from chatter.models.conversation import Conversation
from chatter.models.profile import Profile
from chatter.services.mcp import BuiltInTools, mcp_service
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class LLMProviderError(Exception):
    """LLM provider error."""
    pass


class LLMService:
    """Service for LLM interactions using LangChain."""

    def __init__(self):
        """Initialize LLM service."""
        self._providers: dict[str, BaseChatModel] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize available LLM providers."""
        # OpenAI
        if settings.openai_api_key:
            try:
                self._providers["openai"] = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model,
                    temperature=settings.openai_temperature,
                    max_tokens=settings.openai_max_tokens,
                )
                logger.info("OpenAI provider initialized", model=settings.openai_model)
            except Exception as e:
                logger.warning("Failed to initialize OpenAI provider", error=str(e))

        # Anthropic
        if settings.anthropic_api_key:
            try:
                self._providers["anthropic"] = ChatAnthropic(
                    api_key=settings.anthropic_api_key,
                    model=settings.anthropic_model,
                    temperature=settings.anthropic_temperature,
                    max_tokens=settings.anthropic_max_tokens,
                )
                logger.info("Anthropic provider initialized", model=settings.anthropic_model)
            except Exception as e:
                logger.warning("Failed to initialize Anthropic provider", error=str(e))

    def get_provider(self, provider_name: str) -> BaseChatModel:
        """Get LLM provider by name.

        Args:
            provider_name: Provider name

        Returns:
            LLM provider instance

        Raises:
            LLMProviderError: If provider not available
        """
        if provider_name not in self._providers:
            available = list(self._providers.keys())
            raise LLMProviderError(
                f"Provider '{provider_name}' not available. Available providers: {available}"
            )

        return self._providers[provider_name]

    def get_default_provider(self) -> BaseChatModel:
        """Get default LLM provider.

        Returns:
            Default LLM provider

        Raises:
            LLMProviderError: If no providers available
        """
        if not self._providers:
            raise LLMProviderError("No LLM providers available") from None

        # Try to get the configured default provider
        default_provider = settings.default_llm_provider
        if default_provider in self._providers:
            return self._providers[default_provider]

        # Fall back to first available provider
        return next(iter(self._providers.values()))

    def create_provider_from_profile(self, profile: Profile) -> BaseChatModel:
        """Create LLM provider from profile configuration.

        Args:
            profile: Profile with LLM configuration

        Returns:
            Configured LLM provider

        Raises:
            LLMProviderError: If provider cannot be created
        """
        base_provider = self.get_provider(profile.llm_provider)

        # Create a copy with profile-specific settings
        if profile.llm_provider == "openai":
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model=profile.llm_model,
                temperature=profile.temperature,
                max_tokens=profile.max_tokens,
                top_p=profile.top_p,
                presence_penalty=profile.presence_penalty,
                frequency_penalty=profile.frequency_penalty,
                seed=profile.seed,
                stop=profile.stop_sequences,
                logit_bias=profile.logit_bias,
            )
        elif profile.llm_provider == "anthropic":
            return ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model=profile.llm_model,
                temperature=profile.temperature,
                max_tokens=profile.max_tokens,
                top_p=profile.top_p,
                stop_sequences=profile.stop_sequences,
            )
        else:
            # For other providers, use base configuration with parameter updates
            provider = base_provider
            # Note: This is a simplified approach. In a production system,
            # you'd need more sophisticated provider configuration
            return provider

    def convert_conversation_to_messages(
        self,
        conversation: Conversation,
        messages: list[Any]
    ) -> list[BaseMessage]:
        """Convert conversation messages to LangChain format.

        Args:
            conversation: Conversation object
            messages: List of message objects

        Returns:
            List of LangChain messages
        """
        langchain_messages = []

        # Add system message if present
        if conversation.system_prompt:
            langchain_messages.append(SystemMessage(content=conversation.system_prompt))

        # Convert messages
        for message in messages:
            if message.role == "user":
                langchain_messages.append(HumanMessage(content=message.content))
            elif message.role == "assistant":
                langchain_messages.append(AIMessage(content=message.content))
            elif message.role == "system":
                langchain_messages.append(SystemMessage(content=message.content))

        return langchain_messages

    async def generate_response(
        self,
        messages: list[BaseMessage],
        provider: BaseChatModel | None = None,
        **kwargs
    ) -> tuple[str, dict[str, Any]]:
        """Generate response using LLM.

        Args:
            messages: List of LangChain messages
            provider: LLM provider to use
            **kwargs: Additional generation parameters

        Returns:
            Tuple of (response_content, usage_info)
        """
        if provider is None:
            provider = self.get_default_provider()

        start_time = asyncio.get_event_loop().time()

        try:
            # Generate response
            response = await provider.ainvoke(messages, **kwargs)

            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)

            # Extract usage information
            usage_info = {
                "response_time_ms": response_time_ms,
                "model": getattr(provider, "model_name", "unknown"),
                "provider": provider.__class__.__name__.lower().replace("chat", ""),
            }

            # Try to extract token usage if available
            if hasattr(response, "response_metadata"):
                token_usage = response.response_metadata.get("token_usage", {})
                if token_usage:
                    usage_info.update({
                        "prompt_tokens": token_usage.get("prompt_tokens"),
                        "completion_tokens": token_usage.get("completion_tokens"),
                        "total_tokens": token_usage.get("total_tokens"),
                    })

            return response.content, usage_info

        except Exception as e:
            logger.error("LLM generation failed", error=str(e), provider=provider.__class__.__name__)
            raise LLMProviderError(f"Generation failed: {str(e)}")

    async def generate_streaming_response(
        self,
        messages: list[BaseMessage],
        provider: BaseChatModel | None = None,
        **kwargs
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Generate streaming response using LLM.

        Args:
            messages: List of LangChain messages
            provider: LLM provider to use
            **kwargs: Additional generation parameters

        Yields:
            Dictionary with chunk information
        """
        if provider is None:
            provider = self.get_default_provider()

        start_time = asyncio.get_event_loop().time()
        full_content = ""

        try:
            async for chunk in provider.astream(messages, **kwargs):
                if chunk.content:
                    full_content += chunk.content
                    yield {
                        "type": "token",
                        "content": chunk.content,
                    }

            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)

            # Send final usage information
            yield {
                "type": "usage",
                "usage": {
                    "response_time_ms": response_time_ms,
                    "model": getattr(provider, "model_name", "unknown"),
                    "provider": provider.__class__.__name__.lower().replace("chat", ""),
                    "full_content": full_content,
                }
            }

            # Send end marker
            yield {
                "type": "end"
            }

        except Exception as e:
            logger.error("Streaming generation failed", error=str(e), provider=provider.__class__.__name__)
            yield {
                "type": "error",
                "error": str(e)
            }

    def list_available_providers(self) -> list[str]:
        """List available LLM providers.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    def get_provider_info(self, provider_name: str) -> dict[str, Any]:
        """Get information about a provider.

        Args:
            provider_name: Provider name

        Returns:
            Provider information
        """
        if provider_name not in self._providers:
            raise LLMProviderError(f"Provider '{provider_name}' not available") from None

        provider = self._providers[provider_name]

        return {
            "name": provider_name,
            "class": provider.__class__.__name__,
            "model": getattr(provider, "model_name", "unknown"),
            "available": True,
        }

    def create_conversation_chain(
        self,
        provider_name: str,
        system_message: str | None = None,
        include_history: bool = True
    ):
        """Create a conversation chain using LangChain orchestrator."""
        provider = self.get_provider(provider_name)
        return orchestrator.create_chat_chain(
            llm=provider,
            system_message=system_message,
            include_history=include_history
        )

    def create_rag_chain(
        self,
        provider_name: str,
        retriever,
        system_message: str | None = None
    ):
        """Create a RAG chain using LangChain orchestrator."""
        provider = self.get_provider(provider_name)
        return orchestrator.create_rag_chain(
            llm=provider,
            retriever=retriever,
            system_message=system_message
        )

    async def generate_with_tools(
        self,
        messages: list[BaseMessage],
        tools: list[Any] = None,
        provider: BaseChatModel | None = None,
        **kwargs
    ) -> tuple[str, dict[str, Any]]:
        """Generate response with tool calling capabilities."""
        if not provider:
            provider = self.get_default_provider()

        # Get MCP tools if none provided
        if tools is None:
            tools = await mcp_service.get_tools()
            tools.extend(BuiltInTools.create_builtin_tools())

        if tools:
            # Bind tools to the provider
            provider_with_tools = provider.bind_tools(tools)
        else:
            provider_with_tools = provider

        try:
            start_time = asyncio.get_event_loop().time()
            response = await provider_with_tools.ainvoke(messages)
            response_time_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

            usage_info = {
                "response_time_ms": response_time_ms,
                "model": getattr(provider, "model_name", "unknown"),
                "provider": provider.__class__.__name__.lower().replace("chat", ""),
                "tools_available": len(tools) if tools else 0,
            }

            # Try to extract token usage if available
            if hasattr(response, "response_metadata"):
                token_usage = response.response_metadata.get("token_usage", {})
                if token_usage:
                    usage_info.update({
                        "prompt_tokens": token_usage.get("prompt_tokens"),
                        "completion_tokens": token_usage.get("completion_tokens"),
                        "total_tokens": token_usage.get("total_tokens"),
                    })

            return response.content, usage_info

        except Exception as e:
            logger.error("LLM generation with tools failed", error=str(e), provider=provider.__class__.__name__)
            raise LLMProviderError(f"Generation with tools failed: {str(e)}")

    async def create_langgraph_workflow(
        self,
        provider_name: str,
        workflow_type: str = "basic",
        system_message: str | None = None,
        retriever=None,
        tools: list[Any] = None
    ):
        """Create a LangGraph workflow."""
        from chatter.core.langgraph import workflow_manager

        provider = self.get_provider(provider_name)

        if workflow_type == "rag":
            if not retriever:
                raise LLMProviderError("Retriever required for RAG workflow") from None
            return workflow_manager.create_rag_conversation_workflow(
                llm=provider,
                retriever=retriever,
                system_message=system_message
            )
        elif workflow_type == "tools":
            if not tools:
                tools = await mcp_service.get_tools()
                tools.extend(BuiltInTools.create_builtin_tools())
            return workflow_manager.create_tool_calling_workflow(
                llm=provider,
                tools=tools,
                system_message=system_message
            )
        else:  # basic
            return workflow_manager.create_basic_conversation_workflow(
                llm=provider,
                system_message=system_message
            )
