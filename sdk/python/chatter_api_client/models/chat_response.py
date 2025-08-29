from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.conversation_response import ConversationResponse
    from ..models.message_response import MessageResponse


T = TypeVar("T", bound="ChatResponse")


@_attrs_define
class ChatResponse:
    """Schema for chat response.

    Attributes:
        conversation_id (str): Conversation ID
        message (MessageResponse): Schema for message response.
        conversation (ConversationResponse): Schema for conversation response.
    """

    conversation_id: str
    message: "MessageResponse"
    conversation: "ConversationResponse"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conversation_id = self.conversation_id

        message = self.message.to_dict()

        conversation = self.conversation.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conversation_id": conversation_id,
                "message": message,
                "conversation": conversation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_response import ConversationResponse
        from ..models.message_response import MessageResponse

        d = dict(src_dict)
        conversation_id = d.pop("conversation_id")

        message = MessageResponse.from_dict(d.pop("message"))

        conversation = ConversationResponse.from_dict(d.pop("conversation"))

        chat_response = cls(
            conversation_id=conversation_id,
            message=message,
            conversation=conversation,
        )

        chat_response.additional_properties = d
        return chat_response

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
