"""LLM service for LangChain integration."""

import asyncio
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
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import get_settings
from chatter.core.dependencies import (
    get_model_registry,
)
from chatter.models.registry import ModelType, ProviderType
from chatter.utils.database import get_session_maker
from chatter.utils.logging import get_logger

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from chatter.models.conversation import Conversation
    from chatter.models.profile import Profile

logger = get_logger(__name__)


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
        session_maker = get_session_maker()
        return session_maker()

    async def _create_provider_instance(
        self, provider, model_def, temperature: float | None = None, max_tokens: int | None = None
    ) -> BaseChatModel | None:
        """Create a provider instance based on registry data with optional custom parameters."""
        try:
            # Get API key from settings - registry doesn't store sensitive data
            try:
                settings = get_settings()
                if provider.name.lower() == "openai":
                    api_key = settings.openai_api_key
                elif provider.name.lower() == "anthropic":
                    api_key = settings.anthropic_api_key
                else:
                    api_key = None
            except Exception:
                api_key = None

            if provider.api_key_required and not api_key:
                logger.warning(
                    f"API key required for provider {provider.name} but not found in settings"
                )
                return None

            config = model_def.default_config or {}

            if provider.provider_type == ProviderType.OPENAI:
                return ChatOpenAI(
                    api_key=SecretStr(api_key) if api_key else None,
                    base_url=provider.base_url,
                    model=model_def.model_name,
                    temperature=temperature if temperature is not None else config.get("temperature", 0.7),
                    max_completion_tokens=max_tokens if max_tokens is not None else (
                        model_def.max_tokens or config.get("max_tokens", 4096)
                    ),
                )

            elif provider.provider_type == ProviderType.ANTHROPIC:
                return ChatAnthropic(
                    api_key=SecretStr(api_key) if api_key else None,
                    model_name=model_def.model_name,
                    temperature=temperature if temperature is not None else config.get("temperature", 0.7),
                    max_tokens_to_sample=max_tokens if max_tokens is not None else (
                        model_def.max_tokens or config.get("max_tokens", 4096)
                    ),
                    timeout=None,
                    stop=None,
                )

            else:
                logger.warning(
                    f"Unsupported provider type: {provider.provider_type}"
                )
                return None

        except Exception as e:
            logger.error(
                f"Failed to create provider instance for {provider.name}: {e}"
            )
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
        registry = get_model_registry()(session)

        # Get provider by name
        provider = await registry.get_provider_by_name(provider_name)
        if not provider or not provider.is_active:
            raise LLMProviderError(
                f"Provider '{provider_name}' not found or inactive"
            )

        # Get default LLM model for this provider
        models, _ = await registry.list_models(
            provider.id, ModelType.LLM
        )
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
            raise LLMProviderError(
                f"No active LLM model found for provider '{provider_name}'"
            )

        # Create provider instance
        instance = await self._create_provider_instance(
            provider, default_model
        )
        if not instance:
            raise LLMProviderError(
                f"Failed to create instance for provider '{provider_name}'"
            )

        # Cache the instance
        self._providers[provider_name] = instance
        logger.info(
            f"Initialized LLM provider: {provider_name} with model: {default_model.model_name}"
        )

        return instance

    async def get_default_provider(self) -> BaseChatModel:
        """Get default LLM provider.

        Returns:
            Default LLM provider

        Raises:
            LLMProviderError: If no providers available
        """
        session = await self._get_session()
        registry = get_model_registry()(session)

        # Get default provider for LLM
        provider = await registry.get_default_provider(ModelType.LLM)
        if not provider:
            raise LLMProviderError("No default LLM provider configured")

        return await self.get_provider(provider.name)











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
        registry = get_model_registry()(session)

        providers, _ = await registry.list_providers()
        active_providers = [p.name for p in providers if p.is_active]

        return active_providers

    async def invalidate_provider_cache(
        self, provider_name: str | None = None
    ) -> None:
        """Invalidate cached LLM provider instances.

        This should be called when providers or models are updated/deleted
        to ensure the cache doesn't serve stale data.

        Args:
            provider_name: Specific provider to invalidate, or None to invalidate all
        """
        if provider_name:
            # Invalidate specific provider
            if provider_name in self._providers:
                del self._providers[provider_name]
                logger.debug(
                    "Invalidated LLM provider cache",
                    provider_name=provider_name,
                )
        else:
            # Invalidate all cached providers
            if self._providers:
                provider_count = len(self._providers)
                self._providers.clear()
                logger.info(
                    "Invalidated all LLM provider caches",
                    provider_count=provider_count,
                )





    async def _create_provider_with_custom_params(
        self,
        provider_name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> BaseChatModel:
        """Create a provider with custom parameters."""
        session = await self._get_session()
        registry = get_model_registry()(session)

        if provider_name is None:
            # Get default provider
            provider_info = await registry.get_default_provider(ModelType.LLM)
            if not provider_info:
                raise LLMProviderError("No default LLM provider configured")
            provider_name = provider_info.name

        # Get provider and model info
        provider = await registry.get_provider_by_name(provider_name)
        if not provider or not provider.is_active:
            raise LLMProviderError(
                f"Provider '{provider_name}' not found or inactive"
            )

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
            raise LLMProviderError(
                f"No active LLM model found for provider '{provider_name}'"
            )

        # Create instance with custom parameters
        instance = await self._create_provider_instance(
            provider, default_model, temperature, max_tokens
        )
        if not instance:
            raise LLMProviderError(
                f"Failed to create instance for provider '{provider_name}'"
            )

        return instance








