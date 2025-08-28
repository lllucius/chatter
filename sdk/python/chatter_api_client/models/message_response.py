import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.message_role import MessageRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageResponse")


@_attrs_define
class MessageResponse:
    """Schema for message response.

    Attributes:
        role (MessageRole): Enumeration for message roles.
        content (str): Message content
        id (str): Message ID
        conversation_id (str): Conversation ID
        sequence_number (int): Message sequence number
        created_at (datetime.datetime): Creation timestamp
        prompt_tokens (Union[None, Unset, int]): Prompt tokens used
        completion_tokens (Union[None, Unset, int]): Completion tokens used
        total_tokens (Union[None, Unset, int]): Total tokens used
        model_used (Union[None, Unset, str]): Model used for generation
        provider_used (Union[None, Unset, str]): Provider used
        response_time_ms (Union[None, Unset, int]): Response time in milliseconds
        cost (Union[None, Unset, float]): Cost of the message
    """

    role: MessageRole
    content: str
    id: str
    conversation_id: str
    sequence_number: int
    created_at: datetime.datetime
    prompt_tokens: Union[None, Unset, int] = UNSET
    completion_tokens: Union[None, Unset, int] = UNSET
    total_tokens: Union[None, Unset, int] = UNSET
    model_used: Union[None, Unset, str] = UNSET
    provider_used: Union[None, Unset, str] = UNSET
    response_time_ms: Union[None, Unset, int] = UNSET
    cost: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        content = self.content

        id = self.id

        conversation_id = self.conversation_id

        sequence_number = self.sequence_number

        created_at = self.created_at.isoformat()

        prompt_tokens: Union[None, Unset, int]
        if isinstance(self.prompt_tokens, Unset):
            prompt_tokens = UNSET
        else:
            prompt_tokens = self.prompt_tokens

        completion_tokens: Union[None, Unset, int]
        if isinstance(self.completion_tokens, Unset):
            completion_tokens = UNSET
        else:
            completion_tokens = self.completion_tokens

        total_tokens: Union[None, Unset, int]
        if isinstance(self.total_tokens, Unset):
            total_tokens = UNSET
        else:
            total_tokens = self.total_tokens

        model_used: Union[None, Unset, str]
        if isinstance(self.model_used, Unset):
            model_used = UNSET
        else:
            model_used = self.model_used

        provider_used: Union[None, Unset, str]
        if isinstance(self.provider_used, Unset):
            provider_used = UNSET
        else:
            provider_used = self.provider_used

        response_time_ms: Union[None, Unset, int]
        if isinstance(self.response_time_ms, Unset):
            response_time_ms = UNSET
        else:
            response_time_ms = self.response_time_ms

        cost: Union[None, Unset, float]
        if isinstance(self.cost, Unset):
            cost = UNSET
        else:
            cost = self.cost

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "content": content,
                "id": id,
                "conversation_id": conversation_id,
                "sequence_number": sequence_number,
                "created_at": created_at,
            }
        )
        if prompt_tokens is not UNSET:
            field_dict["prompt_tokens"] = prompt_tokens
        if completion_tokens is not UNSET:
            field_dict["completion_tokens"] = completion_tokens
        if total_tokens is not UNSET:
            field_dict["total_tokens"] = total_tokens
        if model_used is not UNSET:
            field_dict["model_used"] = model_used
        if provider_used is not UNSET:
            field_dict["provider_used"] = provider_used
        if response_time_ms is not UNSET:
            field_dict["response_time_ms"] = response_time_ms
        if cost is not UNSET:
            field_dict["cost"] = cost

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = MessageRole(d.pop("role"))

        content = d.pop("content")

        id = d.pop("id")

        conversation_id = d.pop("conversation_id")

        sequence_number = d.pop("sequence_number")

        created_at = isoparse(d.pop("created_at"))

        def _parse_prompt_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        prompt_tokens = _parse_prompt_tokens(d.pop("prompt_tokens", UNSET))

        def _parse_completion_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        completion_tokens = _parse_completion_tokens(d.pop("completion_tokens", UNSET))

        def _parse_total_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        total_tokens = _parse_total_tokens(d.pop("total_tokens", UNSET))

        def _parse_model_used(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        model_used = _parse_model_used(d.pop("model_used", UNSET))

        def _parse_provider_used(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        provider_used = _parse_provider_used(d.pop("provider_used", UNSET))

        def _parse_response_time_ms(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        response_time_ms = _parse_response_time_ms(d.pop("response_time_ms", UNSET))

        def _parse_cost(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        cost = _parse_cost(d.pop("cost", UNSET))

        message_response = cls(
            role=role,
            content=content,
            id=id,
            conversation_id=conversation_id,
            sequence_number=sequence_number,
            created_at=created_at,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model_used=model_used,
            provider_used=provider_used,
            response_time_ms=response_time_ms,
            cost=cost,
        )

        message_response.additional_properties = d
        return message_response

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
