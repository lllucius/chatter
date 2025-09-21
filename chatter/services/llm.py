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
    get_builtin_tools,
    get_mcp_service,
    get_model_registry,
    get_orchestrator,
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

    async def _create_custom_provider(
        self,
        provider_name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> BaseChatModel:
        """Create a provider instance with custom temperature and max_tokens."""
        session = await self._get_session()
        registry_factory = get_model_registry()
        registry = registry_factory(session)

        # Get the default model if no provider specified
        if provider_name is None:
            try:
                model_def = await registry.get_default_model()
                provider_info = await registry.get_provider(
                    model_def.provider_id
                )
            except Exception:
                # Fallback to OpenAI if registry fails - but still check API key requirements
                provider_name = "openai"
                model_name = "gpt-3.5-turbo"
                try:
                    settings = get_settings()
                    api_key = settings.openai_api_key
                except Exception:
                    api_key = None
                # Don't use dummy API key - fail if no key is available for a fallback
                if not api_key:
                    raise LLMProviderError(
                        "No default model available from registry and no OPENAI_API_KEY found for fallback"
                    ) from None
                return ChatOpenAI(
                    api_key=SecretStr(api_key),
                    model=model_name,
                    temperature=(
                        temperature if temperature is not None else 0.7
                    ),
                    max_completion_tokens=(
                        max_tokens if max_tokens is not None else 2048
                    ),
                )
        else:
            try:
                # Find model by provider name
                models, _ = await registry.list_models()
                model_def = None
                provider_info = None

                for model in models:
                    provider = await registry.get_provider(
                        model.provider_id
                    )
                    if provider.name.lower() == provider_name.lower():
                        model_def = model
                        provider_info = provider
                        break

                if not model_def or not provider_info:
                    raise ValueError(
                        f"Provider {provider_name} not found"
                    )

            except Exception:
                # Fallback creation based on provider name - but respect API key requirements
                if provider_name.lower() == "openai":
                    try:
                        settings = get_settings()
                        api_key = settings.openai_api_key
                    except Exception:
                        api_key = None
                    if not api_key:
                        raise LLMProviderError(
                            f"Provider {provider_name} not found in registry and no OPENAI_API_KEY found for fallback"
                        ) from None
                    return ChatOpenAI(
                        api_key=SecretStr(api_key),
                        model="gpt-3.5-turbo",
                        temperature=(
                            temperature
                            if temperature is not None
                            else 0.7
                        ),
                        max_completion_tokens=(
                            max_tokens
                            if max_tokens is not None
                            else 2048
                        ),
                    )
                elif provider_name.lower() == "anthropic":
                    try:
                        settings = get_settings()
                        api_key = settings.anthropic_api_key
                    except Exception:
                        api_key = None
                    if not api_key:
                        raise LLMProviderError(
                            f"Provider {provider_name} not found in registry and no ANTHROPIC_API_KEY found for fallback"
                        ) from None
                    return ChatAnthropic(
                        api_key=SecretStr(api_key),
                        model_name="claude-3-sonnet-20240229",
                        temperature=(
                            temperature
                            if temperature is not None
                            else 0.7
                        ),
                        max_tokens_to_sample=(
                            max_tokens
                            if max_tokens is not None
                            else 2048
                        ),
                    )
                else:
                    raise ValueError(
                        f"Unsupported provider: {provider_name}"
                    ) from None

        # Create provider instance with custom parameters
        try:
            settings = get_settings()
            if provider_info.name.lower() == "openai":
                api_key = settings.openai_api_key
            elif provider_info.name.lower() == "anthropic":
                api_key = settings.anthropic_api_key
            else:
                api_key = None
        except Exception:
            api_key = None

        if provider_info.api_key_required and not api_key:
            raise LLMProviderError(
                f"API key required for provider {provider_info.name} but not found in settings"
            )

        config = model_def.default_config or {}

        if provider_info.provider_type == ProviderType.OPENAI:
            return ChatOpenAI(
                api_key=SecretStr(api_key) if api_key else None,
                base_url=provider_info.base_url,
                model=model_def.model_name,
                temperature=(
                    temperature
                    if temperature is not None
                    else config.get("temperature", 0.7)
                ),
                max_completion_tokens=(
                    max_tokens
                    if max_tokens is not None
                    else (
                        model_def.max_tokens
                        or config.get("max_tokens", 2048)
                    )
                ),
            )

        elif provider_info.provider_type == ProviderType.ANTHROPIC:
            return ChatAnthropic(
                api_key=SecretStr(api_key) if api_key else None,
                model_name=model_def.model_name,
                temperature=(
                    temperature
                    if temperature is not None
                    else config.get("temperature", 0.7)
                ),
                max_tokens_to_sample=(
                    max_tokens
                    if max_tokens is not None
                    else (
                        model_def.max_tokens
                        or config.get("max_tokens", 2048)
                    )
                ),
                timeout=None,
                stop=None,
            )

        else:
            raise ValueError(
                f"Unsupported provider type: {provider_info.provider_type}"
            )

    async def _create_provider_instance(
        self, provider, model_def
    ) -> BaseChatModel | None:
        """Create a provider instance based on registry data."""
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
                    temperature=config.get("temperature", 0.7),
                    max_completion_tokens=model_def.max_tokens
                    or config.get("max_tokens", 4096),
                )

            elif provider.provider_type == ProviderType.ANTHROPIC:
                return ChatAnthropic(
                    api_key=SecretStr(api_key) if api_key else None,
                    model_name=model_def.model_name,
                    temperature=config.get("temperature", 0.7),
                    max_tokens_to_sample=model_def.max_tokens
                    or config.get("max_tokens", 4096),
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

    def _initialize_providers(self) -> None:
        """Initialize available LLM providers.

        Note: Providers are now loaded dynamically from model registry.
        """
        logger.info(
            "LLM providers will be loaded dynamically from model registry"
        )

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
        # Handle default/null provider
        if (
            not profile.llm_provider
            or profile.llm_provider.lower() == "default"
        ):
            logger.debug(
                "Profile uses default provider, delegating to get_default_provider"
            )
            return await self.get_default_provider()

        # Get the provider configuration from registry
        session = await self._get_session()
        registry = get_model_registry()(session)

        provider = await registry.get_provider_by_name(
            profile.llm_provider
        )
        if not provider:
            logger.warning(
                f"Provider '{profile.llm_provider}' not found, falling back to default"
            )
            return await self.get_default_provider()

        # Get the specific model from the profile or default
        model_def = None
        if profile.llm_model:
            # Find model by name
            models, _ = await registry.list_models(
                provider.id, ModelType.LLM
            )
            for model in models:
                if (
                    model.model_name == profile.llm_model
                    and model.is_active
                ):
                    model_def = model
                    break

        if not model_def:
            # Get default model for provider
            models, _ = await registry.list_models(
                provider.id, ModelType.LLM
            )
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
            logger.warning(
                f"No suitable model found for provider '{profile.llm_provider}', falling back to default"
            )
            return await self.get_default_provider()

        # Create provider instance with profile overrides
        try:
            if provider.provider_type == ProviderType.OPENAI:
                try:
                    settings = get_settings()
                    api_key = settings.openai_api_key
                except Exception:
                    api_key = None
                if provider.api_key_required and not api_key:
                    raise LLMProviderError(
                        f"API key required for provider {provider.name} but not found in settings"
                    )

                return ChatOpenAI(
                    api_key=SecretStr(api_key) if api_key else None,
                    base_url=provider.base_url,
                    model=model_def.model_name,
                    temperature=profile.temperature,
                    max_completion_tokens=profile.max_tokens,
                    top_p=profile.top_p,
                    presence_penalty=profile.presence_penalty,
                    frequency_penalty=profile.frequency_penalty,
                    seed=profile.seed,
                    stop_sequences=profile.stop_sequences,
                    logit_bias=profile.logit_bias,
                )
            elif provider.provider_type == ProviderType.ANTHROPIC:
                try:
                    settings = get_settings()
                    api_key = settings.anthropic_api_key
                except Exception:
                    api_key = None
                if provider.api_key_required and not api_key:
                    raise LLMProviderError(
                        f"API key required for provider {provider.name} but not found in settings"
                    )

                return ChatAnthropic(
                    api_key=SecretStr(api_key) if api_key else None,
                    model_name=model_def.model_name,
                    temperature=profile.temperature,
                    max_tokens_to_sample=profile.max_tokens,
                    top_p=profile.top_p,
                    stop=profile.stop_sequences,
                    timeout=None,
                )
            else:
                raise LLMProviderError(
                    f"Unsupported provider type: {provider.provider_type}"
                )

        except Exception as e:
            raise LLMProviderError(
                f"Failed to create provider from profile: {e}"
            ) from e

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
                langchain_messages.append(HumanMessage(content=content))
            elif role_value == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif role_value == "system":
                langchain_messages.append(
                    SystemMessage(content=content)
                )

        return langchain_messages

    async def generate(
        self,
        messages: list[dict],
        provider: str | None,
        model: str,
        max_retries: int = 1,
        track_cost: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate response using specified provider and model.

        Args:
            messages: List of message dictionaries with role and content
            provider: Provider name (openai, anthropic, etc.) or None for default
            model: Model name
            max_retries: Maximum retry attempts
            track_cost: Whether to track cost information
            **kwargs: Additional parameters

        Returns:
            Response dictionary with content, role, and optionally usage info
        """
        # Convert dict messages to LangChain format
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(
                    SystemMessage(content=content)
                )
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:  # user or any other role
                langchain_messages.append(HumanMessage(content=content))

        # Get provider instance
        try:
            if provider is None or provider == "":
                provider_instance = await self.get_default_provider()
            else:
                provider_instance = await self.get_provider(provider)
        except Exception as e:
            # If provider not found, we should not create fallback instances that bypass
            # registry settings. Instead, raise an appropriate error.
            raise LLMProviderError(
                f"Provider '{provider}' not available. Please ensure the provider is properly configured in the model registry."
            ) from e

        # Generate response with retries
        last_exception = None
        for attempt in range(max_retries):
            try:
                response = await provider_instance.ainvoke(
                    langchain_messages
                )

                result = {
                    "content": response.content,
                    "role": "assistant",
                }

                # Add usage info if available
                if (
                    hasattr(response, "usage_metadata")
                    and response.usage_metadata
                ):
                    result["usage"] = {
                        "input_tokens": response.usage_metadata.get(
                            "input_tokens", 0
                        ),
                        "output_tokens": response.usage_metadata.get(
                            "output_tokens", 0
                        ),
                        "total_tokens": response.usage_metadata.get(
                            "total_tokens", 0
                        ),
                    }

                if track_cost:
                    # Add cost calculation if needed
                    result["cost"] = self._calculate_cost(
                        result.get("usage", {}), provider, model
                    )

                return result

            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying: {e}"
                    )
                    await asyncio.sleep(
                        0.5 * (attempt + 1)
                    )  # Exponential backoff
                else:
                    logger.error(
                        f"All {max_retries} attempts failed: {e}"
                    )

        raise LLMProviderError(
            f"Failed to generate response after {max_retries} attempts: {last_exception}"
        )

    def _calculate_cost(
        self, usage: dict, provider: str, model: str
    ) -> dict:
        """Calculate approximate cost based on usage."""
        # Simplified cost calculation - would need real pricing data
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        # Example pricing (per 1K tokens)
        if provider.lower() == "openai":
            if "gpt-4" in model.lower():
                input_cost = input_tokens * 0.03 / 1000
                output_cost = output_tokens * 0.06 / 1000
            else:  # gpt-3.5-turbo
                input_cost = input_tokens * 0.001 / 1000
                output_cost = output_tokens * 0.002 / 1000
        else:
            # Default pricing
            input_cost = input_tokens * 0.001 / 1000
            output_cost = output_tokens * 0.002 / 1000

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost,
            "currency": "USD",
        }

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

    async def get_provider_info(
        self, provider_name: str
    ) -> dict[str, Any]:
        """Get information about a provider.

        Args:
            provider_name: Provider name

        Returns:
            Provider information
        """
        session = await self._get_session()
        registry = get_model_registry()(session)

        provider = await registry.get_provider_by_name(provider_name)
        if not provider:
            raise LLMProviderError(
                f"Provider '{provider_name}' not found"
            ) from None

        # Get models for this provider
        models, _ = await registry.list_models(
            provider.id, ModelType.LLM
        )
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
        return get_orchestrator().create_chat_chain(
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
        return get_orchestrator().create_rag_chain(
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
            tools = await get_mcp_service().get_tools()
            tools.extend(get_builtin_tools())

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
        provider_name: str | None,
        workflow_type: str = "plain",  # "plain" | "rag" | "tools" | "full"
        system_message: str | None = None,
        retriever=None,
        tools: list[Any] | None = None,
        enable_memory: bool = False,
        memory_window: int = 4,
        max_tool_calls: int | None = None,
        max_documents: int | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        enable_streaming: bool = False,
        focus_mode: bool = False,
    ):
        """Create a LangGraph workflow."""
        from chatter.core.langgraph import workflow_manager

        # Use default provider if none specified, but create with custom parameters if provided
        if provider_name is None or provider_name == "":
            if temperature is not None or max_tokens is not None:
                # Create a custom provider instance with the specified parameters
                provider = await self._create_custom_provider(
                    provider_name=None,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                provider = await self.get_default_provider()
        else:
            if temperature is not None or max_tokens is not None:
                # Create a custom provider instance with the specified parameters
                provider = await self._create_custom_provider(
                    provider_name=provider_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                provider = await self.get_provider(provider_name)

        # Get default tools if needed
        if workflow_type in ("tools", "full") and not tools:
            tools = await get_mcp_service().get_tools()
            tools.extend(get_builtin_tools())

        # Note: do NOT hard-require a retriever; the workflow handles missing retriever gracefully.
        mode = (
            workflow_type
            if workflow_type
            in (
                "plain",
                "rag",
                "tools",
                "full",
            )
            else "plain"
        )

        # Use the unified create_workflow method
        return await workflow_manager.create_workflow(
            llm=provider,
            mode=mode,
            system_message=system_message,
            retriever=retriever if mode in ("rag", "full") else None,
            tools=tools if mode in ("tools", "full") else None,
            enable_memory=enable_memory,
            memory_window=memory_window,
            max_tool_calls=max_tool_calls,
            max_documents=max_documents,
            enable_streaming=enable_streaming,
            focus_mode=focus_mode,
        )

    async def generate_with_fallback(
        self,
        messages: list[dict],
        primary_provider: str,
        fallback_provider: str,
        model: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate response with fallback provider.

        Args:
            messages: List of message dictionaries
            primary_provider: Primary provider to try first
            fallback_provider: Fallback provider if primary fails
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Response with provider_used field
        """
        try:
            result = await self.generate(
                messages, primary_provider, model, **kwargs
            )
            result["provider_used"] = primary_provider
            return result
        except Exception as e:
            logger.warning(
                f"Primary provider {primary_provider} failed: {e}, trying fallback"
            )
            try:
                result = await self.generate(
                    messages, fallback_provider, model, **kwargs
                )
                result["provider_used"] = fallback_provider
                return result
            except Exception as fallback_error:
                raise LLMProviderError(
                    f"Both providers failed. Primary: {e}, Fallback: {fallback_error}"
                ) from fallback_error

    async def generate_with_context(
        self,
        messages: list[dict],
        conversation_id: str,
        provider: str,
        model: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate response with conversation context.

        Args:
            messages: List of message dictionaries
            conversation_id: Conversation ID for context
            provider: Provider name
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        # In a real implementation, this would load context from the conversation
        # For now, just pass through to generate
        result = await self.generate(
            messages, provider, model, **kwargs
        )
        result["conversation_id"] = conversation_id
        return result

    async def generate_with_load_balancing(
        self,
        messages: list[dict],
        providers: list[str],
        model: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate response with load balancing across providers.

        Args:
            messages: List of message dictionaries
            providers: List of provider names to balance across
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Response with provider_used field
        """
        # Simple round-robin load balancing
        # In production, this would use more sophisticated logic
        import random

        provider = random.choice(providers)

        result = await self.generate(
            messages, provider, model, **kwargs
        )
        result["provider_used"] = provider
        return result
