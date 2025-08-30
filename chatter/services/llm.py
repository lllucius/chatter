"""LLM service for LangChain integration."""

import asyncio
import os
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.registry import ModelType, ProviderType
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from chatter.models.conversation import Conversation
    from chatter.models.profile import Profile

logger = get_logger(__name__)


def _get_builtin_tools():
    """Lazy import of BuiltInTools to avoid circular imports."""
    from chatter.services.mcp import BuiltInTools
    return BuiltInTools.create_builtin_tools()


def _get_orchestrator():
    """Lazy import of orchestrator to avoid circular imports."""
    from chatter.core.langchain import orchestrator
    return orchestrator


def _get_mcp_service():
    """Lazy import of MCP service to avoid circular imports."""
    from chatter.services.mcp import mcp_service
    return mcp_service


def _get_model_registry():
    """Lazy import of model registry to avoid circular imports."""
    from chatter.core.model_registry import ModelRegistryService
    return ModelRegistryService


class LLMProviderError(Exception):
    """LLM provider error."""

    pass


class LLMService:
    """Service for LLM interactions using LangChain."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize LLM service."""
        self._session = session
        self._providers: dict[str, BaseChatModel] = {}
        # We'll load providers dynamically as needed

    async def _get_session(self) -> AsyncSession:
        """Get database session."""
        if self._session:
            return self._session
        async for session in get_session():
            return session

    async def _create_provider_instance(self, provider, model_def) -> BaseChatModel | None:
        """Create a provider instance based on registry data."""
        try:
            # Get API key from environment - registry doesn't store sensitive data
            api_key = os.getenv(f"{provider.name.upper()}_API_KEY")
            if provider.api_key_required and not api_key:
                logger.warning(f"No API key found for provider {provider.name}")
                return None

            config = model_def.default_config or {}

            if provider.provider_type == ProviderType.OPENAI:
                return ChatOpenAI(
                    api_key=api_key or "dummy",
                    base_url=provider.base_url,
                    model=model_def.model_name,
                    temperature=config.get('temperature', 0.7),
                    max_tokens=model_def.max_tokens or config.get('max_tokens', 4096),
                )

            elif provider.provider_type == ProviderType.ANTHROPIC:
                return ChatAnthropic(
                    api_key=api_key or "dummy",
                    model=model_def.model_name,
                    temperature=config.get('temperature', 0.7),
                    max_tokens=model_def.max_tokens or config.get('max_tokens', 4096),
                )

            else:
                logger.warning(f"Unsupported provider type: {provider.provider_type}")
                return None

        except Exception as e:
            logger.error(f"Failed to create provider instance for {provider.name}: {e}")
            return None

    async def get_provider(self, provider_name: str) -> BaseChatModel:
        """Get LLM provider by name.

        Args:
            provider_name: Provider name

        Returns:
            LLM provider instance

        Raises:
            LLMProviderError: If provider not available
        """
        # Check if we already have this provider cached
        if provider_name in self._providers:
            return self._providers[provider_name]

        # Load from registry
        session = await self._get_session()
        registry = _get_model_registry()(session)

        # Get provider by name
        provider = await registry.get_provider_by_name(provider_name)
        if not provider or not provider.is_active:
            raise LLMProviderError(f"Provider '{provider_name}' not found or inactive")

        # Get default LLM model for this provider
        models, _ = await registry.list_models(provider.id, ModelType.LLM)
        default_model = None
        for model in models:
            if model.is_default and model.is_active:
                default_model = model
                break

        if not default_model:
            # Get first active model if no default
            for model in models:
                if model.is_active:
                    default_model = model
                    break

        if not default_model:
            raise LLMProviderError(f"No active LLM model found for provider '{provider_name}'")

        # Create provider instance
        instance = await self._create_provider_instance(provider, default_model)
        if not instance:
            raise LLMProviderError(f"Failed to create instance for provider '{provider_name}'")

        # Cache the instance
        self._providers[provider_name] = instance
        logger.info(f"Initialized LLM provider: {provider_name} with model: {default_model.model_name}")

        return instance

    async def get_default_provider(self) -> BaseChatModel:
        """Get default LLM provider.

        Returns:
            Default LLM provider

        Raises:
            LLMProviderError: If no providers available
        """
        session = await self._get_session()
        registry = _get_model_registry()(session)

        # Get default provider for LLM
        provider = await registry.get_default_provider(ModelType.LLM)
        if not provider:
            raise LLMProviderError("No default LLM provider configured")

        return await self.get_provider(provider.name)

    def _initialize_providers(self) -> None:
        """Initialize available LLM providers.

        Note: This is kept for backward compatibility but providers are now loaded dynamically.
        """
        logger.info("LLM providers will be loaded dynamically from model registry")

    async def create_provider_from_profile(
        self, profile: "Profile"
    ) -> BaseChatModel:
        """Create LLM provider from profile configuration.

        Args:
            profile: Profile with LLM configuration

        Returns:
            Configured LLM provider

        Raises:
            LLMProviderError: If provider cannot be created
        """
        # Get the provider configuration from registry
        session = await self._get_session()
        registry = _get_model_registry()(session)

        provider = await registry.get_provider_by_name(profile.llm_provider)
        if not provider:
            raise LLMProviderError(f"Provider '{profile.llm_provider}' not found in registry")

        # Get the specific model from the profile or default
        model_def = None
        if profile.llm_model:
            # Find model by name
            models, _ = await registry.list_models(provider.id, ModelType.LLM)
            for model in models:
                if model.model_name == profile.llm_model and model.is_active:
                    model_def = model
                    break

        if not model_def:
            # Get default model for provider
            models, _ = await registry.list_models(provider.id, ModelType.LLM)
            for model in models:
                if model.is_default and model.is_active:
                    model_def = model
                    break

            if not model_def and models:
                # Get first active model
                for model in models:
                    if model.is_active:
                        model_def = model
                        break

        if not model_def:
            raise LLMProviderError(f"No suitable model found for provider '{profile.llm_provider}'")

        # Create provider instance with profile overrides
        try:
            if provider.provider_type == ProviderType.OPENAI:
                api_key = os.getenv(f"{provider.name.upper()}_API_KEY")
                if provider.api_key_required and not api_key:
                    raise LLMProviderError(f"No API key found for provider {provider.name}")

                # Only create provider if we have an API key or if it's not required
                if api_key or not provider.api_key_required:
                    return ChatOpenAI(
                        api_key=api_key,
                        base_url=provider.base_url,
                        model=model_def.model_name,
                        temperature=profile.temperature,
                        max_tokens=profile.max_tokens,
                        top_p=profile.top_p,
                        presence_penalty=profile.presence_penalty,
                        frequency_penalty=profile.frequency_penalty,
                        seed=profile.seed,
                        stop=profile.stop_sequences,
                        logit_bias=profile.logit_bias,
                    )
                else:
                    raise LLMProviderError(f"Cannot create OpenAI provider {provider.name}: API key required but not provided")
            elif provider.provider_type == ProviderType.ANTHROPIC:
                api_key = os.getenv(f"{provider.name.upper()}_API_KEY")
                if provider.api_key_required and not api_key:
                    raise LLMProviderError(f"No API key found for provider {provider.name}")

                # Only create provider if we have an API key or if it's not required
                if api_key or not provider.api_key_required:
                    return ChatAnthropic(
                        api_key=api_key,
                        model=model_def.model_name,
                        temperature=profile.temperature,
                        max_tokens=profile.max_tokens,
                        top_p=profile.top_p,
                        stop_sequences=profile.stop_sequences,
                    )
                else:
                    raise LLMProviderError(f"Cannot create Anthropic provider {provider.name}: API key required but not provided")
            else:
                raise LLMProviderError(f"Unsupported provider type: {provider.provider_type}")

        except Exception as e:
            raise LLMProviderError(f"Failed to create provider from profile: {e}") from e
            # For other providers, use base configuration with parameter updates
            provider = base_provider
            # Note: This is a simplified approach. In a production system,
            # you'd need more sophisticated provider configuration
            return provider

    def convert_conversation_to_messages(
        self, conversation: "Conversation", messages: list[Any]
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
        if getattr(conversation, "system_prompt", None):
            langchain_messages.append(
                SystemMessage(content=conversation.system_prompt)
            )

        # Convert messages
        for message in messages:
            role_value = getattr(message, "role", None)
            content = getattr(message, "content", "")
            if role_value == "user":
                langchain_messages.append(
                    HumanMessage(content=content)
                )
            elif role_value == "assistant":
                langchain_messages.append(
                    AIMessage(content=content)
                )
            elif role_value == "system":
                langchain_messages.append(
                    SystemMessage(content=content)
                )

        return langchain_messages

    async def generate_response(
        self,
        messages: list[BaseMessage],
        provider: BaseChatModel | None = None,
        **kwargs,
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
            provider = await self.get_default_provider()

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
                "provider": provider.__class__.__name__.lower().replace(
                    "chat", ""
                ),
            }

            # Try to extract token usage if available
            if hasattr(response, "response_metadata"):
                token_usage = response.response_metadata.get(
                    "token_usage", {}
                )
                if token_usage:
                    usage_info.update(
                        {
                            "prompt_tokens": token_usage.get(
                                "prompt_tokens"
                            ),
                            "completion_tokens": token_usage.get(
                                "completion_tokens"
                            ),
                            "total_tokens": token_usage.get(
                                "total_tokens"
                            ),
                        }
                    )

            return response.content, usage_info

        except Exception as e:
            logger.error(
                "LLM generation failed",
                error=str(e),
                provider=provider.__class__.__name__,
            )
            raise LLMProviderError(
                f"Generation failed: {str(e)}"
            ) from e

    async def generate_streaming_response(
        self,
        messages: list[BaseMessage],
        provider: BaseChatModel | None = None,
        **kwargs,
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
            provider = await self.get_default_provider()

        start_time = asyncio.get_event_loop().time()
        full_content = ""

        try:
            async for chunk in provider.astream(messages, **kwargs):
                if getattr(chunk, "content", None):
                    full_content += chunk.content
                    yield {
                        "type": "token",
                        "content": chunk.content,
                    }

            response_time_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000
            )

            # Send final usage information
            yield {
                "type": "usage",
                "usage": {
                    "response_time_ms": response_time_ms,
                    "model": getattr(provider, "model_name", "unknown"),
                    "provider": provider.__class__.__name__.lower().replace(
                        "chat", ""
                    ),
                    "full_content": full_content,
                },
            }

            # Send end marker
            yield {"type": "end"}

        except Exception as e:
            logger.error(
                "Streaming generation failed",
                error=str(e),
                provider=provider.__class__.__name__,
            )
            yield {"type": "error", "error": str(e)}

    async def list_available_providers(self) -> list[str]:
        """List available LLM providers.

        Returns:
            List of provider names
        """
        session = await self._get_session()
        registry = _get_model_registry()(session)

        providers, _ = await registry.list_providers()
        active_providers = [p.name for p in providers if p.is_active]

        return active_providers

    async def get_provider_info(self, provider_name: str) -> dict[str, Any]:
        """Get information about a provider.

        Args:
            provider_name: Provider name

        Returns:
            Provider information
        """
        session = await self._get_session()
        registry = _get_model_registry()(session)

        provider = await registry.get_provider_by_name(provider_name)
        if not provider:
            raise LLMProviderError(f"Provider '{provider_name}' not found") from None

        # Get models for this provider
        models, _ = await registry.list_models(provider.id, ModelType.LLM)
        active_models = [m for m in models if m.is_active]

        return {
            "name": provider.name,
            "display_name": provider.display_name,
            "provider_type": provider.provider_type,
            "description": provider.description,
            "is_active": provider.is_active,
            "is_default": provider.is_default,
            "models": [
                {
                    "name": m.name,
                    "model_name": m.model_name,
                    "display_name": m.display_name,
                    "is_default": m.is_default,
                    "max_tokens": m.max_tokens,
                }
                for m in active_models
            ],
        }

    async def create_conversation_chain(
        self,
        provider_name: str,
        system_message: str | None = None,
        include_history: bool = True,
    ) -> Any:
        """Create a conversation chain using LangChain orchestrator."""
        provider = await self.get_provider(provider_name)
        return _get_orchestrator().create_chat_chain(
            llm=provider,
            system_message=system_message,
            include_history=include_history,
        )

    async def create_rag_chain(
        self,
        provider_name: str,
        retriever: Any,
        system_message: str | None = None,
    ) -> Any:
        """Create a RAG chain using LangChain orchestrator."""
        provider = await self.get_provider(provider_name)
        return _get_orchestrator().create_rag_chain(
            llm=provider,
            retriever=retriever,
            system_message=system_message,
        )

    async def generate_with_tools(
        self,
        messages: list[BaseMessage],
        tools: list[Any] = None,
        provider: BaseChatModel | None = None,
        **kwargs,
    ) -> tuple[str, dict[str, Any]]:
        """Generate response with tool calling capabilities."""
        if not provider:
            provider = await self.get_default_provider()

        # Get MCP tools if none provided
        if tools is None:
            tools = await _get_mcp_service().get_tools()
            tools.extend(_get_builtin_tools())

        if tools:
            # Bind tools to the provider
            provider_with_tools = provider.bind_tools(tools)
        else:
            provider_with_tools = provider

        try:
            start_time = asyncio.get_event_loop().time()
            response = await provider_with_tools.ainvoke(messages)
            response_time_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000
            )

            usage_info = {
                "response_time_ms": response_time_ms,
                "model": getattr(provider, "model_name", "unknown"),
                "provider": provider.__class__.__name__.lower().replace(
                    "chat", ""
                ),
                "tools_available": len(tools) if tools else 0,
            }

            # Try to extract token usage if available
            if hasattr(response, "response_metadata"):
                token_usage = response.response_metadata.get(
                    "token_usage", {}
                )
                if token_usage:
                    usage_info.update(
                        {
                            "prompt_tokens": token_usage.get(
                                "prompt_tokens"
                            ),
                            "completion_tokens": token_usage.get(
                                "completion_tokens"
                            ),
                            "total_tokens": token_usage.get(
                                "total_tokens"
                            ),
                        }
                    )

            return response.content, usage_info

        except Exception as e:
            logger.error(
                "LLM generation with tools failed",
                error=str(e),
                provider=provider.__class__.__name__,
            )
            raise LLMProviderError(
                f"Generation with tools failed: {str(e)}"
            ) from e

    async def create_langgraph_workflow(
        self,
        provider_name: str,
        workflow_type: str = "plain",  # "plain" | "rag" | "tools" | "full"
        system_message: str | None = None,
        retriever=None,
        tools: list[Any] | None = None,
        enable_memory: bool = False,
        memory_window: int = 20,
    ):
        """Create a LangGraph workflow."""
        from chatter.core.langgraph import workflow_manager

        provider = await self.get_provider(provider_name)

        # Get default tools if needed
        if workflow_type in ("tools", "full") and not tools:
            tools = await _get_mcp_service().get_tools()
            tools.extend(_get_builtin_tools())

        # Note: do NOT hard-require a retriever; the workflow handles missing retriever gracefully.
        mode = (
            workflow_type
            if workflow_type in ("plain", "rag", "tools", "full")
            else "plain"
        )

        # Use the unified create_workflow method
        return workflow_manager.create_workflow(
            llm=provider,
            mode=mode,
            system_message=system_message,
            retriever=retriever if mode in ("rag", "full") else None,
            tools=tools if mode in ("tools", "full") else None,
            enable_memory=enable_memory,
            memory_window=memory_window,
        )
