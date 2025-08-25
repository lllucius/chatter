"""AI Agent framework for creating and managing specialized AI agents."""

import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from chatter.core.langgraph import ConversationState, workflow_manager
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class AgentType(str, Enum):
    """Types of AI agents."""
    CONVERSATIONAL = "conversational"
    TASK_ORIENTED = "task_oriented"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    RESEARCH = "research"
    SUPPORT = "support"
    SPECIALIST = "specialist"


class AgentStatus(str, Enum):
    """Agent status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentCapability(BaseModel):
    """Agent capability definition."""
    name: str
    description: str
    required_tools: list[str] = Field(default_factory=list)
    required_models: list[str] = Field(default_factory=list)
    confidence_threshold: float = 0.7
    enabled: bool = True


class AgentProfile(BaseModel):
    """Agent profile and configuration."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.INACTIVE

    # Behavior configuration
    system_prompt: str
    personality_traits: list[str] = Field(default_factory=list)
    knowledge_domains: list[str] = Field(default_factory=list)
    response_style: str = "professional"

    # Capabilities
    capabilities: list[AgentCapability] = Field(default_factory=list)
    available_tools: list[str] = Field(default_factory=list)

    # Model configuration
    primary_llm: str = "openai"
    fallback_llm: str = "anthropic"
    temperature: float = 0.7
    max_tokens: int = 4096

    # Performance settings
    max_conversation_length: int = 50
    context_window_size: int = 4000
    response_timeout: int = 30

    # Learning and adaptation
    learning_enabled: bool = True
    feedback_weight: float = 0.1
    adaptation_threshold: float = 0.8

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str = "system"
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentInteraction(BaseModel):
    """Record of an agent interaction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    conversation_id: str
    user_message: str
    agent_response: str
    tools_used: list[str] = Field(default_factory=list)
    confidence_score: float
    response_time: float
    feedback_score: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


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
        self.conversation_history: dict[str, list[AgentInteraction]] = {}
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
        logger.info(f"Added tool {tool.name} to agent {self.profile.name}")

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
            logger.info(f"Removed tool {tool_name} from agent {self.profile.name}")
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
        return history[-max_interactions:] if len(history) > max_interactions else history

    async def _update_metrics(self, interaction: AgentInteraction) -> None:
        """Update performance metrics based on interaction.

        Args:
            interaction: Interaction to process
        """
        metrics = self.performance_metrics

        # Update total interactions
        metrics["total_interactions"] += 1

        # Update average confidence
        total_confidence = (
            metrics["average_confidence"] * (metrics["total_interactions"] - 1) +
            interaction.confidence_score
        )
        metrics["average_confidence"] = total_confidence / metrics["total_interactions"]

        # Update average response time
        total_response_time = (
            metrics["average_response_time"] * (metrics["total_interactions"] - 1) +
            interaction.response_time
        )
        metrics["average_response_time"] = total_response_time / metrics["total_interactions"]

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
            logger.warning(f"Interaction {interaction_id} not found for feedback")
            return

        # Update interaction with feedback
        interaction.feedback_score = feedback_score

        # Update performance metrics
        total_feedback = sum(
            inter.feedback_score for conv_history in self.conversation_history.values()
            for inter in conv_history if inter.feedback_score is not None
        )
        feedback_count = sum(
            1 for conv_history in self.conversation_history.values()
            for inter in conv_history if inter.feedback_score is not None
        )

        if feedback_count > 0:
            self.performance_metrics["feedback_score"] = total_feedback / feedback_count

        # Adapt behavior based on feedback
        if self.profile.learning_enabled and feedback_score < self.profile.adaptation_threshold:
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
            self.profile.temperature = max(0.1, self.profile.temperature - 0.1)
        elif feedback_score > 0.8:
            # Good feedback, slightly increase temperature for more creativity
            self.profile.temperature = min(1.0, self.profile.temperature + 0.05)

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
            recent_interactions = await self.get_conversation_context(conversation_id)

            # Build message history
            messages = [SystemMessage(content=self.profile.system_prompt)]

            # Add recent conversation history
            for interaction in recent_interactions:
                messages.append(HumanMessage(content=interaction.user_message))
                messages.append(SystemMessage(content=interaction.agent_response))

            # Add current message
            messages.append(HumanMessage(content=message))

            # Generate response
            response = await self.llm.ainvoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Calculate response time and confidence
            response_time = (datetime.now(UTC) - start_time).total_seconds()
            confidence_score = 0.8  # Default confidence for conversational agents

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
            AgentCapability(
                name="conversation",
                description="Engage in natural conversations",
                confidence_threshold=0.7,
            ),
            AgentCapability(
                name="context_awareness",
                description="Maintain conversation context",
                confidence_threshold=0.8,
            ),
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
            # Create workflow for task execution
            workflow = workflow_manager.create_tool_calling_workflow(
                llm=self.llm,
                tools=list(self.tools.values()),
                system_message=self.profile.system_prompt,
            )

            # Create conversation state
            state: ConversationState = {
                "messages": [HumanMessage(content=message)],
                "user_id": context.get("user_id", "unknown") if context else "unknown",
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
                    last_message.content 
                    if hasattr(last_message, 'content') 
                    else str(last_message)
                )

            if result and "tool_calls" in result:
                tools_used = [call.get("name", "unknown") for call in result["tool_calls"]]

            # Calculate response time and confidence
            response_time = (datetime.now(UTC) - start_time).total_seconds()
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
            AgentCapability(
                name="task_execution",
                description="Execute complex tasks using available tools",
                required_tools=list(self.tools.keys()),
                confidence_threshold=0.8,
            ),
            AgentCapability(
                name="tool_integration",
                description="Integrate multiple tools to complete tasks",
                confidence_threshold=0.7,
            ),
        ]

        # Add tool-specific capabilities
        for tool_name in self.tools:
            capabilities.append(
                AgentCapability(
                    name=f"tool_{tool_name}",
                    description=f"Use {tool_name} tool",
                    required_tools=[tool_name],
                    confidence_threshold=0.9,
                )
            )

        return capabilities


class AgentManager:
    """Manager for creating and orchestrating AI agents."""

    def __init__(self):
        """Initialize the agent manager."""
        self.agents: dict[str, BaseAgent] = {}
        self.agent_classes: dict[AgentType, type[BaseAgent]] = {
            AgentType.CONVERSATIONAL: ConversationalAgent,
            AgentType.TASK_ORIENTED: TaskOrientedAgent,
            # Add more agent types as needed
        }

    async def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        description: str,
        system_prompt: str,
        llm: BaseChatModel,
        **kwargs,
    ) -> str:
        """Create a new AI agent.

        Args:
            name: Agent name
            agent_type: Type of agent to create
            description: Agent description
            system_prompt: System prompt for the agent
            llm: Language model instance
            **kwargs: Additional profile configuration

        Returns:
            Agent ID
        """
        # Create agent profile
        profile = AgentProfile(
            name=name,
            description=description,
            agent_type=agent_type,
            system_prompt=system_prompt,
            status=AgentStatus.ACTIVE,
            **kwargs,
        )

        # Get agent class
        agent_class = self.agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        # Create agent instance
        agent = agent_class(profile=profile, llm=llm)
        self.agents[profile.id] = agent

        logger.info(
            "Created agent",
            agent_id=profile.id,
            name=name,
            agent_type=agent_type,
        )

        return profile.id

    async def get_agent(self, agent_id: str) -> BaseAgent | None:
        """Get an agent by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)

    async def list_agents(
        self,
        agent_type: AgentType | None = None,
        status: AgentStatus | None = None,
    ) -> list[AgentProfile]:
        """List agents with optional filtering.

        Args:
            agent_type: Filter by agent type
            status: Filter by agent status

        Returns:
            List of agent profiles
        """
        profiles = [agent.profile for agent in self.agents.values()]

        if agent_type:
            profiles = [p for p in profiles if p.agent_type == agent_type]

        if status:
            profiles = [p for p in profiles if p.status == status]

        return profiles

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

        return await agent.process_message(message, conversation_id, context)

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
            agent for agent in self.agents.values()
            if agent.profile.status == AgentStatus.ACTIVE
        ]

        if preferred_agent_type:
            suitable_agents = [
                agent for agent in suitable_agents
                if agent.profile.agent_type == preferred_agent_type
            ]

        if not suitable_agents:
            return "No suitable agents are currently available."

        # For now, use the first suitable agent
        # In a real implementation, you might want more sophisticated routing logic
        agent = suitable_agents[0]

        return await agent.process_message(message, conversation_id, context)

    async def get_agent_stats(self) -> dict[str, Any]:
        """Get statistics about all agents.

        Returns:
            Agent statistics
        """
        total_agents = len(self.agents)
        active_agents = sum(
            1 for agent in self.agents.values()
            if agent.profile.status == AgentStatus.ACTIVE
        )

        agent_types = {}
        for agent in self.agents.values():
            agent_type = agent.profile.agent_type.value
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


# Global agent manager instance
agent_manager = AgentManager()
