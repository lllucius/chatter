from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chat_request_workflow import ChatRequestWorkflow
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatRequest")


@_attrs_define
class ChatRequest:
    """Schema for chat request.

    Attributes:
        message (str): User message
        conversation_id (Union[None, Unset, str]): Conversation ID for continuing chat
        profile_id (Union[None, Unset, str]): Profile ID to use
        stream (Union[Unset, bool]): Enable streaming response Default: False.
        workflow (Union[Unset, ChatRequestWorkflow]): Workflow type: plain, rag, tools, or full (rag + tools) Default:
            ChatRequestWorkflow.PLAIN.
        provider (Union[None, Unset, str]): Override LLM provider for this request
        temperature (Union[None, Unset, float]): Temperature override
        max_tokens (Union[None, Unset, int]): Max tokens override
        enable_retrieval (Union[None, Unset, bool]): Enable retrieval override
        document_ids (Union[None, Unset, list[str]]): Document IDs to include in context
        system_prompt_override (Union[None, Unset, str]): Override system prompt for this request
    """

    message: str
    conversation_id: Union[None, Unset, str] = UNSET
    profile_id: Union[None, Unset, str] = UNSET
    stream: Union[Unset, bool] = False
    workflow: Union[Unset, ChatRequestWorkflow] = ChatRequestWorkflow.PLAIN
    provider: Union[None, Unset, str] = UNSET
    temperature: Union[None, Unset, float] = UNSET
    max_tokens: Union[None, Unset, int] = UNSET
    enable_retrieval: Union[None, Unset, bool] = UNSET
    document_ids: Union[None, Unset, list[str]] = UNSET
    system_prompt_override: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        conversation_id: Union[None, Unset, str]
        if isinstance(self.conversation_id, Unset):
            conversation_id = UNSET
        else:
            conversation_id = self.conversation_id

        profile_id: Union[None, Unset, str]
        if isinstance(self.profile_id, Unset):
            profile_id = UNSET
        else:
            profile_id = self.profile_id

        stream = self.stream

        workflow: Union[Unset, str] = UNSET
        if not isinstance(self.workflow, Unset):
            workflow = self.workflow.value

        provider: Union[None, Unset, str]
        if isinstance(self.provider, Unset):
            provider = UNSET
        else:
            provider = self.provider

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

        enable_retrieval: Union[None, Unset, bool]
        if isinstance(self.enable_retrieval, Unset):
            enable_retrieval = UNSET
        else:
            enable_retrieval = self.enable_retrieval

        document_ids: Union[None, Unset, list[str]]
        if isinstance(self.document_ids, Unset):
            document_ids = UNSET
        elif isinstance(self.document_ids, list):
            document_ids = self.document_ids

        else:
            document_ids = self.document_ids

        system_prompt_override: Union[None, Unset, str]
        if isinstance(self.system_prompt_override, Unset):
            system_prompt_override = UNSET
        else:
            system_prompt_override = self.system_prompt_override

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
            }
        )
        if conversation_id is not UNSET:
            field_dict["conversation_id"] = conversation_id
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if stream is not UNSET:
            field_dict["stream"] = stream
        if workflow is not UNSET:
            field_dict["workflow"] = workflow
        if provider is not UNSET:
            field_dict["provider"] = provider
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if enable_retrieval is not UNSET:
            field_dict["enable_retrieval"] = enable_retrieval
        if document_ids is not UNSET:
            field_dict["document_ids"] = document_ids
        if system_prompt_override is not UNSET:
            field_dict["system_prompt_override"] = system_prompt_override

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message")

        def _parse_conversation_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        conversation_id = _parse_conversation_id(d.pop("conversation_id", UNSET))

        def _parse_profile_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        profile_id = _parse_profile_id(d.pop("profile_id", UNSET))

        stream = d.pop("stream", UNSET)

        _workflow = d.pop("workflow", UNSET)
        workflow: Union[Unset, ChatRequestWorkflow]
        if isinstance(_workflow, Unset):
            workflow = UNSET
        else:
            workflow = ChatRequestWorkflow(_workflow)

        def _parse_provider(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        provider = _parse_provider(d.pop("provider", UNSET))

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

        def _parse_enable_retrieval(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        enable_retrieval = _parse_enable_retrieval(d.pop("enable_retrieval", UNSET))

        def _parse_document_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                document_ids_type_0 = cast(list[str], data)

                return document_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        document_ids = _parse_document_ids(d.pop("document_ids", UNSET))

        def _parse_system_prompt_override(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        system_prompt_override = _parse_system_prompt_override(d.pop("system_prompt_override", UNSET))

        chat_request = cls(
            message=message,
            conversation_id=conversation_id,
            profile_id=profile_id,
            stream=stream,
            workflow=workflow,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            enable_retrieval=enable_retrieval,
            document_ids=document_ids,
            system_prompt_override=system_prompt_override,
        )

        chat_request.additional_properties = d
        return chat_request

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
