"""Agent management endpoints with comprehensive validation, caching, and security."""

import re
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from chatter.api.auth import get_current_user
from chatter.core.agents import AgentManager
from chatter.core.validation import (
    DEFAULT_CONTEXT,
    ValidationError,
    validation_engine,
)
from chatter.models.user import User
from chatter.schemas.agents import (
    AgentBulkCreateRequest,
    AgentBulkCreateResponse,
    AgentBulkDeleteRequest,
    AgentCreateRequest,
    AgentDeleteResponse,
    AgentHealthResponse,
    AgentInteractRequest,
    AgentInteractResponse,
    AgentListResponse,
    AgentResponse,
    AgentStatsResponse,
    AgentStatus,
    AgentType,
    AgentUpdateRequest,
)
from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem, NotFoundProblem
from chatter.utils.unified_rate_limiter import (
    RateLimitExceeded,
    get_unified_rate_limiter,
)

logger = get_logger(__name__)
router = APIRouter(
    tags=["agents"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)


async def get_agent_manager() -> AgentManager:
    """Get agent manager instance.

    Returns:
        AgentManager instance
    """
    from chatter.core.agents import agent_manager

    return agent_manager


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
    description="Create a new AI agent with specified configuration and capabilities.",
    responses={
        201: {"description": "Agent created successfully"},
        400: {"description": "Invalid input data"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def create_agent(
    agent_data: AgentCreateRequest,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentResponse:
    """Create a new agent.

    Args:
        agent_data: Agent creation data
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Created agent data
    """
    try:
        # Apply rate limiting for agent creation
        rate_limiter = get_unified_rate_limiter()
        try:
            # Check hourly limit
            await rate_limiter.check_rate_limit(
                key=f"create_agent:{current_user.id}",
                limit=10,  # 10 agents per hour
                window=3600,  # 1 hour in seconds
                identifier="create_agent_hourly",
            )
            # Check daily limit
            await rate_limiter.check_rate_limit(
                key=f"create_agent:{current_user.id}",
                limit=50,  # 50 agents per day
                window=86400,  # 1 day in seconds
                identifier="create_agent_daily",
            )
        except RateLimitExceeded as e:
            raise InternalServerProblem(detail=str(e)) from e

        # Validate input data using the unified validation system
        try:
            # Validate agent name
            result = validation_engine.validate_input(
                agent_data.name, "agent_name", DEFAULT_CONTEXT
            )
            if not result.is_valid:
                raise InternalServerProblem(
                    detail=result.errors[0].message
                )
            agent_data.name = result.value

            # Validate description
            result = validation_engine.validate_input(
                agent_data.description, "text", DEFAULT_CONTEXT
            )
            if not result.is_valid:
                raise InternalServerProblem(
                    detail=result.errors[0].message
                )
            agent_data.description = result.value

            # Validate system prompt
            result = validation_engine.validate_input(
                agent_data.system_prompt, "message", DEFAULT_CONTEXT
            )
            if not result.is_valid:
                raise InternalServerProblem(
                    detail=result.errors[0].message
                )
            agent_data.system_prompt = result.value

            # Validate agent type - enum validation is handled by Pydantic, keep simple validation
            if agent_data.agent_type is None:
                raise InternalServerProblem(
                    detail="Agent type is required"
                )

            # Validate temperature
            if (
                not isinstance(agent_data.temperature, int | float)
                or agent_data.temperature < 0.0
                or agent_data.temperature > 2.0
            ):
                raise InternalServerProblem(
                    detail="Temperature must be between 0.0 and 2.0"
                )

            # Validate max_tokens
            if (
                not isinstance(agent_data.max_tokens, int)
                or agent_data.max_tokens < 1
                or agent_data.max_tokens > 32000
            ):
                raise InternalServerProblem(
                    detail="Max tokens must be between 1 and 32000"
                )

        except ValidationError as e:
            raise InternalServerProblem(detail=str(e)) from e

        # Add created_by to metadata
        metadata = agent_data.metadata or {}
        metadata["created_by"] = current_user.id

        # Create agent with enhanced error handling
        try:
            agent_id = await agent_manager.create_agent(
                name=agent_data.name,
                agent_type=agent_data.agent_type,
                description=agent_data.description,
                system_message=agent_data.system_prompt,
                llm=None,  # Will be handled by agent manager
                personality_traits=agent_data.personality_traits,
                knowledge_domains=agent_data.knowledge_domains,
                response_style=agent_data.response_style,
                capabilities=agent_data.capabilities,
                available_tools=agent_data.available_tools,
                primary_llm=agent_data.primary_llm,
                fallback_llm=agent_data.fallback_llm,
                temperature=agent_data.temperature,
                max_tokens=agent_data.max_tokens,
                max_conversation_length=agent_data.max_conversation_length,
                context_window_size=agent_data.context_window_size,
                response_timeout=agent_data.response_timeout,
                learning_enabled=agent_data.learning_enabled,
                feedback_weight=agent_data.feedback_weight,
                adaptation_threshold=agent_data.adaptation_threshold,
                tags=agent_data.tags,
                metadata=metadata,
                created_by=current_user.id,
            )
        except ValueError as e:
            logger.error("Invalid agent configuration", error=str(e))
            raise InternalServerProblem(
                detail=f"Invalid agent configuration: {str(e)}"
            ) from e

        # Get the created agent
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            logger.error("Created agent not found", agent_id=agent_id)
            raise InternalServerProblem(
                detail="Failed to retrieve created agent"
            )

        logger.info(
            "Agent created successfully",
            agent_id=agent_id,
            agent_name=agent_data.name,
            created_by=current_user.id,
        )

        return AgentResponse.model_validate(agent.profile.model_dump())

    except InternalServerProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to create agent", error=str(e), exc_info=True
        )
        raise InternalServerProblem(
            detail="Failed to create agent"
        ) from e


@router.get(
    "/",
    response_model=AgentListResponse,
    summary="List agents",
    description="List all agents with optional filtering and pagination. Users can only see their own agents.",
)
async def list_agents(
    agent_type: AgentType | None = Query(
        None, description="Filter by agent type"
    ),
    status: AgentStatus | None = Query(
        None, description="Filter by status"
    ),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    limit: int = Query(
        50, ge=1, description="Maximum number of results"
    ),
    offset: int = Query(
        0, ge=0, description="Number of results to skip"
    ),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    ),
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentListResponse:
    """List all agents with optional filtering and pagination.

    Args:
        agent_type: Filter by agent type
        status: Filter by status
        tags: Filter by tags
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Paginated list of agents
    """
    try:
        # Validate pagination parameters
        validated_offset = (
            max(0, offset) if isinstance(offset, int) else 0
        )
        validated_limit = (
            limit if isinstance(limit, int) and limit >= 1 else 10
        )

        # Get agents with filtering
        agents, total = await agent_manager.list_agents(
            agent_type=agent_type,
            status=status,
            offset=validated_offset,
            limit=validated_limit,
            user_id=current_user.id,  # Filter by user's agents only
        )

        # Additional client-side filtering by tags if specified
        if tags:
            filtered_agents = []
            for agent in agents:
                # Check if any of the requested tags match agent tags
                if any(tag in agent.tags for tag in tags):
                    filtered_agents.append(agent)
            agents = filtered_agents
            # Note: This changes the total count for this page but not the overall total
            # In a production system, tag filtering should be done at the database level

        # Convert to response format
        agent_responses = []
        for agent in agents:
            try:
                agent_responses.append(
                    AgentResponse.model_validate(agent)
                )
            except Exception as e:
                logger.warning(
                    f"Failed to serialize agent {agent.id}: {e}"
                )
                continue

        # Calculate pagination info
        current_page = (
            (validated_offset // validated_limit) + 1
            if validated_limit > 0
            else 1
        )
        total_pages = (
            (total + validated_limit - 1) // validated_limit
            if validated_limit > 0
            else 1
        )  # Ceiling division

        logger.info(
            "Listed agents",
            count=len(agent_responses),
            total=total,
            page=current_page,
            user_id=current_user.id,
        )

        return AgentListResponse(
            agents=agent_responses,
            total=total,
            page=current_page,
            per_page=validated_limit,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(
            "Failed to list agents",
            error=str(e),
            user_id=current_user.id,
        )
        raise InternalServerProblem(
            detail="Failed to list agents"
        ) from e


@router.get(
    "/templates",
    response_model=list[dict[str, Any]],
    summary="Get agent templates",
    description="Get predefined agent templates for common use cases.",
)
async def get_agent_templates(
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> list[dict[str, Any]]:
    """Get agent templates.

    Args:
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        List of agent templates
    """
    try:
        templates = await agent_manager.get_agent_templates()
        return templates

    except Exception as e:
        logger.error("Failed to get agent templates", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get agent templates"
        ) from e


@router.get(
    "/stats/overview",
    response_model=AgentStatsResponse,
    summary="Get agent statistics",
    description="Get comprehensive statistics about all agents for the current user.",
)
async def get_agent_stats(
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentStatsResponse:
    """Get agent statistics.

    Args:
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent statistics
    """
    try:
        stats = await agent_manager.get_agent_stats()
        return AgentStatsResponse.model_validate(stats)

    except Exception as e:
        logger.error("Failed to get agent stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get agent stats"
        ) from e


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentResponse:
    """Get agent by ID.

    Args:
        agent_id: Agent ID
        request: Get request parameters
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent data
    """
    try:
        # Validate agent_id format
        result = validation_engine.validate_input(
            agent_id, "agent_id", DEFAULT_CONTEXT
        )
        if not result.is_valid:
            raise InternalServerProblem(detail=result.errors[0].message)
        agent_id = result.value

        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has access to this agent (basic ownership check)
        if (
            hasattr(agent.profile, "created_by")
            and agent.profile.created_by != current_user.id
            and current_user.id != "system"
        ):
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        return AgentResponse.model_validate(agent.profile.model_dump())

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to get agent", agent_id=agent_id, error=str(e)
        )
        raise InternalServerProblem(detail="Failed to get agent") from e


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdateRequest,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentResponse:
    """Update an agent.

    Args:
        agent_id: Agent ID
        agent_data: Agent update data
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Updated agent data
    """
    try:
        # Validate agent_id format (ULID)
        from ulid import ULID

        try:
            ULID.from_str(agent_id)
        except ValueError as e:
            raise NotFoundProblem(
                detail=f"Invalid agent ID format: {agent_id}"
            ) from e

        # First check if agent exists
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has permission to update this agent
        if (
            hasattr(agent.profile, "created_by")
            and agent.profile.created_by != current_user.id
            and current_user.id != "system"
        ):
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Update agent using the agent manager
        success = await agent_manager.update_agent(
            agent_id, agent_data.model_dump(exclude_unset=True)
        )

        if not success:
            raise InternalServerProblem(detail="Failed to update agent")

        # Get updated agent
        updated_agent = await agent_manager.get_agent(agent_id)
        if not updated_agent:
            raise InternalServerProblem(
                detail="Failed to retrieve updated agent"
            )

        return AgentResponse.model_validate(
            updated_agent.profile.model_dump()
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to update agent", agent_id=agent_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to update agent"
        ) from e


@router.delete("/{agent_id}", response_model=AgentDeleteResponse)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentDeleteResponse:
    """Delete an agent.

    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Deletion result
    """
    try:
        # Validate agent_id format (ULID)
        from ulid import ULID

        try:
            ULID.from_str(agent_id)
        except ValueError as e:
            raise NotFoundProblem(
                detail=f"Invalid agent ID format: {agent_id}"
            ) from e

        # Check if agent exists and user has permission to delete
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has permission to delete this agent
        if (
            hasattr(agent.profile, "created_by")
            and agent.profile.created_by != current_user.id
            and current_user.id != "system"
        ):
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        success = await agent_manager.delete_agent(agent_id)

        if not success:
            raise InternalServerProblem(detail="Failed to delete agent")

        return AgentDeleteResponse(
            success=True,
            message=f"Agent {agent_id} deleted successfully",
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete agent", agent_id=agent_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to delete agent"
        ) from e


@router.post(
    "/{agent_id}/interact",
    response_model=AgentInteractResponse,
    summary="Interact with agent",
    description="Send a message to an agent and receive a response. Rate limited per user per agent.",
    responses={
        200: {"description": "Interaction successful"},
        404: {"description": "Agent not found or access denied"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def interact_with_agent(
    agent_id: str,
    interaction_data: AgentInteractRequest,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentInteractResponse:
    """Send a message to an agent and get a response.

    Args:
        agent_id: Agent ID
        interaction_data: Interaction data
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent response
    """
    try:
        # Apply rate limiting for agent interactions
        rate_limiter = get_unified_rate_limiter()
        try:
            # Check hourly limit
            await rate_limiter.check_rate_limit(
                key=f"interact_agent:{current_user.id}:{agent_id}",
                limit=100,  # 100 interactions per hour per agent
                window=3600,  # 1 hour in seconds
                identifier="interact_agent_hourly",
            )
            # Check daily limit
            await rate_limiter.check_rate_limit(
                key=f"interact_agent:{current_user.id}:{agent_id}",
                limit=1000,  # 1000 interactions per day per agent
                window=86400,  # 1 day in seconds
                identifier="interact_agent_daily",
            )
        except RateLimitExceeded as e:
            raise InternalServerProblem(detail=str(e)) from e

        # Validate inputs
        result = validation_engine.validate_input(
            agent_id, "agent_id", DEFAULT_CONTEXT
        )
        if not result.is_valid:
            raise InternalServerProblem(detail=result.errors[0].message)
        agent_id = result.value

        result = validation_engine.validate_input(
            interaction_data.conversation_id,
            "conversation_id",
            DEFAULT_CONTEXT,
        )
        if not result.is_valid:
            raise InternalServerProblem(detail=result.errors[0].message)
        conversation_id = result.value

        result = validation_engine.validate_input(
            interaction_data.message, "message", DEFAULT_CONTEXT
        )
        if not result.is_valid:
            raise InternalServerProblem(detail=result.errors[0].message)
        message = result.value

        # Sanitize context
        context = interaction_data.context or {}
        if not isinstance(context, dict):
            context = {}

        # Sanitize context keys and values
        sanitized_context = {}
        for key, value in context.items():
            if isinstance(key, str) and len(key) <= 100:
                if isinstance(value, str) and len(value) <= 1000:
                    # Remove dangerous patterns
                    value = re.sub(
                        r"<script.*?>.*?</script>",
                        "",
                        value,
                        flags=re.IGNORECASE,
                    )
                    value = re.sub(
                        r"javascript:", "", value, flags=re.IGNORECASE
                    )
                    value = re.sub(
                        r"on\w+\s*=", "", value, flags=re.IGNORECASE
                    )
                    sanitized_context[key] = value
                elif isinstance(value, int | float | bool):
                    sanitized_context[key] = value
        context = sanitized_context

        # Check if agent exists and user has access
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has permission to interact with this agent
        if (
            hasattr(agent.profile, "created_by")
            and agent.profile.created_by != current_user.id
            and current_user.id != "system"
        ):
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Add user context to interaction
        context["user_id"] = current_user.id

        from datetime import UTC, datetime

        start_time = datetime.now(UTC)

        response = await agent_manager.send_message_to_agent(
            agent_id=agent_id,
            message=message,
            conversation_id=conversation_id,
            context=context,
        )

        if response is None:
            raise NotFoundProblem(
                detail=f"Agent {agent_id} not found or unable to respond"
            )

        response_time = (datetime.now(UTC) - start_time).total_seconds()

        return AgentInteractResponse(
            agent_id=agent_id,
            response=response,
            conversation_id=conversation_id,
            tools_used=[],  # Would be populated by actual agent response
            confidence_score=0.9,  # Would be calculated by agent
            response_time=response_time,
            timestamp=datetime.now(UTC),
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to interact with agent",
            agent_id=agent_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to interact with agent"
        ) from e


@router.get("/{agent_id}/health", response_model=AgentHealthResponse)
async def get_agent_health(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentHealthResponse:
    """Get agent health status.

    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent health information
    """
    try:
        # Validate agent_id format
        result = validation_engine.validate_input(
            agent_id, "agent_id", DEFAULT_CONTEXT
        )
        if not result.is_valid:
            raise InternalServerProblem(detail=result.errors[0].message)
        agent_id = result.value

        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has access to this agent
        if (
            hasattr(agent.profile, "created_by")
            and agent.profile.created_by != current_user.id
            and current_user.id != "system"
        ):
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Calculate health metrics
        health_status = "healthy"
        if agent.profile.status != AgentStatus.ACTIVE:
            health_status = "unhealthy"

        # Get performance metrics
        metrics = agent.performance_metrics
        last_interaction = None
        if agent.conversation_history:
            # Find the most recent interaction across all conversations
            all_interactions = []
            for conv_history in agent.conversation_history.values():
                all_interactions.extend(conv_history)
            if all_interactions:
                last_interaction = max(
                    all_interactions, key=lambda x: x.timestamp
                ).timestamp

        return AgentHealthResponse(
            agent_id=agent_id,
            status=agent.profile.status,
            health=health_status,
            last_interaction=last_interaction,
            response_time_avg=metrics.get("average_response_time", 0.0),
            error_rate=0.0,  # Would be calculated from actual error tracking
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to get agent health",
            agent_id=agent_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get agent health"
        ) from e


@router.post(
    "/bulk",
    response_model=AgentBulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_agents(
    request: AgentBulkCreateRequest,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentBulkCreateResponse:
    """Create multiple agents in bulk.

    Args:
        request: Bulk creation request
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Bulk creation results
    """
    try:
        # Apply rate limiting for bulk operations
        rate_limiter = get_unified_rate_limiter()
        try:
            # Check hourly limit
            await rate_limiter.check_rate_limit(
                key=f"bulk_create_agents:{current_user.id}",
                limit=3,  # 3 bulk operations per hour
                window=3600,  # 1 hour in seconds
                identifier="bulk_create_hourly",
            )
            # Check daily limit
            await rate_limiter.check_rate_limit(
                key=f"bulk_create_agents:{current_user.id}",
                limit=10,  # 10 bulk operations per day
                window=86400,  # 1 day in seconds
                identifier="bulk_create_daily",
            )
        except RateLimitExceeded as e:
            raise InternalServerProblem(detail=str(e)) from e

        created_agents = []
        failed_creations = []

        for i, agent_data in enumerate(request.agents):
            try:
                # Validate each agent data
                try:
                    # Validate agent name
                    result = validation_engine.validate_input(
                        agent_data.name, "agent_name", DEFAULT_CONTEXT
                    )
                    if not result.is_valid:
                        raise ValueError(result.errors[0].message)
                    agent_data.name = result.value

                    # Validate description
                    result = validation_engine.validate_input(
                        agent_data.description,
                        "text",
                        DEFAULT_CONTEXT,
                    )
                    if not result.is_valid:
                        raise ValueError(result.errors[0].message)
                    agent_data.description = result.value

                    # Validate system prompt
                    result = validation_engine.validate_input(
                        agent_data.system_prompt,
                        "message",
                        DEFAULT_CONTEXT,
                    )
                    if not result.is_valid:
                        raise ValueError(result.errors[0].message)
                    agent_data.system_prompt = result.value

                    # Validate agent type
                    if agent_data.agent_type is None:
                        raise ValueError("Agent type is required")

                    # Validate temperature
                    if (
                        not isinstance(
                            agent_data.temperature, int | float
                        )
                        or agent_data.temperature < 0.0
                        or agent_data.temperature > 2.0
                    ):
                        raise ValueError(
                            "Temperature must be between 0.0 and 2.0"
                        )

                    # Validate max_tokens
                    if (
                        not isinstance(agent_data.max_tokens, int)
                        or agent_data.max_tokens < 1
                        or agent_data.max_tokens > 32000
                    ):
                        raise ValueError(
                            "Max tokens must be between 1 and 32000"
                        )

                except (ValidationError, ValueError) as ve:
                    failed_creations.append(
                        {
                            "index": i,
                            "agent_name": getattr(
                                agent_data, "name", "Unknown"
                            ),
                            "error": str(ve),
                        }
                    )
                    continue

                # Add created_by to metadata
                metadata = agent_data.metadata or {}
                metadata["created_by"] = current_user.id
                metadata["bulk_creation"] = True
                metadata["bulk_index"] = i

                # Create agent
                agent_id = await agent_manager.create_agent(
                    name=agent_data.name,
                    agent_type=agent_data.agent_type,
                    description=agent_data.description,
                    system_message=agent_data.system_prompt,
                    llm=None,
                    personality_traits=agent_data.personality_traits,
                    knowledge_domains=agent_data.knowledge_domains,
                    response_style=agent_data.response_style,
                    capabilities=agent_data.capabilities,
                    available_tools=agent_data.available_tools,
                    primary_llm=agent_data.primary_llm,
                    fallback_llm=agent_data.fallback_llm,
                    temperature=agent_data.temperature,
                    max_tokens=agent_data.max_tokens,
                    max_conversation_length=agent_data.max_conversation_length,
                    context_window_size=agent_data.context_window_size,
                    response_timeout=agent_data.response_timeout,
                    learning_enabled=agent_data.learning_enabled,
                    feedback_weight=agent_data.feedback_weight,
                    adaptation_threshold=agent_data.adaptation_threshold,
                    tags=agent_data.tags,
                    metadata=metadata,
                    created_by=current_user.id,
                )

                # Get the created agent
                agent = await agent_manager.get_agent(agent_id)
                if agent:
                    created_agents.append(
                        AgentResponse.model_validate(agent.profile)
                    )

            except Exception as e:
                failed_creations.append(
                    {
                        "index": i,
                        "name": getattr(
                            agent_data, "name", f"Agent {i}"
                        ),
                        "error": str(e),
                    }
                )
                logger.warning(
                    f"Failed to create agent {i} in bulk operation",
                    error=str(e),
                )

        logger.info(
            "Bulk agent creation completed",
            total_requested=len(request.agents),
            created=len(created_agents),
            failed=len(failed_creations),
            user_id=current_user.id,
        )

        return AgentBulkCreateResponse(
            created=created_agents,
            failed=failed_creations,
            total_requested=len(request.agents),
            total_created=len(created_agents),
        )

    except InternalServerProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to bulk create agents",
            error=str(e),
            user_id=current_user.id,
        )
        raise InternalServerProblem(
            detail="Failed to bulk create agents"
        ) from e


@router.delete("/bulk", response_model=dict[str, Any])
async def bulk_delete_agents(
    request: AgentBulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> dict[str, Any]:
    """Delete multiple agents in bulk.

    Args:
        request: Bulk deletion request
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Bulk deletion results
    """
    try:
        # Apply rate limiting for bulk operations
        rate_limiter = get_unified_rate_limiter()
        try:
            # Check hourly limit
            await rate_limiter.check_rate_limit(
                key=f"bulk_delete_agents:{current_user.id}",
                limit=3,  # 3 bulk operations per hour
                window=3600,  # 1 hour in seconds
                identifier="bulk_delete_hourly",
            )
            # Check daily limit
            await rate_limiter.check_rate_limit(
                key=f"bulk_delete_agents:{current_user.id}",
                limit=10,  # 10 bulk operations per day
                window=86400,  # 1 day in seconds
                identifier="bulk_delete_daily",
            )
        except RateLimitExceeded as e:
            raise InternalServerProblem(detail=str(e)) from e

        deleted_agents = []
        failed_deletions = []

        for agent_id in request.agent_ids:
            try:
                # Validate agent_id format
                result = validation_engine.validate_input(
                    agent_id, "agent_id", DEFAULT_CONTEXT
                )
                if not result.is_valid:
                    failed_deletions.append(
                        {
                            "agent_id": agent_id,
                            "error": result.errors[0].message,
                        }
                    )
                    continue
                agent_id = result.value

                # Check if agent exists and user has permission
                agent = await agent_manager.get_agent(agent_id)
                if not agent:
                    failed_deletions.append(
                        {
                            "agent_id": agent_id,
                            "error": "Agent not found",
                        }
                    )
                    continue

                # Check if user has permission to delete this agent
                if (
                    hasattr(agent.profile, "created_by")
                    and agent.profile.created_by != current_user.id
                    and current_user.id != "system"
                ):
                    failed_deletions.append(
                        {
                            "agent_id": agent_id,
                            "error": "Permission denied",
                        }
                    )
                    continue

                # Delete the agent
                success = await agent_manager.delete_agent(agent_id)
                if success:
                    deleted_agents.append(agent_id)
                else:
                    failed_deletions.append(
                        {
                            "agent_id": agent_id,
                            "error": "Deletion failed",
                        }
                    )

            except Exception as e:
                failed_deletions.append(
                    {"agent_id": agent_id, "error": str(e)}
                )
                logger.warning(
                    f"Failed to delete agent {agent_id} in bulk operation",
                    error=str(e),
                )

        logger.info(
            "Bulk agent deletion completed",
            total_requested=len(request.agent_ids),
            deleted=len(deleted_agents),
            failed=len(failed_deletions),
            user_id=current_user.id,
        )

        return {
            "deleted": deleted_agents,
            "failed": failed_deletions,
            "total_requested": len(request.agent_ids),
            "total_deleted": len(deleted_agents),
        }

    except InternalServerProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to bulk delete agents",
            error=str(e),
            user_id=current_user.id,
        )
        raise InternalServerProblem(
            detail="Failed to bulk delete agents"
        ) from e
