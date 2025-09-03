"""Agent management endpoints."""

from fastapi import APIRouter, Depends, status

from chatter.api.auth import get_current_user
from chatter.core.agents import AgentManager
from chatter.models.user import User
from chatter.schemas.agents import (
    AgentCreateRequest,
    AgentDeleteResponse,
    AgentGetRequest,
    AgentInteractRequest,
    AgentInteractResponse,
    AgentListRequest,
    AgentListResponse,
    AgentResponse,
    AgentStatsResponse,
    AgentUpdateRequest,
)
from chatter.utils.agent_validation import AgentInputValidator
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    InternalServerProblem,
    NotFoundProblem,
)
from chatter.utils.rate_limiter import get_rate_limiter, RateLimitExceeded

logger = get_logger(__name__)
router = APIRouter()


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
        rate_limiter = get_rate_limiter()
        try:
            await rate_limiter.check_rate_limit(
                f"create_agent:{current_user.id}",
                limit_per_hour=10,  # 10 agents per hour
                limit_per_day=50,   # 50 agents per day
            )
        except RateLimitExceeded as e:
            raise InternalServerProblem(detail=str(e))

        # Validate input data using the input validator
        agent_data.name = AgentInputValidator.validate_agent_name(agent_data.name)
        agent_data.description = AgentInputValidator.validate_agent_name(agent_data.description)  # Same validation rules
        agent_data.system_prompt = AgentInputValidator.validate_agent_message(agent_data.system_prompt)
        agent_data.agent_type = AgentInputValidator.validate_agent_type(agent_data.agent_type)
        agent_data.temperature = AgentInputValidator.validate_temperature(agent_data.temperature)
        agent_data.max_tokens = AgentInputValidator.validate_max_tokens(agent_data.max_tokens)

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
            raise InternalServerProblem(detail=f"Invalid agent configuration: {str(e)}")

        # Get the created agent
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            logger.error("Created agent not found", agent_id=agent_id)
            raise InternalServerProblem(
                detail="Failed to retrieve created agent"
            )

        logger.info("Agent created successfully", 
                   agent_id=agent_id, 
                   agent_name=agent_data.name,
                   created_by=current_user.id)

        return AgentResponse.model_validate(agent.profile.model_dump())

    except InternalServerProblem:
        raise
    except Exception as e:
        logger.error("Failed to create agent", error=str(e), exc_info=True)
        raise InternalServerProblem(
            detail="Failed to create agent"
        ) from e


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    request: AgentListRequest = Depends(),
    current_user: User = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgentListResponse:
    """List all agents with optional filtering and pagination.

    Args:
        request: List request parameters with pagination
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Paginated list of agents
    """
    try:
        # Validate pagination parameters
        offset, limit = AgentInputValidator.validate_pagination_params(
            request.pagination.offset, 
            request.pagination.limit
        )

        # Get agents with filtering
        agents, total = await agent_manager.list_agents(
            agent_type=request.agent_type,
            status=request.status,
            offset=offset,
            limit=limit,
            user_id=current_user.id,  # Filter by user's agents only
        )

        # Additional client-side filtering by tags if specified
        if request.tags:
            filtered_agents = []
            for agent in agents:
                # Check if any of the requested tags match agent tags
                if any(tag in agent.tags for tag in request.tags):
                    filtered_agents.append(agent)
            agents = filtered_agents
            # Note: This changes the total count for this page but not the overall total
            # In a production system, tag filtering should be done at the database level

        # Convert to response format
        agent_responses = []
        for agent in agents:
            try:
                agent_responses.append(AgentResponse.model_validate(agent.model_dump()))
            except Exception as e:
                logger.warning(f"Failed to serialize agent {agent.id}: {e}")
                continue

        # Calculate pagination info
        current_page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 1  # Ceiling division

        logger.info("Listed agents", 
                   count=len(agent_responses), 
                   total=total,
                   page=current_page,
                   user_id=current_user.id)

        return AgentListResponse(
            agents=agent_responses,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error("Failed to list agents", error=str(e), user_id=current_user.id)
        raise InternalServerProblem(
            detail="Failed to list agents"
        ) from e


@router.get("/stats/overview", response_model=AgentStatsResponse)
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
    request: AgentGetRequest = Depends(),
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
        agent_id = AgentInputValidator.validate_agent_id(agent_id)

        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has access to this agent (basic ownership check)
        if hasattr(agent.profile, 'created_by') and agent.profile.created_by != current_user.id and current_user.id != "system":
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
        # Validate agent_id format (UUID)
        import uuid
        try:
            uuid.UUID(agent_id)
        except ValueError:
            raise NotFoundProblem(detail=f"Invalid agent ID format: {agent_id}")

        # First check if agent exists
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has permission to update this agent
        if hasattr(agent.profile, 'created_by') and agent.profile.created_by != current_user.id and current_user.id != "system":
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Update agent using the agent manager
        success = await agent_manager.update_agent(agent_id, agent_data.model_dump(exclude_unset=True))
        
        if not success:
            raise InternalServerProblem(detail="Failed to update agent")

        # Get updated agent
        updated_agent = await agent_manager.get_agent(agent_id)
        if not updated_agent:
            raise InternalServerProblem(detail="Failed to retrieve updated agent")

        return AgentResponse.model_validate(updated_agent.profile.model_dump())

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
        # Validate agent_id format (UUID)
        import uuid
        try:
            uuid.UUID(agent_id)
        except ValueError:
            raise NotFoundProblem(detail=f"Invalid agent ID format: {agent_id}")

        # Check if agent exists and user has permission to delete
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has permission to delete this agent
        if hasattr(agent.profile, 'created_by') and agent.profile.created_by != current_user.id and current_user.id != "system":
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
    "/{agent_id}/interact", response_model=AgentInteractResponse
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
        rate_limiter = get_rate_limiter()
        try:
            await rate_limiter.check_rate_limit(
                f"interact_agent:{current_user.id}:{agent_id}",
                limit_per_hour=100,  # 100 interactions per hour per agent
                limit_per_day=1000,  # 1000 interactions per day per agent
            )
        except RateLimitExceeded as e:
            raise InternalServerProblem(detail=str(e))

        # Validate inputs
        agent_id = AgentInputValidator.validate_agent_id(agent_id)
        conversation_id = AgentInputValidator.validate_conversation_id(interaction_data.conversation_id)
        message = AgentInputValidator.validate_agent_message(interaction_data.message)
        context = AgentInputValidator.sanitize_agent_context(interaction_data.context)

        # Check if agent exists and user has access
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Check if user has permission to interact with this agent
        if hasattr(agent.profile, 'created_by') and agent.profile.created_by != current_user.id and current_user.id != "system":
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
