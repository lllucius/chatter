"""Prompt management service."""

import hashlib
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.prompt import Prompt, PromptCategory, PromptType
from chatter.schemas.prompt import (
    PromptCreate,
    PromptListRequest,
    PromptTestRequest,
    PromptUpdate,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class PromptService:
    """Service for prompt management operations."""

    def __init__(self, session: AsyncSession):
        """Initialize prompt service.

        Args:
            session: Database session
        """
        self.session = session

    async def create_prompt(
        self,
        user_id: str,
        prompt_data: PromptCreate
    ) -> Prompt:
        """Create a new prompt.

        Args:
            user_id: Owner user ID
            prompt_data: Prompt creation data

        Returns:
            Created prompt

        Raises:
            PromptError: If prompt creation fails
        """
        try:
            # Check for duplicate prompt names for this user
            existing_result = await self.session.execute(
                select(Prompt).where(
                    and_(
                        Prompt.owner_id == user_id,
                        Prompt.name == prompt_data.name
                    )
                )
            )
            existing_prompt = existing_result.scalar_one_or_none()

            if existing_prompt:
                raise PromptError("Prompt with this name already exists") from None

            # Generate content hash
            content_hash = hashlib.sha256(prompt_data.content.encode()).hexdigest()

            # Create prompt
            prompt_dict = prompt_data.model_dump()
            prompt = Prompt(
                owner_id=user_id,
                content_hash=content_hash,
                **prompt_dict
            )

            self.session.add(prompt)
            await self.session.commit()
            await self.session.refresh(prompt)

            logger.info(
                "Prompt created",
                prompt_id=prompt.id,
                name=prompt.name,
                user_id=user_id,
                prompt_type=prompt.prompt_type.value,
                category=prompt.category.value
            )

            return prompt

        except PromptError:
            raise
        except Exception as e:
            logger.error("Prompt creation failed", error=str(e))
            raise PromptError(f"Failed to create prompt: {str(e)}")

    async def get_prompt(
        self,
        prompt_id: str,
        user_id: str
    ) -> Prompt | None:
        """Get prompt by ID with access control.

        Args:
            prompt_id: Prompt ID
            user_id: Requesting user ID

        Returns:
            Prompt if found and accessible, None otherwise
        """
        try:
            result = await self.session.execute(
                select(Prompt).where(
                    and_(
                        Prompt.id == prompt_id,
                        or_(
                            Prompt.owner_id == user_id,
                            Prompt.is_public is True,
                        )
                    )
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error("Failed to get prompt", prompt_id=prompt_id, error=str(e))
            return None

    async def list_prompts(
        self,
        user_id: str,
        list_request: PromptListRequest
    ) -> tuple[list[Prompt], int]:
        """List prompts with filtering and pagination.

        Args:
            user_id: Requesting user ID
            list_request: List request parameters

        Returns:
            Tuple of (prompts list, total count)
        """
        try:
            # Build base query with access control
            query = select(Prompt).where(
                or_(
                    Prompt.owner_id == user_id,
                    Prompt.is_public is True,
                )
            )

            # Add filters
            if list_request.prompt_type:
                query = query.where(Prompt.prompt_type == list_request.prompt_type)

            if list_request.category:
                query = query.where(Prompt.category == list_request.category)

            if list_request.tags:
                for tag in list_request.tags:
                    query = query.where(Prompt.tags.contains([tag]))

            if list_request.is_public is not None:
                query = query.where(Prompt.is_public == list_request.is_public)

            if list_request.is_chain is not None:
                query = query.where(Prompt.is_chain == list_request.is_chain)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()

            # Add sorting
            sort_column = getattr(Prompt, list_request.sort_by, Prompt.created_at)
            if list_request.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Add pagination
            query = query.offset(list_request.offset).limit(list_request.limit)

            # Execute query
            result = await self.session.execute(query)
            prompts = result.scalars().all()

            return list(prompts), total_count

        except Exception as e:
            logger.error("Failed to list prompts", error=str(e))
            return [], 0

    async def update_prompt(
        self,
        prompt_id: str,
        user_id: str,
        update_data: PromptUpdate
    ) -> Prompt | None:
        """Update prompt.

        Args:
            prompt_id: Prompt ID
            user_id: Requesting user ID
            update_data: Update data

        Returns:
            Updated prompt if successful, None otherwise
        """
        try:
            # Get prompt with ownership check
            result = await self.session.execute(
                select(Prompt).where(
                    and_(
                        Prompt.id == prompt_id,
                        Prompt.owner_id == user_id
                    )
                )
            )
            prompt = result.scalar_one_or_none()

            if not prompt:
                return None

            # Check for name conflicts if name is being updated
            if update_data.name and update_data.name != prompt.name:
                existing_result = await self.session.execute(
                    select(Prompt).where(
                        and_(
                            Prompt.owner_id == user_id,
                            Prompt.name == update_data.name,
                            Prompt.id != prompt_id
                        )
                    )
                )
                existing_prompt = existing_result.scalar_one_or_none()

                if existing_prompt:
                    raise PromptError("Prompt with this name already exists") from None

            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(prompt, field, value)

            # Update content hash if content changed
            if update_data.content:
                prompt.content_hash = hashlib.sha256(update_data.content.encode()).hexdigest()

            await self.session.commit()
            await self.session.refresh(prompt)

            logger.info("Prompt updated", prompt_id=prompt_id, user_id=user_id)
            return prompt

        except PromptError:
            raise
        except Exception as e:
            logger.error("Failed to update prompt", prompt_id=prompt_id, error=str(e))
            raise PromptError(f"Failed to update prompt: {str(e)}")

    async def delete_prompt(
        self,
        prompt_id: str,
        user_id: str
    ) -> bool:
        """Delete prompt.

        Args:
            prompt_id: Prompt ID
            user_id: Requesting user ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get prompt with ownership check
            result = await self.session.execute(
                select(Prompt).where(
                    and_(
                        Prompt.id == prompt_id,
                        Prompt.owner_id == user_id
                    )
                )
            )
            prompt = result.scalar_one_or_none()

            if not prompt:
                return False

            await self.session.delete(prompt)
            await self.session.commit()

            logger.info("Prompt deleted", prompt_id=prompt_id, user_id=user_id)
            return True

        except Exception as e:
            logger.error("Failed to delete prompt", prompt_id=prompt_id, error=str(e))
            return False

    async def test_prompt(
        self,
        prompt_id: str,
        user_id: str,
        test_request: PromptTestRequest
    ) -> dict[str, Any]:
        """Test prompt with given variables.

        Args:
            prompt_id: Prompt ID
            user_id: Requesting user ID
            test_request: Test request parameters

        Returns:
            Test results
        """
        try:
            # Get prompt
            prompt = await self.get_prompt(prompt_id, user_id)
            if not prompt:
                raise PromptError("Prompt not found") from None

            start_time = datetime.now(UTC)

            # Validate variables
            validation_result = prompt.validate_variables(**test_request.variables)

            rendered_content = None
            estimated_tokens = None

            # Render prompt if validation passed and not validate-only
            if validation_result["valid"] and not test_request.validate_only:
                try:
                    rendered_content = prompt.render(**test_request.variables)
                    # Simple token estimation (approximate)
                    estimated_tokens = len(rendered_content.split()) * 1.3  # rough approximation
                except Exception as render_error:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Render error: {str(render_error)}")

            end_time = datetime.now(UTC)
            test_duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Update prompt usage stats if test was successful
            if validation_result["valid"] and rendered_content:
                prompt.usage_count += 1
                prompt.last_used_at = datetime.now(UTC)
                await self.session.commit()

            result = {
                "rendered_content": rendered_content,
                "validation_result": validation_result,
                "estimated_tokens": int(estimated_tokens) if estimated_tokens else None,
                "test_duration_ms": test_duration_ms,
            }

            logger.info(
                "Prompt test completed",
                prompt_id=prompt_id,
                test_duration_ms=test_duration_ms,
                validation_valid=validation_result["valid"]
            )

            return result

        except PromptError:
            raise
        except Exception as e:
            logger.error("Prompt test failed", prompt_id=prompt_id, error=str(e))
            raise PromptError(f"Prompt test failed: {str(e)}")

    async def clone_prompt(
        self,
        prompt_id: str,
        user_id: str,
        new_name: str,
        description: str | None = None,
        modifications: dict[str, Any] | None = None
    ) -> Prompt:
        """Clone an existing prompt.

        Args:
            prompt_id: Source prompt ID
            user_id: User ID for the new prompt
            new_name: Name for the cloned prompt
            description: Description for the cloned prompt
            modifications: Optional modifications to apply

        Returns:
            Cloned prompt

        Raises:
            PromptError: If cloning fails
        """
        try:
            # Get source prompt
            source_prompt = await self.get_prompt(prompt_id, user_id)
            if not source_prompt:
                raise PromptError("Source prompt not found") from None

            # Check for name conflicts
            existing_result = await self.session.execute(
                select(Prompt).where(
                    and_(
                        Prompt.owner_id == user_id,
                        Prompt.name == new_name
                    )
                )
            )
            existing_prompt = existing_result.scalar_one_or_none()

            if existing_prompt:
                raise PromptError("Prompt with this name already exists") from None

            # Create new prompt from source
            prompt_dict = source_prompt.to_dict()

            # Remove fields that should not be copied
            fields_to_remove = [
                'id', 'owner_id', 'created_at', 'updated_at', 'content_hash',
                'usage_count', 'last_used_at', 'total_tokens_used', 'total_cost',
                'rating', 'rating_count', 'success_rate', 'avg_response_time_ms'
            ]
            for field in fields_to_remove:
                prompt_dict.pop(field, None)

            # Apply modifications
            prompt_dict['name'] = new_name
            if description is not None:
                prompt_dict['description'] = description

            if modifications:
                prompt_dict.update(modifications)

            # Generate new content hash
            content_hash = hashlib.sha256(prompt_dict['content'].encode()).hexdigest()

            # Create cloned prompt
            cloned_prompt = Prompt(
                owner_id=user_id,
                content_hash=content_hash,
                **prompt_dict
            )

            self.session.add(cloned_prompt)
            await self.session.commit()
            await self.session.refresh(cloned_prompt)

            logger.info(
                "Prompt cloned",
                source_prompt_id=prompt_id,
                cloned_prompt_id=cloned_prompt.id,
                user_id=user_id
            )

            return cloned_prompt

        except PromptError:
            raise
        except Exception as e:
            logger.error("Failed to clone prompt", prompt_id=prompt_id, error=str(e))
            raise PromptError(f"Failed to clone prompt: {str(e)}")

    async def get_prompt_stats(
        self,
        user_id: str
    ) -> dict[str, Any]:
        """Get prompt statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with prompt statistics
        """
        try:
            # Count prompts by type
            type_counts = {}
            for prompt_type in PromptType:
                result = await self.session.execute(
                    select(func.count(Prompt.id)).where(
                        and_(
                            Prompt.owner_id == user_id,
                            Prompt.prompt_type == prompt_type
                        )
                    )
                )
                type_counts[prompt_type.value] = result.scalar()

            # Count prompts by category
            category_counts = {}
            for category in PromptCategory:
                result = await self.session.execute(
                    select(func.count(Prompt.id)).where(
                        and_(
                            Prompt.owner_id == user_id,
                            Prompt.category == category
                        )
                    )
                )
                category_counts[category.value] = result.scalar()

            # Get most used prompts
            most_used_result = await self.session.execute(
                select(Prompt).where(
                    Prompt.owner_id == user_id
                ).order_by(desc(Prompt.usage_count)).limit(5)
            )
            most_used_prompts = most_used_result.scalars().all()

            # Get recent prompts
            recent_result = await self.session.execute(
                select(Prompt).where(
                    Prompt.owner_id == user_id
                ).order_by(desc(Prompt.created_at)).limit(5)
            )
            recent_prompts = recent_result.scalars().all()

            # Get usage totals
            usage_result = await self.session.execute(
                select(
                    func.sum(Prompt.usage_count),
                    func.sum(Prompt.total_tokens_used),
                    func.sum(Prompt.total_cost)
                ).where(Prompt.owner_id == user_id)
            )
            total_usage, total_tokens, total_cost = usage_result.first()

            return {
                "total_prompts": sum(type_counts.values()),
                "prompts_by_type": type_counts,
                "prompts_by_category": category_counts,
                "most_used_prompts": [prompt.to_dict() for prompt in most_used_prompts],
                "recent_prompts": [prompt.to_dict() for prompt in recent_prompts],
                "usage_stats": {
                    "total_usage_count": total_usage or 0,
                    "total_tokens_used": total_tokens or 0,
                    "total_cost": float(total_cost or 0),
                },
            }

        except Exception as e:
            logger.error("Failed to get prompt stats", error=str(e))
            return {}


class PromptError(Exception):
    """Prompt operation error."""
    pass
