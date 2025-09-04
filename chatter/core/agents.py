"""AI Agent framework for creating and managing specialized AI agents."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.tools import BaseTool

from chatter.core.langgraph import ConversationState, workflow_manager
from chatter.schemas.agents import (
    AgentCapability,
    AgentInteraction,
    AgentProfile,
    AgentStatus,
    AgentType,
)
from chatter.core.cache_factory import get_general_cache, CacheBackend
from chatter.core.cache_interface import CacheConfig
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, profile: AgentProfile, llm: BaseChatModel):
        """Initialize the agent.

        Args:
            profile: Agent profile and configuration
            llm: Language model instance
        """
        self.profile = profile
        self.llm = llm
        self.tools: dict[str, BaseTool] = {}
        self.conversation_history: dict[str, list[AgentInteraction]] = (
            {}
        )
        self.performance_metrics: dict[str, Any] = {
            "total_interactions": 0,
            "average_confidence": 0.0,
            "average_response_time": 0.0,
            "feedback_score": 0.0,
            "success_rate": 0.0,
        }

    @abstractmethod
    async def process_message(
        self,
        message: str,
        conversation_id: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Process a user message and generate a response.

        Args:
            message: User message
            conversation_id: Conversation identifier
            context: Additional context for processing

        Returns:
            Agent response
        """
        pass

    @abstractmethod
    async def get_capabilities(self) -> list[AgentCapability]:
        """Get the agent's current capabilities.

        Returns:
            List of agent capabilities
        """
        pass

    async def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the agent's toolkit.

        Args:
            tool: Tool to add
        """
        self.tools[tool.name] = tool
        if tool.name not in self.profile.available_tools:
            self.profile.available_tools.append(tool.name)
        logger.info(
            f"Added tool {tool.name} to agent {self.profile.name}"
        )

    async def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from the agent's toolkit.

        Args:
            tool_name: Name of tool to remove

        Returns:
            True if removed, False if not found
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            if tool_name in self.profile.available_tools:
                self.profile.available_tools.remove(tool_name)
            logger.info(
                f"Removed tool {tool_name} from agent {self.profile.name}"
            )
            return True
        return False

    async def update_profile(self, updates: dict[str, Any]) -> None:
        """Update the agent's profile.

        Args:
            updates: Profile updates to apply
        """
        for key, value in updates.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)

        self.profile.updated_at = datetime.now(UTC)
        logger.info(f"Updated profile for agent {self.profile.name}")

    async def record_interaction(
        self,
        conversation_id: str,
        user_message: str,
        agent_response: str,
        tools_used: list[str],
        confidence_score: float,
        response_time: float,
    ) -> AgentInteraction:
        """Record an interaction for learning and metrics.

        Args:
            conversation_id: Conversation identifier
            user_message: User's message
            agent_response: Agent's response
            tools_used: List of tools used
            confidence_score: Confidence in the response
            response_time: Response generation time

        Returns:
            Recorded interaction
        """
        interaction = AgentInteraction(
            agent_id=self.profile.id,
            conversation_id=conversation_id,
            user_message=user_message,
            agent_response=agent_response,
            tools_used=tools_used,
            confidence_score=confidence_score,
            response_time=response_time,
        )

        # Store interaction
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        self.conversation_history[conversation_id].append(interaction)

        # Update metrics
        await self._update_metrics(interaction)

        return interaction

    async def get_conversation_context(
        self, conversation_id: str, max_interactions: int = 10
    ) -> list[AgentInteraction]:
        """Get recent conversation context.

        Args:
            conversation_id: Conversation identifier
            max_interactions: Maximum number of interactions to return

        Returns:
            List of recent interactions
        """
        history = self.conversation_history.get(conversation_id, [])
        return (
            history[-max_interactions:]
            if len(history) > max_interactions
            else history
        )

    async def _update_metrics(
        self, interaction: AgentInteraction
    ) -> None:
        """Update performance metrics based on interaction.

        Args:
            interaction: Interaction to process
        """
        metrics = self.performance_metrics

        # Update total interactions
        metrics["total_interactions"] += 1

        # Update average confidence
        total_confidence = (
            metrics["average_confidence"]
            * (metrics["total_interactions"] - 1)
            + interaction.confidence_score
        )
        metrics["average_confidence"] = (
            total_confidence / metrics["total_interactions"]
        )

        # Update average response time
        total_response_time = (
            metrics["average_response_time"]
            * (metrics["total_interactions"] - 1)
            + interaction.response_time
        )
        metrics["average_response_time"] = (
            total_response_time / metrics["total_interactions"]
        )

    async def learn_from_feedback(
        self, interaction_id: str, feedback_score: float
    ) -> None:
        """Learn from user feedback.

        Args:
            interaction_id: Interaction identifier
            feedback_score: Feedback score (0.0 to 1.0)
        """
        if not self.profile.learning_enabled:
            return

        # Find the interaction
        interaction = None
        for conv_history in self.conversation_history.values():
            for inter in conv_history:
                if inter.id == interaction_id:
                    interaction = inter
                    break
            if interaction:
                break

        if not interaction:
            logger.warning(
                f"Interaction {interaction_id} not found for feedback"
            )
            return

        # Update interaction with feedback
        interaction.feedback_score = feedback_score

        # Update performance metrics
        total_feedback = sum(
            inter.feedback_score
            for conv_history in self.conversation_history.values()
            for inter in conv_history
            if inter.feedback_score is not None
        )
        feedback_count = sum(
            1
            for conv_history in self.conversation_history.values()
            for inter in conv_history
            if inter.feedback_score is not None
        )

        if feedback_count > 0:
            self.performance_metrics["feedback_score"] = (
                total_feedback / feedback_count
            )

        # Adapt behavior based on feedback
        if (
            self.profile.learning_enabled
            and feedback_score < self.profile.adaptation_threshold
        ):
            await self._adapt_behavior(interaction, feedback_score)

        logger.info(
            f"Recorded feedback for agent {self.profile.name}",
            interaction_id=interaction_id,
            feedback_score=feedback_score,
        )

    async def _adapt_behavior(
        self, interaction: AgentInteraction, feedback_score: float
    ) -> None:
        """Adapt agent behavior based on poor feedback.

        Args:
            interaction: Interaction that received poor feedback
            feedback_score: The feedback score received
        """
        # Simple adaptation: adjust temperature based on feedback
        if feedback_score < 0.5:
            # Poor feedback, reduce temperature for more deterministic responses
            self.profile.temperature = max(
                0.1, self.profile.temperature - 0.1
            )
        elif feedback_score > 0.8:
            # Good feedback, slightly increase temperature for more creativity
            self.profile.temperature = min(
                1.0, self.profile.temperature + 0.05
            )

        logger.info(
            f"Adapted behavior for agent {self.profile.name}",
            new_temperature=self.profile.temperature,
            feedback_score=feedback_score,
        )


class ConversationalAgent(BaseAgent):
    """General conversational AI agent."""

    async def process_message(
        self,
        message: str,
        conversation_id: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Process a conversational message."""
        start_time = datetime.now(UTC)

        try:
            # Get conversation context
            recent_interactions = await self.get_conversation_context(
                conversation_id
            )

            # Build message history
            messages: list[BaseMessage] = [
                SystemMessage(content=self.profile.system_message)
            ]

            # Add recent conversation history
            for interaction in recent_interactions:
                messages.append(
                    HumanMessage(content=interaction.user_message)
                )
                messages.append(
                    SystemMessage(content=interaction.agent_response)
                )

            # Add current message
            messages.append(HumanMessage(content=message))

            # Generate response
            response = await self.llm.ainvoke(messages)
            response_text = (
                str(response.content)
                if hasattr(response, 'content')
                else str(response)
            )

            # Calculate response time and confidence
            response_time = (
                datetime.now(UTC) - start_time
            ).total_seconds()
            confidence_score = (
                0.8  # Default confidence for conversational agents
            )

            # Record interaction
            await self.record_interaction(
                conversation_id=conversation_id,
                user_message=message,
                agent_response=response_text,
                tools_used=[],
                confidence_score=confidence_score,
                response_time=response_time,
            )

            return response_text

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I apologize, but I encountered an error processing your request."

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get conversational agent capabilities."""
        return [
            AgentCapability.NATURAL_LANGUAGE,
            AgentCapability.MEMORY,
        ]


class TaskOrientedAgent(BaseAgent):
    """Task-oriented AI agent with tool usage."""

    async def process_message(
        self,
        message: str,
        conversation_id: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Process a task-oriented message with potential tool usage."""
        start_time = datetime.now(UTC)
        tools_used = []

        try:
            # Create workflow for task execution using unified API
            workflow = workflow_manager.create_workflow(
                llm=self.llm,
                mode="tools",
                system_message=self.profile.system_message,
                tools=list(self.tools.values()),
            )

            # Create conversation state
            state: ConversationState = {
                "messages": [HumanMessage(content=message)],
                "user_id": (
                    context.get("user_id", "unknown")
                    if context
                    else "unknown"
                ),
                "conversation_id": conversation_id,
                "retrieval_context": None,
                "tool_calls": [],
                "metadata": {},
                "conversation_summary": None,
                "parent_conversation_id": None,
                "branch_id": None,
                "memory_context": {},
                "workflow_template": None,
                "a_b_test_group": None,
            }

            # Execute workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=state,
                thread_id=conversation_id,
            )

            # Extract response and tools used
            response_text = ""
            if result and "messages" in result:
                last_message = result["messages"][-1]
                response_text = (
                    str(last_message.content)
                    if hasattr(last_message, 'content')
                    else str(last_message)
                )

            if result and "tool_calls" in result:
                tools_used = [
                    call.get("name", "unknown")
                    for call in result["tool_calls"]
                ]

            # Calculate response time and confidence
            response_time = (
                datetime.now(UTC) - start_time
            ).total_seconds()
            confidence_score = 0.9 if tools_used else 0.7

            # Record interaction
            await self.record_interaction(
                conversation_id=conversation_id,
                user_message=message,
                agent_response=response_text,
                tools_used=tools_used,
                confidence_score=confidence_score,
                response_time=response_time,
            )

            return response_text

        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return "I apologize, but I encountered an error while processing your task."

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get task-oriented agent capabilities."""
        capabilities = [
            AgentCapability.TOOL_USE,
            AgentCapability.NATURAL_LANGUAGE,
        ]

        # Add capabilities based on available tools
        if self.tools:
            capabilities.append(AgentCapability.ANALYTICAL)

        return capabilities


class AgentManager:
    """Manager for creating and orchestrating AI agents."""

    def __init__(self):
        """Initialize the agent manager."""
        self.agents: dict[str, BaseAgent] = {}
        self.registry = AgentRegistry()
        self.cache = get_general_cache(
            backend=CacheBackend.MULTI_TIER,  # Use multi-tier for fallback to memory
            config=CacheConfig(key_prefix="agents:")
        )
        self.agent_classes: dict[AgentType, type[BaseAgent]] = {
            AgentType.CONVERSATIONAL: ConversationalAgent,
            AgentType.TASK_ORIENTED: TaskOrientedAgent,
            AgentType.SPECIALIST: SpecializedAgent,
            # Add more agent types as needed
        }

        # Register agent types in the registry
        for agent_type, agent_class in self.agent_classes.items():
            self.registry.register_agent_type(
                agent_type.value, agent_class
            )

    async def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        description: str,
        system_message: str,
        llm: BaseChatModel | None = None,
        created_by: str = "system",
        **kwargs: Any,
    ) -> str:
        """Create a new AI agent.

        Args:
            name: Agent name
            agent_type: Type of agent to create
            description: Agent description
            system_message: System message for the agent
            llm: Language model instance
            created_by: ID of user creating the agent
            **kwargs: Additional profile configuration

        Returns:
            Agent ID
        """
        # Create agent profile
        profile = AgentProfile(
            name=name,
            description=description,
            type=agent_type,
            system_message=system_message,
            status=AgentStatus.ACTIVE,
            created_by=created_by,
            **kwargs,
        )

        # Get agent class
        agent_class = self.agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        # Create default LLM if not provided
        if llm is None:
            llm = await self._create_default_llm(profile.primary_llm)

        # Create agent instance
        agent = agent_class(profile=profile, llm=llm)
        self.agents[profile.id] = agent

        # Cache the agent profile
        try:
            await self.cache.set(
                f"profile:{profile.id}",
                profile.model_dump(),
                ttl=3600  # Cache for 1 hour
            )
        except Exception as e:
            logger.warning(f"Failed to cache agent profile: {e}")

        logger.info(
            "Created agent",
            agent_id=profile.id,
            name=name,
            type=agent_type,
            created_by=created_by,
        )

        return profile.id

    async def _create_default_llm(self, provider: str = "openai") -> BaseChatModel:
        """Create a default LLM instance.
        
        Args:
            provider: LLM provider name
            
        Returns:
            BaseChatModel instance
        """
        # Import here to avoid circular imports
        try:
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.7,
                    max_tokens=4096,
                )
            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    temperature=0.7,
                    max_tokens=4096,
                )
            else:
                # Fallback to a mock LLM for testing
                from langchain_core.language_models.fake import FakeListChatModel
                return FakeListChatModel(responses=["I'm a test response."])
        except ImportError as e:
            logger.warning(f"Failed to import {provider} LLM: {e}, using fake LLM")
            from langchain_core.language_models.fake import FakeListChatModel
            return FakeListChatModel(responses=["I'm a test response."])

    async def get_agent(self, agent_id: str) -> BaseAgent | None:
        """Get an agent by ID with caching.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent instance or None if not found
        """
        # Try to get from in-memory cache first
        if agent_id in self.agents:
            return self.agents[agent_id]

        # Try to get from external cache
        try:
            cached_profile = await self.cache.get(f"profile:{agent_id}")
            if cached_profile:
                # Reconstruct agent from cached profile
                profile = AgentProfile.model_validate(cached_profile)
                agent_class = self.agent_classes.get(profile.type)
                if agent_class:
                    llm = await self._create_default_llm(profile.primary_llm)
                    agent = agent_class(profile=profile, llm=llm)
                    self.agents[agent_id] = agent  # Cache in memory
                    return agent
        except Exception as e:
            logger.warning(f"Failed to retrieve agent from cache: {e}")

        return None

    async def list_agents(
        self,
        agent_type: AgentType | None = None,
        status: AgentStatus | None = None,
        offset: int = 0,
        limit: int = 50,
        user_id: str | None = None,
    ) -> tuple[list[AgentProfile], int]:
        """List agents with optional filtering and pagination.

        Args:
            agent_type: Filter by agent type
            status: Filter by agent status
            offset: Number of items to skip
            limit: Maximum number of items to return
            user_id: Filter by user who created the agent

        Returns:
            Tuple of (list of agent profiles, total count)
        """
        profiles = [agent.profile for agent in self.agents.values()]

        # Apply filters
        if agent_type:
            profiles = [p for p in profiles if p.type == agent_type]

        if status:
            profiles = [p for p in profiles if p.status == status]

        if user_id:
            profiles = [p for p in profiles if getattr(p, 'created_by', None) == user_id]

        total = len(profiles)

        # Apply pagination
        paginated_profiles = profiles[offset : offset + limit]

        return paginated_profiles, total

    async def update_agent(self, agent_id: str, update_data: dict[str, Any]) -> bool:
        """Update an agent's configuration.

        Args:
            agent_id: Agent identifier
            update_data: Dictionary of fields to update

        Returns:
            True if updated successfully, False if agent not found
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        try:
            # Update agent profile
            await agent.update_profile(update_data)
            
            # If LLM-related fields changed, recreate LLM
            llm_fields = {'primary_llm', 'fallback_llm', 'temperature', 'max_tokens'}
            if any(field in update_data for field in llm_fields):
                new_llm = await self._create_default_llm(agent.profile.primary_llm)
                agent.llm = new_llm

            # Update cache
            try:
                await self.cache.set(
                    f"profile:{agent_id}",
                    agent.profile.model_dump(),
                    ttl=3600
                )
            except Exception as e:
                logger.warning(f"Failed to update agent cache: {e}")

            logger.info(
                "Updated agent",
                agent_id=agent_id,
                updated_fields=list(update_data.keys()),
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update agent {agent_id}: {e}")
            return False

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if deleted, False if not found
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.profile.status = AgentStatus.INACTIVE
            del self.agents[agent_id]
            
            # Remove from cache
            try:
                await self.cache.delete(f"profile:{agent_id}")
            except Exception as e:
                logger.warning(f"Failed to remove agent from cache: {e}")
            
            logger.info(f"Deleted agent {agent_id}")
            return True
        return False

    async def send_message_to_agent(
        self,
        agent_id: str,
        message: str,
        conversation_id: str,
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """Send a message to a specific agent.

        Args:
            agent_id: Agent identifier
            message: Message to send
            conversation_id: Conversation identifier
            context: Additional context

        Returns:
            Agent response or None if agent not found
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        if agent.profile.status != AgentStatus.ACTIVE:
            return "Agent is currently unavailable."

        return await agent.process_message(
            message, conversation_id, context
        )

    async def route_message(
        self,
        message: str,
        conversation_id: str,
        context: dict[str, Any] | None = None,
        preferred_agent_type: AgentType | None = None,
    ) -> str:
        """Route a message to the most appropriate agent.

        Args:
            message: Message to route
            conversation_id: Conversation identifier
            context: Additional context
            preferred_agent_type: Preferred agent type

        Returns:
            Agent response
        """
        # Find suitable agents
        suitable_agents = [
            agent
            for agent in self.agents.values()
            if agent.profile.status == AgentStatus.ACTIVE
        ]

        if preferred_agent_type:
            suitable_agents = [
                agent
                for agent in suitable_agents
                if agent.profile.type == preferred_agent_type
            ]

        if not suitable_agents:
            return "No suitable agents are currently available."

        # For now, use the first suitable agent
        # In a real implementation, you might want more sophisticated routing logic
        agent = suitable_agents[0]

        return await agent.process_message(
            message, conversation_id, context
        )

    async def get_agent_stats(self) -> dict[str, Any]:
        """Get statistics about all agents.

        Returns:
            Agent statistics
        """
        total_agents = len(self.agents)
        active_agents = sum(
            1
            for agent in self.agents.values()
            if agent.profile.status == AgentStatus.ACTIVE
        )

        agent_types = {}
        for agent in self.agents.values():
            agent_type = agent.profile.type.value
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1

        total_interactions = sum(
            agent.performance_metrics.get("total_interactions", 0)
            for agent in self.agents.values()
        )

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "agent_types": agent_types,
            "total_interactions": total_interactions,
        }


class AgentRegistry:
    """Registry for managing agent types and instances."""

    def __init__(self):
        """Initialize the agent registry."""
        self.agent_types: dict[str, type[BaseAgent]] = {}
        self.agent_instances: dict[str, BaseAgent] = {}

    def register_agent_type(
        self, name: str, agent_class: type[BaseAgent]
    ) -> None:
        """Register an agent type.

        Args:
            name: Name of the agent type
            agent_class: Agent class to register
        """
        self.agent_types[name] = agent_class

    def get_agent_type(self, name: str) -> type[BaseAgent] | None:
        """Get an agent type by name.

        Args:
            name: Name of the agent type

        Returns:
            Agent class or None if not found
        """
        return self.agent_types.get(name)

    def list_agent_types(self) -> list[str]:
        """List all registered agent types.

        Returns:
            List of agent type names
        """
        return list(self.agent_types.keys())


class AgentExecutor:
    """Executor for running agent tasks."""

    def __init__(self):
        """Initialize the agent executor."""
        self.active_tasks: dict[str, Any] = {}

    async def execute_agent_task(
        self,
        agent: BaseAgent,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a task with an agent.

        Args:
            agent: The agent to execute the task
            task: Task description
            context: Optional context for the task

        Returns:
            Task execution result
        """
        task_id = f"task_{len(self.active_tasks)}"
        self.active_tasks[task_id] = {
            "agent": agent,
            "task": task,
            "context": context or {},
            "status": "running",
        }

        try:
            # Execute the task through the agent
            result = await agent.process_message(task, context or {})
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["result"] = result
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
            }
        except Exception as e:
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = str(e)
            raise

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get the status of a task.

        Args:
            task_id: ID of the task

        Returns:
            Task status or None if not found
        """
        return self.active_tasks.get(task_id)


class SpecializedAgent(BaseAgent):
    """Specialized agent with domain expertise."""

    def __init__(self, profile: AgentProfile, llm: BaseChatModel):
        """Initialize the specialized agent.

        Args:
            profile: Agent profile and configuration
            llm: Language model instance
        """
        super().__init__(profile, llm)
        self.specialization = getattr(
            profile, 'specialization', 'general'
        )
        self.domain_knowledge: dict[str, Any] = {}

    async def process_message(
        self,
        message: str,
        conversation_id: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Process a message with specialized domain knowledge.

        Args:
            message: Input message to process
            conversation_id: Conversation identifier
            context: Additional context for processing

        Returns:
            Agent response
        """
        context = context or {}

        # Add specialized context
        specialized_context = {
            **context,
            "specialization": self.specialization,
            "domain_knowledge": self.domain_knowledge,
        }

        # Build specialized system message
        system_message = SystemMessage(
            content=f"{self.profile.system_message}\n"
            f"You are specialized in: {self.specialization}"
        )

        # Create messages for processing
        messages = [system_message, HumanMessage(content=message)]

        try:
            # Process with LLM
            response = await self.llm.ainvoke(messages)

            # Calculate confidence based on specialization match
            confidence = self._calculate_specialized_confidence(
                message, specialized_context
            )

            # Record interaction
            await self.record_interaction(
                conversation_id=conversation_id,
                user_message=message,
                agent_response=(
                    str(response.content)
                    if hasattr(response, 'content')
                    else str(response)
                ),
                tools_used=[],
                confidence_score=confidence,
                response_time=1.0,  # Default response time
            )

            return (
                str(response.content)
                if hasattr(response, 'content')
                else str(response)
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I apologize, but I encountered an error processing your request."

    def _calculate_specialized_confidence(
        self, message: str, context: dict[str, Any]
    ) -> float:
        """Calculate confidence score based on specialization match.

        Args:
            message: Input message
            context: Processing context

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Simple specialization-based confidence calculation
        base_confidence = 0.7

        # Boost confidence if message matches specialization
        if self.specialization.lower() in message.lower():
            base_confidence += 0.2

        # Cap at 1.0
        return min(base_confidence, 1.0)

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get specialized agent capabilities.

        Returns:
            List of agent capabilities based on specialization
        """
        base_capabilities = [
            AgentCapability.NATURAL_LANGUAGE,
            AgentCapability.ANALYTICAL,
        ]

        # Add capabilities based on specialization
        if self.specialization.lower() in [
            "programming",
            "code",
            "software",
        ]:
            base_capabilities.append(AgentCapability.CODE_GENERATION)
            base_capabilities.append(AgentCapability.TOOL_USE)
        elif self.specialization.lower() in ["research", "analysis"]:
            base_capabilities.append(AgentCapability.RESEARCH)
            base_capabilities.append(AgentCapability.ANALYTICAL)
        elif self.specialization.lower() in ["creative", "writing"]:
            base_capabilities.append(AgentCapability.CREATIVE)
        elif self.specialization.lower() in ["support", "help"]:
            base_capabilities.append(AgentCapability.SUPPORT)

        # Remove duplicates
        return list(set(base_capabilities))


# Global agent manager instance
agent_manager = AgentManager()


# Alias for backward compatibility and common usage
Agent = BaseAgent
