from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.conversation_response import ConversationResponse


T = TypeVar("T", bound="ConversationSearchResponse")


@_attrs_define
class ConversationSearchResponse:
    """Schema for conversation search response.

    Attributes:
        conversations (list['ConversationResponse']): Conversations
        total (int): Total number of conversations
        limit (int): Request limit
        offset (int): Request offset
    """

    conversations: list["ConversationResponse"]
    total: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conversations = []
        for conversations_item_data in self.conversations:
            conversations_item = conversations_item_data.to_dict()
            conversations.append(conversations_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conversations": conversations,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_response import ConversationResponse

        d = dict(src_dict)
        conversations = []
        _conversations = d.pop("conversations")
        for conversations_item_data in _conversations:
            conversations_item = ConversationResponse.from_dict(conversations_item_data)

            conversations.append(conversations_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        conversation_search_response = cls(
            conversations=conversations,
            total=total,
            limit=limit,
            offset=offset,
        )

        conversation_search_response.additional_properties = d
        return conversation_search_response

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
