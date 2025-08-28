from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_type import AgentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_capability import AgentCapability
    from ..models.agent_create_request_metadata import AgentCreateRequestMetadata


T = TypeVar("T", bound="AgentCreateRequest")


@_attrs_define
class AgentCreateRequest:
    """Request schema for creating an agent.

    Attributes:
        name (str): Agent name
        description (str): Agent description
        agent_type (AgentType): Types of AI agents.
        system_prompt (str): System prompt for the agent
        personality_traits (Union[Unset, list[str]]): Agent personality traits
        knowledge_domains (Union[Unset, list[str]]): Knowledge domains
        response_style (Union[Unset, str]): Response style Default: 'professional'.
        capabilities (Union[Unset, list['AgentCapability']]): Agent capabilities
        available_tools (Union[Unset, list[str]]): Available tools
        primary_llm (Union[Unset, str]): Primary LLM provider Default: 'openai'.
        fallback_llm (Union[Unset, str]): Fallback LLM provider Default: 'anthropic'.
        temperature (Union[Unset, float]): Temperature for responses Default: 0.7.
        max_tokens (Union[Unset, int]): Maximum tokens Default: 4096.
        max_conversation_length (Union[Unset, int]): Maximum conversation length Default: 50.
        context_window_size (Union[Unset, int]): Context window size Default: 4000.
        response_timeout (Union[Unset, int]): Response timeout in seconds Default: 30.
        learning_enabled (Union[Unset, bool]): Enable learning from feedback Default: True.
        feedback_weight (Union[Unset, float]): Weight for feedback learning Default: 0.1.
        adaptation_threshold (Union[Unset, float]): Adaptation threshold Default: 0.8.
        tags (Union[Unset, list[str]]): Agent tags
        metadata (Union[Unset, AgentCreateRequestMetadata]): Additional metadata
    """

    name: str
    description: str
    agent_type: AgentType
    system_prompt: str
    personality_traits: Union[Unset, list[str]] = UNSET
    knowledge_domains: Union[Unset, list[str]] = UNSET
    response_style: Union[Unset, str] = "professional"
    capabilities: Union[Unset, list["AgentCapability"]] = UNSET
    available_tools: Union[Unset, list[str]] = UNSET
    primary_llm: Union[Unset, str] = "openai"
    fallback_llm: Union[Unset, str] = "anthropic"
    temperature: Union[Unset, float] = 0.7
    max_tokens: Union[Unset, int] = 4096
    max_conversation_length: Union[Unset, int] = 50
    context_window_size: Union[Unset, int] = 4000
    response_timeout: Union[Unset, int] = 30
    learning_enabled: Union[Unset, bool] = True
    feedback_weight: Union[Unset, float] = 0.1
    adaptation_threshold: Union[Unset, float] = 0.8
    tags: Union[Unset, list[str]] = UNSET
    metadata: Union[Unset, "AgentCreateRequestMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        agent_type = self.agent_type.value

        system_prompt = self.system_prompt

        personality_traits: Union[Unset, list[str]] = UNSET
        if not isinstance(self.personality_traits, Unset):
            personality_traits = self.personality_traits

        knowledge_domains: Union[Unset, list[str]] = UNSET
        if not isinstance(self.knowledge_domains, Unset):
            knowledge_domains = self.knowledge_domains

        response_style = self.response_style

        capabilities: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.capabilities, Unset):
            capabilities = []
            for capabilities_item_data in self.capabilities:
                capabilities_item = capabilities_item_data.to_dict()
                capabilities.append(capabilities_item)

        available_tools: Union[Unset, list[str]] = UNSET
        if not isinstance(self.available_tools, Unset):
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

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "agent_type": agent_type,
                "system_prompt": system_prompt,
            }
        )
        if personality_traits is not UNSET:
            field_dict["personality_traits"] = personality_traits
        if knowledge_domains is not UNSET:
            field_dict["knowledge_domains"] = knowledge_domains
        if response_style is not UNSET:
            field_dict["response_style"] = response_style
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if available_tools is not UNSET:
            field_dict["available_tools"] = available_tools
        if primary_llm is not UNSET:
            field_dict["primary_llm"] = primary_llm
        if fallback_llm is not UNSET:
            field_dict["fallback_llm"] = fallback_llm
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if max_conversation_length is not UNSET:
            field_dict["max_conversation_length"] = max_conversation_length
        if context_window_size is not UNSET:
            field_dict["context_window_size"] = context_window_size
        if response_timeout is not UNSET:
            field_dict["response_timeout"] = response_timeout
        if learning_enabled is not UNSET:
            field_dict["learning_enabled"] = learning_enabled
        if feedback_weight is not UNSET:
            field_dict["feedback_weight"] = feedback_weight
        if adaptation_threshold is not UNSET:
            field_dict["adaptation_threshold"] = adaptation_threshold
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_capability import AgentCapability
        from ..models.agent_create_request_metadata import AgentCreateRequestMetadata

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        agent_type = AgentType(d.pop("agent_type"))

        system_prompt = d.pop("system_prompt")

        personality_traits = cast(list[str], d.pop("personality_traits", UNSET))

        knowledge_domains = cast(list[str], d.pop("knowledge_domains", UNSET))

        response_style = d.pop("response_style", UNSET)

        capabilities = []
        _capabilities = d.pop("capabilities", UNSET)
        for capabilities_item_data in _capabilities or []:
            capabilities_item = AgentCapability.from_dict(capabilities_item_data)

            capabilities.append(capabilities_item)

        available_tools = cast(list[str], d.pop("available_tools", UNSET))

        primary_llm = d.pop("primary_llm", UNSET)

        fallback_llm = d.pop("fallback_llm", UNSET)

        temperature = d.pop("temperature", UNSET)

        max_tokens = d.pop("max_tokens", UNSET)

        max_conversation_length = d.pop("max_conversation_length", UNSET)

        context_window_size = d.pop("context_window_size", UNSET)

        response_timeout = d.pop("response_timeout", UNSET)

        learning_enabled = d.pop("learning_enabled", UNSET)

        feedback_weight = d.pop("feedback_weight", UNSET)

        adaptation_threshold = d.pop("adaptation_threshold", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, AgentCreateRequestMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = AgentCreateRequestMetadata.from_dict(_metadata)

        agent_create_request = cls(
            name=name,
            description=description,
            agent_type=agent_type,
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
            tags=tags,
            metadata=metadata,
        )

        agent_create_request.additional_properties = d
        return agent_create_request

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
