import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.conversation_status import ConversationStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_response import MessageResponse


T = TypeVar("T", bound="ConversationWithMessages")


@_attrs_define
class ConversationWithMessages:
    """Schema for conversation with messages.

    Attributes:
        title (str): Conversation title
        id (str): Conversation ID
        user_id (str): User ID
        status (ConversationStatus): Enumeration for conversation status.
        enable_retrieval (bool): Retrieval enabled
        message_count (int): Number of messages
        total_tokens (int): Total tokens used
        total_cost (float): Total cost
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        description (Union[None, Unset, str]): Conversation description
        profile_id (Union[None, Unset, str]): Profile ID
        llm_provider (Union[None, Unset, str]): LLM provider
        llm_model (Union[None, Unset, str]): LLM model
        temperature (Union[None, Unset, float]): Temperature setting
        max_tokens (Union[None, Unset, int]): Max tokens setting
        last_message_at (Union[None, Unset, datetime.datetime]): Last message timestamp
        messages (Union[Unset, list['MessageResponse']]): Conversation messages
    """

    title: str
    id: str
    user_id: str
    status: ConversationStatus
    enable_retrieval: bool
    message_count: int
    total_tokens: int
    total_cost: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    profile_id: Union[None, Unset, str] = UNSET
    llm_provider: Union[None, Unset, str] = UNSET
    llm_model: Union[None, Unset, str] = UNSET
    temperature: Union[None, Unset, float] = UNSET
    max_tokens: Union[None, Unset, int] = UNSET
    last_message_at: Union[None, Unset, datetime.datetime] = UNSET
    messages: Union[Unset, list["MessageResponse"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        id = self.id

        user_id = self.user_id

        status = self.status.value

        enable_retrieval = self.enable_retrieval

        message_count = self.message_count

        total_tokens = self.total_tokens

        total_cost = self.total_cost

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        profile_id: Union[None, Unset, str]
        if isinstance(self.profile_id, Unset):
            profile_id = UNSET
        else:
            profile_id = self.profile_id

        llm_provider: Union[None, Unset, str]
        if isinstance(self.llm_provider, Unset):
            llm_provider = UNSET
        else:
            llm_provider = self.llm_provider

        llm_model: Union[None, Unset, str]
        if isinstance(self.llm_model, Unset):
            llm_model = UNSET
        else:
            llm_model = self.llm_model

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

        last_message_at: Union[None, Unset, str]
        if isinstance(self.last_message_at, Unset):
            last_message_at = UNSET
        elif isinstance(self.last_message_at, datetime.datetime):
            last_message_at = self.last_message_at.isoformat()
        else:
            last_message_at = self.last_message_at

        messages: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.messages, Unset):
            messages = []
            for messages_item_data in self.messages:
                messages_item = messages_item_data.to_dict()
                messages.append(messages_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "id": id,
                "user_id": user_id,
                "status": status,
                "enable_retrieval": enable_retrieval,
                "message_count": message_count,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if llm_provider is not UNSET:
            field_dict["llm_provider"] = llm_provider
        if llm_model is not UNSET:
            field_dict["llm_model"] = llm_model
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if last_message_at is not UNSET:
            field_dict["last_message_at"] = last_message_at
        if messages is not UNSET:
            field_dict["messages"] = messages

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_response import MessageResponse

        d = dict(src_dict)
        title = d.pop("title")

        id = d.pop("id")

        user_id = d.pop("user_id")

        status = ConversationStatus(d.pop("status"))

        enable_retrieval = d.pop("enable_retrieval")

        message_count = d.pop("message_count")

        total_tokens = d.pop("total_tokens")

        total_cost = d.pop("total_cost")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_profile_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        profile_id = _parse_profile_id(d.pop("profile_id", UNSET))

        def _parse_llm_provider(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        llm_provider = _parse_llm_provider(d.pop("llm_provider", UNSET))

        def _parse_llm_model(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        llm_model = _parse_llm_model(d.pop("llm_model", UNSET))

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

        def _parse_last_message_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_message_at_type_0 = isoparse(data)

                return last_message_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_message_at = _parse_last_message_at(d.pop("last_message_at", UNSET))

        messages = []
        _messages = d.pop("messages", UNSET)
        for messages_item_data in _messages or []:
            messages_item = MessageResponse.from_dict(messages_item_data)

            messages.append(messages_item)

        conversation_with_messages = cls(
            title=title,
            id=id,
            user_id=user_id,
            status=status,
            enable_retrieval=enable_retrieval,
            message_count=message_count,
            total_tokens=total_tokens,
            total_cost=total_cost,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            profile_id=profile_id,
            llm_provider=llm_provider,
            llm_model=llm_model,
            temperature=temperature,
            max_tokens=max_tokens,
            last_message_at=last_message_at,
            messages=messages,
        )

        conversation_with_messages.additional_properties = d
        return conversation_with_messages

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
