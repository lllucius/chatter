from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.profile_type import ProfileType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.profile_create_extra_metadata_type_0 import ProfileCreateExtraMetadataType0
    from ..models.profile_create_logit_bias_type_0 import ProfileCreateLogitBiasType0


T = TypeVar("T", bound="ProfileCreate")


@_attrs_define
class ProfileCreate:
    """Schema for creating a profile.

    Attributes:
        name (str): Profile name
        llm_provider (str): LLM provider (openai, anthropic, etc.)
        llm_model (str): LLM model name
        description (Union[None, Unset, str]): Profile description
        profile_type (Union[Unset, ProfileType]): Enumeration for profile types.
        temperature (Union[Unset, float]): Temperature for generation Default: 0.7.
        top_p (Union[None, Unset, float]): Top-p sampling parameter
        top_k (Union[None, Unset, int]): Top-k sampling parameter
        max_tokens (Union[Unset, int]): Maximum tokens to generate Default: 4096.
        presence_penalty (Union[None, Unset, float]): Presence penalty
        frequency_penalty (Union[None, Unset, float]): Frequency penalty
        context_window (Union[Unset, int]): Context window size Default: 4096.
        system_prompt (Union[None, Unset, str]): System prompt template
        memory_enabled (Union[Unset, bool]): Enable conversation memory Default: True.
        memory_strategy (Union[None, Unset, str]): Memory management strategy
        enable_retrieval (Union[Unset, bool]): Enable document retrieval Default: False.
        retrieval_limit (Union[Unset, int]): Number of documents to retrieve Default: 5.
        retrieval_score_threshold (Union[Unset, float]): Minimum retrieval score Default: 0.7.
        enable_tools (Union[Unset, bool]): Enable tool calling Default: False.
        available_tools (Union[None, Unset, list[str]]): List of available tools
        tool_choice (Union[None, Unset, str]): Tool choice strategy
        content_filter_enabled (Union[Unset, bool]): Enable content filtering Default: True.
        safety_level (Union[None, Unset, str]): Safety level
        response_format (Union[None, Unset, str]): Response format (json, text, markdown)
        stream_response (Union[Unset, bool]): Enable streaming responses Default: True.
        seed (Union[None, Unset, int]): Random seed for reproducibility
        stop_sequences (Union[None, Unset, list[str]]): Stop sequences
        logit_bias (Union['ProfileCreateLogitBiasType0', None, Unset]): Logit bias adjustments
        embedding_provider (Union[None, Unset, str]): Embedding provider
        embedding_model (Union[None, Unset, str]): Embedding model
        is_public (Union[Unset, bool]): Whether profile is public Default: False.
        tags (Union[None, Unset, list[str]]): Profile tags
        extra_metadata (Union['ProfileCreateExtraMetadataType0', None, Unset]): Additional metadata
    """

    name: str
    llm_provider: str
    llm_model: str
    description: Union[None, Unset, str] = UNSET
    profile_type: Union[Unset, ProfileType] = UNSET
    temperature: Union[Unset, float] = 0.7
    top_p: Union[None, Unset, float] = UNSET
    top_k: Union[None, Unset, int] = UNSET
    max_tokens: Union[Unset, int] = 4096
    presence_penalty: Union[None, Unset, float] = UNSET
    frequency_penalty: Union[None, Unset, float] = UNSET
    context_window: Union[Unset, int] = 4096
    system_prompt: Union[None, Unset, str] = UNSET
    memory_enabled: Union[Unset, bool] = True
    memory_strategy: Union[None, Unset, str] = UNSET
    enable_retrieval: Union[Unset, bool] = False
    retrieval_limit: Union[Unset, int] = 5
    retrieval_score_threshold: Union[Unset, float] = 0.7
    enable_tools: Union[Unset, bool] = False
    available_tools: Union[None, Unset, list[str]] = UNSET
    tool_choice: Union[None, Unset, str] = UNSET
    content_filter_enabled: Union[Unset, bool] = True
    safety_level: Union[None, Unset, str] = UNSET
    response_format: Union[None, Unset, str] = UNSET
    stream_response: Union[Unset, bool] = True
    seed: Union[None, Unset, int] = UNSET
    stop_sequences: Union[None, Unset, list[str]] = UNSET
    logit_bias: Union["ProfileCreateLogitBiasType0", None, Unset] = UNSET
    embedding_provider: Union[None, Unset, str] = UNSET
    embedding_model: Union[None, Unset, str] = UNSET
    is_public: Union[Unset, bool] = False
    tags: Union[None, Unset, list[str]] = UNSET
    extra_metadata: Union["ProfileCreateExtraMetadataType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.profile_create_extra_metadata_type_0 import ProfileCreateExtraMetadataType0
        from ..models.profile_create_logit_bias_type_0 import ProfileCreateLogitBiasType0

        name = self.name

        llm_provider = self.llm_provider

        llm_model = self.llm_model

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        profile_type: Union[Unset, str] = UNSET
        if not isinstance(self.profile_type, Unset):
            profile_type = self.profile_type.value

        temperature = self.temperature

        top_p: Union[None, Unset, float]
        if isinstance(self.top_p, Unset):
            top_p = UNSET
        else:
            top_p = self.top_p

        top_k: Union[None, Unset, int]
        if isinstance(self.top_k, Unset):
            top_k = UNSET
        else:
            top_k = self.top_k

        max_tokens = self.max_tokens

        presence_penalty: Union[None, Unset, float]
        if isinstance(self.presence_penalty, Unset):
            presence_penalty = UNSET
        else:
            presence_penalty = self.presence_penalty

        frequency_penalty: Union[None, Unset, float]
        if isinstance(self.frequency_penalty, Unset):
            frequency_penalty = UNSET
        else:
            frequency_penalty = self.frequency_penalty

        context_window = self.context_window

        system_prompt: Union[None, Unset, str]
        if isinstance(self.system_prompt, Unset):
            system_prompt = UNSET
        else:
            system_prompt = self.system_prompt

        memory_enabled = self.memory_enabled

        memory_strategy: Union[None, Unset, str]
        if isinstance(self.memory_strategy, Unset):
            memory_strategy = UNSET
        else:
            memory_strategy = self.memory_strategy

        enable_retrieval = self.enable_retrieval

        retrieval_limit = self.retrieval_limit

        retrieval_score_threshold = self.retrieval_score_threshold

        enable_tools = self.enable_tools

        available_tools: Union[None, Unset, list[str]]
        if isinstance(self.available_tools, Unset):
            available_tools = UNSET
        elif isinstance(self.available_tools, list):
            available_tools = self.available_tools

        else:
            available_tools = self.available_tools

        tool_choice: Union[None, Unset, str]
        if isinstance(self.tool_choice, Unset):
            tool_choice = UNSET
        else:
            tool_choice = self.tool_choice

        content_filter_enabled = self.content_filter_enabled

        safety_level: Union[None, Unset, str]
        if isinstance(self.safety_level, Unset):
            safety_level = UNSET
        else:
            safety_level = self.safety_level

        response_format: Union[None, Unset, str]
        if isinstance(self.response_format, Unset):
            response_format = UNSET
        else:
            response_format = self.response_format

        stream_response = self.stream_response

        seed: Union[None, Unset, int]
        if isinstance(self.seed, Unset):
            seed = UNSET
        else:
            seed = self.seed

        stop_sequences: Union[None, Unset, list[str]]
        if isinstance(self.stop_sequences, Unset):
            stop_sequences = UNSET
        elif isinstance(self.stop_sequences, list):
            stop_sequences = self.stop_sequences

        else:
            stop_sequences = self.stop_sequences

        logit_bias: Union[None, Unset, dict[str, Any]]
        if isinstance(self.logit_bias, Unset):
            logit_bias = UNSET
        elif isinstance(self.logit_bias, ProfileCreateLogitBiasType0):
            logit_bias = self.logit_bias.to_dict()
        else:
            logit_bias = self.logit_bias

        embedding_provider: Union[None, Unset, str]
        if isinstance(self.embedding_provider, Unset):
            embedding_provider = UNSET
        else:
            embedding_provider = self.embedding_provider

        embedding_model: Union[None, Unset, str]
        if isinstance(self.embedding_model, Unset):
            embedding_model = UNSET
        else:
            embedding_model = self.embedding_model

        is_public = self.is_public

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        extra_metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.extra_metadata, Unset):
            extra_metadata = UNSET
        elif isinstance(self.extra_metadata, ProfileCreateExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "llm_provider": llm_provider,
                "llm_model": llm_model,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if profile_type is not UNSET:
            field_dict["profile_type"] = profile_type
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if top_p is not UNSET:
            field_dict["top_p"] = top_p
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if presence_penalty is not UNSET:
            field_dict["presence_penalty"] = presence_penalty
        if frequency_penalty is not UNSET:
            field_dict["frequency_penalty"] = frequency_penalty
        if context_window is not UNSET:
            field_dict["context_window"] = context_window
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if memory_enabled is not UNSET:
            field_dict["memory_enabled"] = memory_enabled
        if memory_strategy is not UNSET:
            field_dict["memory_strategy"] = memory_strategy
        if enable_retrieval is not UNSET:
            field_dict["enable_retrieval"] = enable_retrieval
        if retrieval_limit is not UNSET:
            field_dict["retrieval_limit"] = retrieval_limit
        if retrieval_score_threshold is not UNSET:
            field_dict["retrieval_score_threshold"] = retrieval_score_threshold
        if enable_tools is not UNSET:
            field_dict["enable_tools"] = enable_tools
        if available_tools is not UNSET:
            field_dict["available_tools"] = available_tools
        if tool_choice is not UNSET:
            field_dict["tool_choice"] = tool_choice
        if content_filter_enabled is not UNSET:
            field_dict["content_filter_enabled"] = content_filter_enabled
        if safety_level is not UNSET:
            field_dict["safety_level"] = safety_level
        if response_format is not UNSET:
            field_dict["response_format"] = response_format
        if stream_response is not UNSET:
            field_dict["stream_response"] = stream_response
        if seed is not UNSET:
            field_dict["seed"] = seed
        if stop_sequences is not UNSET:
            field_dict["stop_sequences"] = stop_sequences
        if logit_bias is not UNSET:
            field_dict["logit_bias"] = logit_bias
        if embedding_provider is not UNSET:
            field_dict["embedding_provider"] = embedding_provider
        if embedding_model is not UNSET:
            field_dict["embedding_model"] = embedding_model
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if tags is not UNSET:
            field_dict["tags"] = tags
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_create_extra_metadata_type_0 import ProfileCreateExtraMetadataType0
        from ..models.profile_create_logit_bias_type_0 import ProfileCreateLogitBiasType0

        d = dict(src_dict)
        name = d.pop("name")

        llm_provider = d.pop("llm_provider")

        llm_model = d.pop("llm_model")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        _profile_type = d.pop("profile_type", UNSET)
        profile_type: Union[Unset, ProfileType]
        if isinstance(_profile_type, Unset):
            profile_type = UNSET
        else:
            profile_type = ProfileType(_profile_type)

        temperature = d.pop("temperature", UNSET)

        def _parse_top_p(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        top_p = _parse_top_p(d.pop("top_p", UNSET))

        def _parse_top_k(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        top_k = _parse_top_k(d.pop("top_k", UNSET))

        max_tokens = d.pop("max_tokens", UNSET)

        def _parse_presence_penalty(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        presence_penalty = _parse_presence_penalty(d.pop("presence_penalty", UNSET))

        def _parse_frequency_penalty(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        frequency_penalty = _parse_frequency_penalty(d.pop("frequency_penalty", UNSET))

        context_window = d.pop("context_window", UNSET)

        def _parse_system_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        system_prompt = _parse_system_prompt(d.pop("system_prompt", UNSET))

        memory_enabled = d.pop("memory_enabled", UNSET)

        def _parse_memory_strategy(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        memory_strategy = _parse_memory_strategy(d.pop("memory_strategy", UNSET))

        enable_retrieval = d.pop("enable_retrieval", UNSET)

        retrieval_limit = d.pop("retrieval_limit", UNSET)

        retrieval_score_threshold = d.pop("retrieval_score_threshold", UNSET)

        enable_tools = d.pop("enable_tools", UNSET)

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

        def _parse_tool_choice(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tool_choice = _parse_tool_choice(d.pop("tool_choice", UNSET))

        content_filter_enabled = d.pop("content_filter_enabled", UNSET)

        def _parse_safety_level(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        safety_level = _parse_safety_level(d.pop("safety_level", UNSET))

        def _parse_response_format(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        response_format = _parse_response_format(d.pop("response_format", UNSET))

        stream_response = d.pop("stream_response", UNSET)

        def _parse_seed(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        seed = _parse_seed(d.pop("seed", UNSET))

        def _parse_stop_sequences(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                stop_sequences_type_0 = cast(list[str], data)

                return stop_sequences_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        stop_sequences = _parse_stop_sequences(d.pop("stop_sequences", UNSET))

        def _parse_logit_bias(data: object) -> Union["ProfileCreateLogitBiasType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                logit_bias_type_0 = ProfileCreateLogitBiasType0.from_dict(data)

                return logit_bias_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ProfileCreateLogitBiasType0", None, Unset], data)

        logit_bias = _parse_logit_bias(d.pop("logit_bias", UNSET))

        def _parse_embedding_provider(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        embedding_provider = _parse_embedding_provider(d.pop("embedding_provider", UNSET))

        def _parse_embedding_model(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        embedding_model = _parse_embedding_model(d.pop("embedding_model", UNSET))

        is_public = d.pop("is_public", UNSET)

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

        def _parse_extra_metadata(data: object) -> Union["ProfileCreateExtraMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = ProfileCreateExtraMetadataType0.from_dict(data)

                return extra_metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ProfileCreateExtraMetadataType0", None, Unset], data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))

        profile_create = cls(
            name=name,
            llm_provider=llm_provider,
            llm_model=llm_model,
            description=description,
            profile_type=profile_type,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            context_window=context_window,
            system_prompt=system_prompt,
            memory_enabled=memory_enabled,
            memory_strategy=memory_strategy,
            enable_retrieval=enable_retrieval,
            retrieval_limit=retrieval_limit,
            retrieval_score_threshold=retrieval_score_threshold,
            enable_tools=enable_tools,
            available_tools=available_tools,
            tool_choice=tool_choice,
            content_filter_enabled=content_filter_enabled,
            safety_level=safety_level,
            response_format=response_format,
            stream_response=stream_response,
            seed=seed,
            stop_sequences=stop_sequences,
            logit_bias=logit_bias,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            is_public=is_public,
            tags=tags,
            extra_metadata=extra_metadata,
        )

        profile_create.additional_properties = d
        return profile_create

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
