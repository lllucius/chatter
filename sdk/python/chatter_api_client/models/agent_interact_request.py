from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_interact_request_context_type_0 import AgentInteractRequestContextType0


T = TypeVar("T", bound="AgentInteractRequest")


@_attrs_define
class AgentInteractRequest:
    """Request schema for interacting with an agent.

    Attributes:
        message (str): Message to send to the agent
        conversation_id (str): Conversation ID
        context (Union['AgentInteractRequestContextType0', None, Unset]): Additional context
    """

    message: str
    conversation_id: str
    context: Union["AgentInteractRequestContextType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.agent_interact_request_context_type_0 import AgentInteractRequestContextType0

        message = self.message

        conversation_id = self.conversation_id

        context: Union[None, Unset, dict[str, Any]]
        if isinstance(self.context, Unset):
            context = UNSET
        elif isinstance(self.context, AgentInteractRequestContextType0):
            context = self.context.to_dict()
        else:
            context = self.context

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "conversation_id": conversation_id,
            }
        )
        if context is not UNSET:
            field_dict["context"] = context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_interact_request_context_type_0 import AgentInteractRequestContextType0

        d = dict(src_dict)
        message = d.pop("message")

        conversation_id = d.pop("conversation_id")

        def _parse_context(data: object) -> Union["AgentInteractRequestContextType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                context_type_0 = AgentInteractRequestContextType0.from_dict(data)

                return context_type_0
            except:  # noqa: E722
                pass
            return cast(Union["AgentInteractRequestContextType0", None, Unset], data)

        context = _parse_context(d.pop("context", UNSET))

        agent_interact_request = cls(
            message=message,
            conversation_id=conversation_id,
            context=context,
        )

        agent_interact_request.additional_properties = d
        return agent_interact_request

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
