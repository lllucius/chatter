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
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    InternalServerProblem,
    NotFoundProblem,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_agent_manager() -> AgentManager:
    """Get agent manager instance.

    Returns:
        AgentManager instance
    """
    from chatter.core.agents import agent_manager
    return agent_manager


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
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
        # We'll need to adapt this to work with the actual agent manager interface
        # For now, create a placeholder response structure
        agent_id = await agent_manager.create_agent(
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            description=agent_data.description,
            system_prompt=agent_data.system_prompt,
            llm=None,  # This would need to be properly initialized
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
            metadata=agent_data.metadata,
        )

        # Get the created agent
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise InternalServerProblem(detail="Failed to retrieve created agent")

        return AgentResponse.model_validate(agent.profile.model_dump())

    except Exception as e:
        logger.error("Failed to create agent", error=str(e))
        raise InternalServerProblem(detail="Failed to create agent") from e


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
        offset = request.pagination.offset
        limit = request.pagination.limit

        agents, total = await agent_manager.list_agents(
            agent_type=request.agent_type,
            status=request.status,
            offset=offset,
            limit=limit,
        )

        # Filter by tags if specified
        if request.tags:
            filtered_agents = []
            for agent in agents:
                if any(tag in agent.tags for tag in request.tags):
                    filtered_agents.append(agent)
            agents = filtered_agents
            total = len(agents)  # Update total after tag filtering

        agent_responses = [AgentResponse.model_validate(agent.model_dump()) for agent in agents]

        # Calculate pagination info
        current_page = (offset // limit) + 1
        total_pages = (total + limit - 1) // limit  # Ceiling division

        return AgentListResponse(
            agents=agent_responses,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error("Failed to list agents", error=str(e))
        raise InternalServerProblem(detail="Failed to list agents") from e


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
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        return AgentResponse.model_validate(agent.profile.model_dump())

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to get agent", agent_id=agent_id, error=str(e))
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
        # First check if agent exists
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        # Update agent profile with provided data
        profile = agent.profile
        update_data = agent_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        # The agent manager would need an update method - for now we'll simulate it
        # await agent_manager.update_agent(agent_id, profile)

        return AgentResponse.model_validate(profile.model_dump())

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to update agent", agent_id=agent_id, error=str(e))
        raise InternalServerProblem(detail="Failed to update agent") from e


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
        success = await agent_manager.delete_agent(agent_id)

        if not success:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found")

        return AgentDeleteResponse(
            success=True,
            message=f"Agent {agent_id} deleted successfully"
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to delete agent", agent_id=agent_id, error=str(e))
        raise InternalServerProblem(detail="Failed to delete agent") from e


@router.post("/{agent_id}/interact", response_model=AgentInteractResponse)
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
        response = await agent_manager.send_message_to_agent(
            agent_id=agent_id,
            message=interaction_data.message,
            conversation_id=interaction_data.conversation_id,
            context=interaction_data.context,
        )

        if response is None:
            raise NotFoundProblem(detail=f"Agent {agent_id} not found or unable to respond")

        # For now, return a basic response structure
        # In a real implementation, the agent manager would return full interaction details
        from datetime import UTC, datetime

        return AgentInteractResponse(
            agent_id=agent_id,
            response=response,
            conversation_id=interaction_data.conversation_id,
            tools_used=[],  # Would be populated by actual agent response
            confidence_score=0.9,  # Would be calculated by agent
            response_time=1.5,  # Would be measured
            timestamp=datetime.now(UTC),
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to interact with agent", agent_id=agent_id, error=str(e))
        raise InternalServerProblem(detail="Failed to interact with agent") from e


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
        raise InternalServerProblem(detail="Failed to get agent stats") from e
