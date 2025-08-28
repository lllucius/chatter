from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_status import AgentStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_capability import AgentCapability
    from ..models.agent_update_request_metadata_type_0 import AgentUpdateRequestMetadataType0


T = TypeVar("T", bound="AgentUpdateRequest")


@_attrs_define
class AgentUpdateRequest:
    """Request schema for updating an agent.

    Attributes:
        name (Union[None, Unset, str]): Agent name
        description (Union[None, Unset, str]): Agent description
        system_prompt (Union[None, Unset, str]): System prompt for the agent
        status (Union[AgentStatus, None, Unset]): Agent status
        personality_traits (Union[None, Unset, list[str]]): Agent personality traits
        knowledge_domains (Union[None, Unset, list[str]]): Knowledge domains
        response_style (Union[None, Unset, str]): Response style
        capabilities (Union[None, Unset, list['AgentCapability']]): Agent capabilities
        available_tools (Union[None, Unset, list[str]]): Available tools
        primary_llm (Union[None, Unset, str]): Primary LLM provider
        fallback_llm (Union[None, Unset, str]): Fallback LLM provider
        temperature (Union[None, Unset, float]): Temperature for responses
        max_tokens (Union[None, Unset, int]): Maximum tokens
        max_conversation_length (Union[None, Unset, int]): Maximum conversation length
        context_window_size (Union[None, Unset, int]): Context window size
        response_timeout (Union[None, Unset, int]): Response timeout in seconds
        learning_enabled (Union[None, Unset, bool]): Enable learning from feedback
        feedback_weight (Union[None, Unset, float]): Weight for feedback learning
        adaptation_threshold (Union[None, Unset, float]): Adaptation threshold
        tags (Union[None, Unset, list[str]]): Agent tags
        metadata (Union['AgentUpdateRequestMetadataType0', None, Unset]): Additional metadata
    """

    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    system_prompt: Union[None, Unset, str] = UNSET
    status: Union[AgentStatus, None, Unset] = UNSET
    personality_traits: Union[None, Unset, list[str]] = UNSET
    knowledge_domains: Union[None, Unset, list[str]] = UNSET
    response_style: Union[None, Unset, str] = UNSET
    capabilities: Union[None, Unset, list["AgentCapability"]] = UNSET
    available_tools: Union[None, Unset, list[str]] = UNSET
    primary_llm: Union[None, Unset, str] = UNSET
    fallback_llm: Union[None, Unset, str] = UNSET
    temperature: Union[None, Unset, float] = UNSET
    max_tokens: Union[None, Unset, int] = UNSET
    max_conversation_length: Union[None, Unset, int] = UNSET
    context_window_size: Union[None, Unset, int] = UNSET
    response_timeout: Union[None, Unset, int] = UNSET
    learning_enabled: Union[None, Unset, bool] = UNSET
    feedback_weight: Union[None, Unset, float] = UNSET
    adaptation_threshold: Union[None, Unset, float] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    metadata: Union["AgentUpdateRequestMetadataType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.agent_update_request_metadata_type_0 import AgentUpdateRequestMetadataType0

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        system_prompt: Union[None, Unset, str]
        if isinstance(self.system_prompt, Unset):
            system_prompt = UNSET
        else:
            system_prompt = self.system_prompt

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, AgentStatus):
            status = self.status.value
        else:
            status = self.status

        personality_traits: Union[None, Unset, list[str]]
        if isinstance(self.personality_traits, Unset):
            personality_traits = UNSET
        elif isinstance(self.personality_traits, list):
            personality_traits = self.personality_traits

        else:
            personality_traits = self.personality_traits

        knowledge_domains: Union[None, Unset, list[str]]
        if isinstance(self.knowledge_domains, Unset):
            knowledge_domains = UNSET
        elif isinstance(self.knowledge_domains, list):
            knowledge_domains = self.knowledge_domains

        else:
            knowledge_domains = self.knowledge_domains

        response_style: Union[None, Unset, str]
        if isinstance(self.response_style, Unset):
            response_style = UNSET
        else:
            response_style = self.response_style

        capabilities: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.capabilities, Unset):
            capabilities = UNSET
        elif isinstance(self.capabilities, list):
            capabilities = []
            for capabilities_type_0_item_data in self.capabilities:
                capabilities_type_0_item = capabilities_type_0_item_data.to_dict()
                capabilities.append(capabilities_type_0_item)

        else:
            capabilities = self.capabilities

        available_tools: Union[None, Unset, list[str]]
        if isinstance(self.available_tools, Unset):
            available_tools = UNSET
        elif isinstance(self.available_tools, list):
            available_tools = self.available_tools

        else:
            available_tools = self.available_tools

        primary_llm: Union[None, Unset, str]
        if isinstance(self.primary_llm, Unset):
            primary_llm = UNSET
        else:
            primary_llm = self.primary_llm

        fallback_llm: Union[None, Unset, str]
        if isinstance(self.fallback_llm, Unset):
            fallback_llm = UNSET
        else:
            fallback_llm = self.fallback_llm

        temperature: Union[None, Unset, float]
        if isinstance(self.temperature, Unset):
            temperature = UNSET
        else:
            temperature = self.temperature

        max_tokens: Union[None, Unset, int]
        if isinstance(self.max_tokens, Unset):
            max_tokens = UNSET
        else:
            max_tokens = self.max_tokens

        max_conversation_length: Union[None, Unset, int]
        if isinstance(self.max_conversation_length, Unset):
            max_conversation_length = UNSET
        else:
            max_conversation_length = self.max_conversation_length

        context_window_size: Union[None, Unset, int]
        if isinstance(self.context_window_size, Unset):
            context_window_size = UNSET
        else:
            context_window_size = self.context_window_size

        response_timeout: Union[None, Unset, int]
        if isinstance(self.response_timeout, Unset):
            response_timeout = UNSET
        else:
            response_timeout = self.response_timeout

        learning_enabled: Union[None, Unset, bool]
        if isinstance(self.learning_enabled, Unset):
            learning_enabled = UNSET
        else:
            learning_enabled = self.learning_enabled

        feedback_weight: Union[None, Unset, float]
        if isinstance(self.feedback_weight, Unset):
            feedback_weight = UNSET
        else:
            feedback_weight = self.feedback_weight

        adaptation_threshold: Union[None, Unset, float]
        if isinstance(self.adaptation_threshold, Unset):
            adaptation_threshold = UNSET
        else:
            adaptation_threshold = self.adaptation_threshold

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, AgentUpdateRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if status is not UNSET:
            field_dict["status"] = status
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
        from ..models.agent_update_request_metadata_type_0 import AgentUpdateRequestMetadataType0

        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_system_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        system_prompt = _parse_system_prompt(d.pop("system_prompt", UNSET))

        def _parse_status(data: object) -> Union[AgentStatus, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = AgentStatus(data)

                return status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[AgentStatus, None, Unset], data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_personality_traits(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                personality_traits_type_0 = cast(list[str], data)

                return personality_traits_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        personality_traits = _parse_personality_traits(d.pop("personality_traits", UNSET))

        def _parse_knowledge_domains(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                knowledge_domains_type_0 = cast(list[str], data)

                return knowledge_domains_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        knowledge_domains = _parse_knowledge_domains(d.pop("knowledge_domains", UNSET))

        def _parse_response_style(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        response_style = _parse_response_style(d.pop("response_style", UNSET))

        def _parse_capabilities(data: object) -> Union[None, Unset, list["AgentCapability"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                capabilities_type_0 = []
                _capabilities_type_0 = data
                for capabilities_type_0_item_data in _capabilities_type_0:
                    capabilities_type_0_item = AgentCapability.from_dict(capabilities_type_0_item_data)

                    capabilities_type_0.append(capabilities_type_0_item)

                return capabilities_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["AgentCapability"]], data)

        capabilities = _parse_capabilities(d.pop("capabilities", UNSET))

        def _parse_available_tools(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                available_tools_type_0 = cast(list[str], data)

                return available_tools_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        available_tools = _parse_available_tools(d.pop("available_tools", UNSET))

        def _parse_primary_llm(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        primary_llm = _parse_primary_llm(d.pop("primary_llm", UNSET))

        def _parse_fallback_llm(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        fallback_llm = _parse_fallback_llm(d.pop("fallback_llm", UNSET))

        def _parse_temperature(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        temperature = _parse_temperature(d.pop("temperature", UNSET))

        def _parse_max_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_tokens = _parse_max_tokens(d.pop("max_tokens", UNSET))

        def _parse_max_conversation_length(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_conversation_length = _parse_max_conversation_length(d.pop("max_conversation_length", UNSET))

        def _parse_context_window_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        context_window_size = _parse_context_window_size(d.pop("context_window_size", UNSET))

        def _parse_response_timeout(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        response_timeout = _parse_response_timeout(d.pop("response_timeout", UNSET))

        def _parse_learning_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        learning_enabled = _parse_learning_enabled(d.pop("learning_enabled", UNSET))

        def _parse_feedback_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        feedback_weight = _parse_feedback_weight(d.pop("feedback_weight", UNSET))

        def _parse_adaptation_threshold(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        adaptation_threshold = _parse_adaptation_threshold(d.pop("adaptation_threshold", UNSET))

        def _parse_tags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        tags = _parse_tags(d.pop("tags", UNSET))

        def _parse_metadata(data: object) -> Union["AgentUpdateRequestMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = AgentUpdateRequestMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["AgentUpdateRequestMetadataType0", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        agent_update_request = cls(
            name=name,
            description=description,
            system_prompt=system_prompt,
            status=status,
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

        agent_update_request.additional_properties = d
        return agent_update_request

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
