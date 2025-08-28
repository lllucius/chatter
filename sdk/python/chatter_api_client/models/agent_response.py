import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.agent_status import AgentStatus
from ..models.agent_type import AgentType

if TYPE_CHECKING:
    from ..models.agent_capability import AgentCapability
    from ..models.agent_response_metadata import AgentResponseMetadata


T = TypeVar("T", bound="AgentResponse")


@_attrs_define
class AgentResponse:
    """Response schema for agent data.

    Attributes:
        id (str): Agent ID
        name (str): Agent name
        description (str): Agent description
        agent_type (AgentType): Types of AI agents.
        status (AgentStatus): Agent status.
        system_prompt (str): System prompt
        personality_traits (list[str]): Agent personality traits
        knowledge_domains (list[str]): Knowledge domains
        response_style (str): Response style
        capabilities (list['AgentCapability']): Agent capabilities
        available_tools (list[str]): Available tools
        primary_llm (str): Primary LLM provider
        fallback_llm (str): Fallback LLM provider
        temperature (float): Temperature for responses
        max_tokens (int): Maximum tokens
        max_conversation_length (int): Maximum conversation length
        context_window_size (int): Context window size
        response_timeout (int): Response timeout in seconds
        learning_enabled (bool): Learning enabled
        feedback_weight (float): Feedback weight
        adaptation_threshold (float): Adaptation threshold
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        created_by (str): Creator
        tags (list[str]): Agent tags
        metadata (AgentResponseMetadata): Additional metadata
    """

    id: str
    name: str
    description: str
    agent_type: AgentType
    status: AgentStatus
    system_prompt: str
    personality_traits: list[str]
    knowledge_domains: list[str]
    response_style: str
    capabilities: list["AgentCapability"]
    available_tools: list[str]
    primary_llm: str
    fallback_llm: str
    temperature: float
    max_tokens: int
    max_conversation_length: int
    context_window_size: int
    response_timeout: int
    learning_enabled: bool
    feedback_weight: float
    adaptation_threshold: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
    created_by: str
    tags: list[str]
    metadata: "AgentResponseMetadata"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        agent_type = self.agent_type.value

        status = self.status.value

        system_prompt = self.system_prompt

        personality_traits = self.personality_traits

        knowledge_domains = self.knowledge_domains

        response_style = self.response_style

        capabilities = []
        for capabilities_item_data in self.capabilities:
            capabilities_item = capabilities_item_data.to_dict()
            capabilities.append(capabilities_item)

        available_tools = self.available_tools

        primary_llm = self.primary_llm

        fallback_llm = self.fallback_llm

        temperature = self.temperature

        max_tokens = self.max_tokens

        max_conversation_length = self.max_conversation_length

        context_window_size = self.context_window_size

        response_timeout = self.response_timeout

        learning_enabled = self.learning_enabled

        feedback_weight = self.feedback_weight

        adaptation_threshold = self.adaptation_threshold

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        created_by = self.created_by

        tags = self.tags

        metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "agent_type": agent_type,
                "status": status,
                "system_prompt": system_prompt,
                "personality_traits": personality_traits,
                "knowledge_domains": knowledge_domains,
                "response_style": response_style,
                "capabilities": capabilities,
                "available_tools": available_tools,
                "primary_llm": primary_llm,
                "fallback_llm": fallback_llm,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "max_conversation_length": max_conversation_length,
                "context_window_size": context_window_size,
                "response_timeout": response_timeout,
                "learning_enabled": learning_enabled,
                "feedback_weight": feedback_weight,
                "adaptation_threshold": adaptation_threshold,
                "created_at": created_at,
                "updated_at": updated_at,
                "created_by": created_by,
                "tags": tags,
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_capability import AgentCapability
        from ..models.agent_response_metadata import AgentResponseMetadata

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        agent_type = AgentType(d.pop("agent_type"))

        status = AgentStatus(d.pop("status"))

        system_prompt = d.pop("system_prompt")

        personality_traits = cast(list[str], d.pop("personality_traits"))

        knowledge_domains = cast(list[str], d.pop("knowledge_domains"))

        response_style = d.pop("response_style")

        capabilities = []
        _capabilities = d.pop("capabilities")
        for capabilities_item_data in _capabilities:
            capabilities_item = AgentCapability.from_dict(capabilities_item_data)

            capabilities.append(capabilities_item)

        available_tools = cast(list[str], d.pop("available_tools"))

        primary_llm = d.pop("primary_llm")

        fallback_llm = d.pop("fallback_llm")

        temperature = d.pop("temperature")

        max_tokens = d.pop("max_tokens")

        max_conversation_length = d.pop("max_conversation_length")

        context_window_size = d.pop("context_window_size")

        response_timeout = d.pop("response_timeout")

        learning_enabled = d.pop("learning_enabled")

        feedback_weight = d.pop("feedback_weight")

        adaptation_threshold = d.pop("adaptation_threshold")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        created_by = d.pop("created_by")

        tags = cast(list[str], d.pop("tags"))

        metadata = AgentResponseMetadata.from_dict(d.pop("metadata"))

        agent_response = cls(
            id=id,
            name=name,
            description=description,
            agent_type=agent_type,
            status=status,
            system_prompt=system_prompt,
            personality_traits=personality_traits,
            knowledge_domains=knowledge_domains,
            response_style=response_style,
            capabilities=capabilities,
            available_tools=available_tools,
            primary_llm=primary_llm,
            fallback_llm=fallback_llm,
            temperature=temperature,
            max_tokens=max_tokens,
            max_conversation_length=max_conversation_length,
            context_window_size=context_window_size,
            response_timeout=response_timeout,
            learning_enabled=learning_enabled,
            feedback_weight=feedback_weight,
            adaptation_threshold=adaptation_threshold,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            tags=tags,
            metadata=metadata,
        )

        agent_response.additional_properties = d
        return agent_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
