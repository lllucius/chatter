"""Service for managing workflow defaults from profiles, models, and prompts."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.profile import Profile, ProfileType
from chatter.models.registry import ModelDef, Provider
from chatter.models.prompt import Prompt, PromptType
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowDefaultsService:
    """Service for providing workflow defaults from system profiles, models, and prompts."""

    def __init__(self, session: AsyncSession):
        """Initialize the workflow defaults service.
        
        Args:
            session: Database session
        """
        self.session = session
        
        # Cache for defaults to avoid repeated DB queries
        self._defaults_cache: dict[str, Any] = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes

    async def get_default_model_config(
        self, user_id: str | None = None, prefer_profile_type: ProfileType | None = None
    ) -> dict[str, Any]:
        """Get default model configuration from profiles and models.
        
        Args:
            user_id: User ID to get user-specific defaults
            prefer_profile_type: Preferred profile type (e.g., ANALYTICAL, CREATIVE)
            
        Returns:
            Dictionary with default model configuration
        """
        try:
            # Try to get from user's default profile first
            if user_id:
                profile = await self._get_default_profile(user_id, prefer_profile_type)
                if profile:
                    return {
                        'provider': profile.llm_provider,
                        'model': profile.llm_model,
                        'temperature': profile.temperature,
                        'max_tokens': profile.max_tokens,
                        'top_p': profile.top_p or 1.0,
                        'frequency_penalty': profile.frequency_penalty or 0.0,
                        'presence_penalty': profile.presence_penalty or 0.0,
                    }
            
            # Fall back to system default from registry
            return await self._get_system_default_model_config()
            
        except Exception as e:
            logger.error("Failed to get default model config", error=str(e))
            return self._get_hardcoded_fallback_config()

    async def get_default_node_config(
        self, node_type: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """Get default configuration for a specific workflow node type.
        
        Args:
            node_type: Type of workflow node (e.g., 'model', 'retrieval', 'memory')
            user_id: User ID for user-specific defaults
            
        Returns:
            Dictionary with default node configuration
        """
        try:
            if node_type == 'model':
                model_config = await self.get_default_model_config(user_id)
                return {
                    'systemMessage': '',
                    'temperature': model_config['temperature'],
                    'maxTokens': model_config['max_tokens'],
                    'model': model_config['model'],
                    'provider': model_config.get('provider', 'openai'),
                }
            elif node_type == 'retrieval':
                return await self._get_default_retrieval_config()
            elif node_type == 'memory':
                return await self._get_default_memory_config()
            elif node_type == 'loop':
                return {'maxIterations': 10, 'condition': '', 'breakCondition': ''}
            elif node_type == 'conditional':
                return {'condition': '', 'branches': {}}
            elif node_type == 'variable':
                return {
                    'operation': 'set',
                    'variable_name': '',  # Use snake_case to match VariableNode
                    'value': '',
                    'scope': 'workflow',
                }
            elif node_type == 'errorHandler':
                return {'retryCount': 3, 'fallbackAction': 'continue', 'logErrors': True}
            elif node_type == 'delay':
                return {'duration': 1, 'type': 'fixed', 'unit': 'seconds'}
            elif node_type == 'tool':
                return {'tools': [], 'parallel': False}
            elif node_type == 'start':
                return {'isEntryPoint': True}
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get default config for node type {node_type}", error=str(e))
            return {}

    async def get_default_prompt_text(
        self, prompt_type: PromptType = PromptType.SYSTEM, user_id: str | None = None
    ) -> str:
        """Get default prompt text from the prompt system.
        
        Args:
            prompt_type: Type of prompt to get default for
            user_id: User ID for user-specific prompts
            
        Returns:
            Default prompt text
        """
        try:
            query = select(Prompt).where(Prompt.prompt_type == prompt_type)
            
            if user_id:
                # Prefer user's prompts, fall back to public prompts
                query = query.where(
                    (Prompt.owner_id == user_id) | (Prompt.is_public == True)
                ).order_by(Prompt.owner_id == user_id)
            else:
                query = query.where(Prompt.is_public == True)
                
            query = query.order_by(Prompt.created_at.desc()).limit(1)
            
            result = await self.session.execute(query)
            prompt = result.scalar_one_or_none()
            
            return prompt.content if prompt else ""
            
        except Exception as e:
            logger.error("Failed to get default prompt text", error=str(e))
            return ""

    async def _get_default_profile(
        self, user_id: str, prefer_profile_type: ProfileType | None = None
    ) -> Profile | None:
        """Get the user's default profile."""
        try:
            query = select(Profile).where(Profile.owner_id == user_id)
            
            if prefer_profile_type:
                # Try to get preferred profile type first
                preferred_query = query.where(Profile.profile_type == prefer_profile_type)
                result = await self.session.execute(preferred_query.limit(1))
                profile = result.scalar_one_or_none()
                if profile:
                    return profile
            
            # Fall back to any profile for this user
            result = await self.session.execute(query.order_by(Profile.created_at.desc()).limit(1))
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error("Failed to get default profile", error=str(e))
            return None

    async def _get_system_default_model_config(self) -> dict[str, Any]:
        """Get system default model configuration from registry."""
        try:
            # Get default provider and model
            provider_query = select(Provider).where(Provider.is_default == True)
            provider_result = await self.session.execute(provider_query.limit(1))
            provider = provider_result.scalar_one_or_none()
            
            if not provider:
                # Fall back to first available provider
                provider_result = await self.session.execute(select(Provider).limit(1))
                provider = provider_result.scalar_one_or_none()
                
            if provider:
                model_query = select(ModelDef).where(
                    ModelDef.provider_id == provider.id,
                    ModelDef.is_default == True
                )
                model_result = await self.session.execute(model_query.limit(1))
                model = model_result.scalar_one_or_none()
                
                if not model:
                    # Fall back to first model for this provider
                    model_result = await self.session.execute(
                        select(ModelDef).where(ModelDef.provider_id == provider.id).limit(1)
                    )
                    model = model_result.scalar_one_or_none()
                
                if model:
                    config = model.default_config or {}
                    return {
                        'provider': provider.name,
                        'model': model.model_name,
                        'temperature': config.get('temperature', 0.7),
                        'max_tokens': model.max_tokens or config.get('max_tokens', 1000),
                        'top_p': config.get('top_p', 1.0),
                        'frequency_penalty': config.get('frequency_penalty', 0.0),
                        'presence_penalty': config.get('presence_penalty', 0.0),
                    }
            
            return self._get_hardcoded_fallback_config()
            
        except Exception as e:
            logger.error("Failed to get system default model config", error=str(e))
            return self._get_hardcoded_fallback_config()

    async def _get_default_retrieval_config(self) -> dict[str, Any]:
        """Get default retrieval configuration."""
        return {
            'collection': '',
            'topK': 5,
            'threshold': 0.7
        }

    async def _get_default_memory_config(self) -> dict[str, Any]:
        """Get default memory configuration."""
        return {
            'enabled': True,
            'window': 20,
            'memoryType': 'conversation'
        }

    def _get_hardcoded_fallback_config(self) -> dict[str, Any]:
        """Get hardcoded fallback configuration when all else fails."""
        return {
            'provider': 'openai',
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
        }