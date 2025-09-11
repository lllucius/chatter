"""Profile management service."""

import time
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.models.profile import Profile, ProfileType
from chatter.schemas.profile import (
    ProfileCreate,
    ProfileListRequest,
    ProfileTestRequest,
    ProfileUpdate,
)
from chatter.services.llm import LLMService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ProfileService:
    """Service for profile management operations."""

    # Cache for expensive provider lookups (TTL: 10 minutes)
    _provider_cache = {}
    _provider_cache_timestamp = 0
    _provider_cache_ttl = 600  # 10 minutes

    def __init__(self, session: AsyncSession):
        """Initialize profile service.

        Args:
            session: Database session
        """
        self.session = session
        self.llm_service = LLMService()

    async def create_profile(
        self, user_id: str, profile_data: ProfileCreate
    ) -> Profile:
        """Create a new profile.

        Args:
            user_id: Owner user ID
            profile_data: Profile creation data

        Returns:
            Created profile

        Raises:
            ProfileError: If profile creation fails
        """
        try:
            # Check for duplicate profile names for this user
            existing_result = await self.session.execute(
                select(Profile).where(
                    and_(
                        Profile.owner_id == user_id,
                        Profile.name == profile_data.name,
                    )
                )
            )
            existing_profile = existing_result.scalar_one_or_none()

            if existing_profile:
                raise ProfileError(
                    "Profile with this name already exists"
                ) from None

            # Validate LLM provider against available providers
            try:
                available_providers_info = (
                    await self.get_available_providers()
                )
                available_providers = available_providers_info.get(
                    "providers", {}
                )

                if profile_data.llm_provider not in available_providers:
                    logger.warning(
                        "LLM provider not available",
                        provider=profile_data.llm_provider,
                        available_providers=list(
                            available_providers.keys()
                        ),
                    )
                    raise ProfileError(
                        f"LLM provider '{profile_data.llm_provider}' is not available. "
                        f"Available providers: {', '.join(available_providers.keys())}"
                    ) from None

                # Validate model against provider's available models
                provider_info = available_providers[
                    profile_data.llm_provider
                ]
                available_models = provider_info.get("models", [])
                if (
                    available_models
                    and profile_data.llm_model not in available_models
                ):
                    logger.warning(
                        "LLM model not available for provider",
                        provider=profile_data.llm_provider,
                        model=profile_data.llm_model,
                        available_models=available_models,
                    )
                    raise ProfileError(
                        f"Model '{profile_data.llm_model}' is not available for provider '{profile_data.llm_provider}'. "
                        f"Available models: {', '.join(available_models)}"
                    ) from None

            except ProfileError:
                raise
            except Exception as e:
                logger.warning(
                    "Could not validate provider/model availability",
                    error=str(e),
                    provider=profile_data.llm_provider,
                    model=profile_data.llm_model,
                )
                # Continue with creation but log the issue

            # Create profile
            profile = Profile(
                owner_id=user_id, **profile_data.model_dump()
            )

            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)

            logger.info(
                "Profile created",
                profile_id=profile.id,
                name=profile.name,
                user_id=user_id,
                llm_provider=profile.llm_provider,
                llm_model=profile.llm_model,
            )

            return profile

        except ProfileError:
            raise
        except Exception as e:
            logger.error("Profile creation failed", error=str(e))
            raise ProfileError(
                f"Failed to create profile: {str(e)}"
            ) from e

    async def get_profile(
        self, profile_id: str, user_id: str
    ) -> Profile | None:
        """Get profile by ID with access control.

        Args:
            profile_id: Profile ID
            user_id: Requesting user ID

        Returns:
            Profile if found and accessible, None otherwise
        """
        try:
            result = await self.session.execute(
                select(Profile).where(
                    and_(
                        Profile.id == profile_id,
                        or_(
                            Profile.owner_id == user_id,
                            Profile.is_public is True,
                        ),
                    )
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                "Failed to get profile",
                profile_id=profile_id,
                error=str(e),
            )
            return None

    async def list_profiles(
        self, user_id: str, list_request: ProfileListRequest
    ) -> tuple[list[Profile], int]:
        """List profiles with filtering and pagination.

        Args:
            user_id: Requesting user ID
            list_request: List request parameters

        Returns:
            Tuple of (profiles list, total count)
        """
        try:
            # Build base query with access control
            query = select(Profile).where(
                or_(
                    Profile.owner_id == user_id,
                    Profile.is_public is True,
                )
            )

            # Add filters
            if list_request.profile_type:
                query = query.where(
                    Profile.profile_type == list_request.profile_type
                )

            if list_request.llm_provider:
                query = query.where(
                    Profile.llm_provider == list_request.llm_provider
                )

            if list_request.tags:
                # Use JSON operators for efficient tag filtering
                for tag in list_request.tags:
                    query = query.where(Profile.tags.contains([tag]))

            if list_request.is_public is not None:
                query = query.where(
                    Profile.is_public == list_request.is_public
                )

            # Get total count efficiently - use the same query without ordering/pagination
            count_query = select(func.count()).select_from(
                query.subquery()
            )
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()

            # Add sorting with proper column references
            sort_column = getattr(
                Profile, list_request.sort_by, Profile.created_at
            )
            if list_request.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Add pagination
            query = query.offset(list_request.offset).limit(
                list_request.limit
            )

            # Execute query
            result = await self.session.execute(query)
            profiles = result.scalars().all()

            logger.debug(
                "Listed profiles",
                user_id=user_id,
                total_count=total_count,
                returned_count=len(profiles),
                filters={
                    "profile_type": list_request.profile_type,
                    "llm_provider": list_request.llm_provider,
                    "tags": list_request.tags,
                    "is_public": list_request.is_public,
                },
            )

            return list(profiles), total_count

        except Exception as e:
            logger.error("Failed to list profiles", error=str(e))
            return [], 0

    async def update_profile(
        self, profile_id: str, user_id: str, update_data: ProfileUpdate
    ) -> Profile | None:
        """Update profile.

        Args:
            profile_id: Profile ID
            user_id: Requesting user ID
            update_data: Update data

        Returns:
            Updated profile if successful, None otherwise
        """
        try:
            # Get profile with ownership check
            result = await self.session.execute(
                select(Profile).where(
                    and_(
                        Profile.id == profile_id,
                        Profile.owner_id == user_id,
                    )
                )
            )
            profile = result.scalar_one_or_none()

            if not profile:
                return None

            # Check for name conflicts if name is being updated
            if update_data.name and update_data.name != profile.name:
                existing_result = await self.session.execute(
                    select(Profile).where(
                        and_(
                            Profile.owner_id == user_id,
                            Profile.name == update_data.name,
                            Profile.id != profile_id,
                        )
                    )
                )
                existing_profile = existing_result.scalar_one_or_none()

                if existing_profile:
                    raise ProfileError(
                        "Profile with this name already exists"
                    ) from None

            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(profile, field, value)

            await self.session.commit()
            await self.session.refresh(profile)

            logger.info(
                "Profile updated",
                profile_id=profile_id,
                user_id=user_id,
            )
            return profile

        except ProfileError:
            raise
        except Exception as e:
            logger.error(
                "Failed to update profile",
                profile_id=profile_id,
                error=str(e),
            )
            raise ProfileError(
                f"Failed to update profile: {str(e)}"
            ) from e

    async def delete_profile(
        self, profile_id: str, user_id: str
    ) -> bool:
        """Delete profile.

        Args:
            profile_id: Profile ID
            user_id: Requesting user ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get profile with ownership check
            result = await self.session.execute(
                select(Profile).where(
                    and_(
                        Profile.id == profile_id,
                        Profile.owner_id == user_id,
                    )
                )
            )
            profile = result.scalar_one_or_none()

            if not profile:
                return False

            # Check if profile is in use by conversations
            # This would require checking conversations table if we want to prevent deletion
            # For now, we'll allow deletion and let foreign key constraints handle it

            await self.session.delete(profile)
            await self.session.commit()

            logger.info(
                "Profile deleted",
                profile_id=profile_id,
                user_id=user_id,
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to delete profile",
                profile_id=profile_id,
                error=str(e),
            )
            return False

    async def test_profile(
        self,
        profile_id: str,
        user_id: str,
        test_request: ProfileTestRequest,
    ) -> dict[str, Any]:
        """Test profile with a sample message.

        Args:
            profile_id: Profile ID
            user_id: Requesting user ID
            test_request: Test request parameters

        Returns:
            Test results
        """
        try:
            # Get profile
            profile = await self.get_profile(profile_id, user_id)
            if not profile:
                raise ProfileError("Profile not found") from None

            # Create LLM provider from profile
            provider = self.llm_service.create_provider_from_profile(
                profile
            )
            if not provider:
                raise ProfileError(
                    "Failed to create LLM provider from profile"
                ) from None

            # Prepare messages
            from langchain_core.messages import (
                HumanMessage,
                SystemMessage,
            )

            messages = []
            if profile.system_prompt:
                messages.append(
                    SystemMessage(content=profile.system_prompt)
                )
            messages.append(
                HumanMessage(content=test_request.test_message)
            )

            # Generate response
            start_time = datetime.now(UTC)

            generation_config = profile.get_generation_config()
            (
                response_content,
                usage_info,
            ) = await self.llm_service.generate_response(
                messages, provider, **generation_config
            )

            end_time = datetime.now(UTC)
            response_time_ms = int(
                (end_time - start_time).total_seconds() * 1000
            )

            # Update profile usage stats
            profile.usage_count += 1
            if usage_info.get("total_tokens"):
                profile.total_tokens_used += usage_info["total_tokens"]
            if usage_info.get("cost"):
                profile.total_cost += usage_info["cost"]
            profile.last_used_at = datetime.now(UTC)

            await self.session.commit()
            await self.session.refresh(profile)

            result = {
                "profile_id": profile_id,
                "test_message": test_request.test_message,
                "response": response_content,
                "usage_info": usage_info,
                "response_time_ms": response_time_ms,
            }

            # Add retrieval results if enabled
            if (
                test_request.include_retrieval
                and profile.enable_retrieval
            ):
                # In a test mode, indicate that retrieval would be performed
                # In production, this would integrate with the document service
                result["retrieval_results"] = (
                    [
                        {
                            "document_id": "test_doc_1",
                            "chunk_text": f"This is simulated retrieval content for test message: {test_request.test_message[:50]}...",
                            "similarity_score": 0.85,
                            "metadata": {
                                "source": "test_document",
                                "page": 1,
                            },
                        }
                    ]
                    if test_request.test_message
                    else []
                )

            # Add tools used if enabled
            if test_request.include_tools and profile.enable_tools:
                # In a test mode, indicate that tools would be used
                # In production, this would integrate with MCP service for tool calling
                result["tools_used"] = (
                    [
                        {
                            "tool_name": "search_tool",
                            "description": "Would search knowledge base",
                            "parameters": {
                                "query": test_request.test_message
                            },
                            "status": "simulated",
                        }
                    ]
                    if test_request.test_message
                    else []
                )

            logger.info(
                "Profile test completed",
                profile_id=profile_id,
                response_time_ms=response_time_ms,
                tokens_used=usage_info.get("total_tokens", 0),
            )

            return result

        except ProfileError:
            raise
        except Exception as e:
            logger.error(
                "Profile test failed",
                profile_id=profile_id,
                error=str(e),
            )
            raise ProfileError(f"Profile test failed: {str(e)}") from e

    async def clone_profile(
        self,
        profile_id: str,
        user_id: str,
        new_name: str,
        description: str | None = None,
        modifications: ProfileUpdate | None = None,
    ) -> Profile:
        """Clone an existing profile.

        Args:
            profile_id: Source profile ID
            user_id: Requesting user ID
            new_name: Name for the cloned profile
            description: Description for the cloned profile
            modifications: Modifications to apply to the cloned profile

        Returns:
            Cloned profile
        """
        try:
            # Get source profile
            source_profile = await self.get_profile(profile_id, user_id)
            if not source_profile:
                raise ProfileError("Source profile not found") from None

            # Check for name conflicts
            existing_result = await self.session.execute(
                select(Profile).where(
                    and_(
                        Profile.owner_id == user_id,
                        Profile.name == new_name,
                    )
                )
            )
            existing_profile = existing_result.scalar_one_or_none()

            if existing_profile:
                raise ProfileError(
                    "Profile with this name already exists"
                ) from None

            # Create profile data from source
            profile_data = ProfileCreate(
                name=new_name,
                description=description
                or f"Cloned from {source_profile.name}",
                profile_type=source_profile.profile_type,
                llm_provider=source_profile.llm_provider,
                llm_model=source_profile.llm_model,
                temperature=source_profile.temperature,
                top_p=source_profile.top_p,
                top_k=source_profile.top_k,
                max_tokens=source_profile.max_tokens,
                presence_penalty=source_profile.presence_penalty,
                frequency_penalty=source_profile.frequency_penalty,
                context_window=source_profile.context_window,
                system_prompt=source_profile.system_prompt,
                memory_enabled=source_profile.memory_enabled,
                memory_strategy=source_profile.memory_strategy,
                enable_retrieval=source_profile.enable_retrieval,
                retrieval_limit=source_profile.retrieval_limit,
                retrieval_score_threshold=source_profile.retrieval_score_threshold,
                enable_tools=source_profile.enable_tools,
                available_tools=source_profile.available_tools,
                tool_choice=source_profile.tool_choice,
                content_filter_enabled=source_profile.content_filter_enabled,
                safety_level=source_profile.safety_level,
                response_format=source_profile.response_format,
                stream_response=source_profile.stream_response,
                seed=source_profile.seed,
                stop_sequences=source_profile.stop_sequences,
                logit_bias=source_profile.logit_bias,
                embedding_provider=source_profile.embedding_provider,
                embedding_model=source_profile.embedding_model,
                is_public=False,  # Cloned profiles are private by default
                tags=(
                    source_profile.tags.copy()
                    if source_profile.tags
                    else None
                ),
                extra_metadata=(
                    source_profile.extra_metadata.copy()
                    if source_profile.extra_metadata
                    else None
                ),
            )

            # Apply modifications if provided
            if modifications:
                modification_dict = modifications.model_dump(
                    exclude_unset=True
                )
                for field, value in modification_dict.items():
                    setattr(profile_data, field, value)

            # Create the cloned profile
            cloned_profile = await self.create_profile(
                user_id, profile_data
            )

            logger.info(
                "Profile cloned",
                source_profile_id=profile_id,
                cloned_profile_id=cloned_profile.id,
                user_id=user_id,
            )

            return cloned_profile

        except ProfileError:
            raise
        except Exception as e:
            logger.error(
                "Profile cloning failed",
                profile_id=profile_id,
                error=str(e),
            )
            raise ProfileError(
                f"Failed to clone profile: {str(e)}"
            ) from e

    async def get_profile_stats(self, user_id: str) -> dict[str, Any]:
        """Get profile statistics for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with profile statistics
        """
        try:
            # Count profiles by type
            type_counts = {}
            for profile_type in ProfileType:
                result = await self.session.execute(
                    select(func.count(Profile.id)).where(
                        and_(
                            Profile.owner_id == user_id,
                            Profile.profile_type == profile_type,
                        )
                    )
                )
                type_counts[profile_type.value] = result.scalar()

            # Count profiles by provider
            provider_result = await self.session.execute(
                select(Profile.llm_provider, func.count(Profile.id))
                .where(Profile.owner_id == user_id)
                .group_by(Profile.llm_provider)
            )
            provider_counts = dict(provider_result.all())

            # Get most used profiles
            most_used_result = await self.session.execute(
                select(Profile)
                .where(Profile.owner_id == user_id)
                .order_by(desc(Profile.usage_count))
                .limit(5)
            )
            most_used_profiles = most_used_result.scalars().all()

            # Get recent profiles
            recent_result = await self.session.execute(
                select(Profile)
                .where(Profile.owner_id == user_id)
                .order_by(desc(Profile.created_at))
                .limit(5)
            )
            recent_profiles = recent_result.scalars().all()

            # Get usage totals
            usage_result = await self.session.execute(
                select(
                    func.sum(Profile.usage_count),
                    func.sum(Profile.total_tokens_used),
                    func.sum(Profile.total_cost),
                ).where(Profile.owner_id == user_id)
            )
            total_usage, total_tokens, total_cost = usage_result.first()

            return {
                "total_profiles": sum(type_counts.values()),
                "profiles_by_type": type_counts,
                "profiles_by_provider": provider_counts,
                "most_used_profiles": [
                    profile.to_dict() for profile in most_used_profiles
                ],
                "recent_profiles": [
                    profile.to_dict() for profile in recent_profiles
                ],
                "usage_stats": {
                    "total_usage_count": total_usage or 0,
                    "total_tokens_used": total_tokens or 0,
                    "total_cost": float(total_cost or 0),
                },
            }

        except Exception as e:
            logger.error("Failed to get profile stats", error=str(e))
            return {}

    @classmethod
    def clear_provider_cache(cls) -> None:
        """Clear the provider cache to force fresh data on next request."""
        cls._provider_cache = {}
        cls._provider_cache_timestamp = 0
        logger.info("Provider cache cleared")

    async def get_available_providers(self) -> dict[str, Any]:
        """Get available LLM providers and their information.

        Uses caching to avoid expensive provider lookups on every request.

        Returns:
            Dictionary with provider information
        """
        try:
            current_time = time.time()

            # Check if cache is valid
            if (
                self._provider_cache
                and (current_time - self._provider_cache_timestamp)
                < self._provider_cache_ttl
            ):
                logger.debug("Returning cached provider information")
                return self._provider_cache

            logger.debug("Fetching fresh provider information")
            providers = {}

            for (
                provider_name
            ) in await self.llm_service.list_available_providers():
                provider_info = (
                    await self.llm_service.get_provider_info(
                        provider_name
                    )
                )
                providers[provider_name] = provider_info

            result = {
                "providers": providers,
                "default_provider": getattr(
                    settings, "default_llm_provider", "openai"
                ),
            }

            # Update cache
            self._provider_cache = result
            self._provider_cache_timestamp = current_time

            return result

        except Exception as e:
            logger.error(
                "Failed to get available providers", error=str(e)
            )
            return {}


class ProfileError(Exception):
    """Profile operation error."""

    pass
