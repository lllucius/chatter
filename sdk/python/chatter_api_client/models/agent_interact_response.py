import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="AgentInteractResponse")


@_attrs_define
class AgentInteractResponse:
    """Response schema for agent interaction.

    Attributes:
        agent_id (str): Agent ID
        response (str): Agent response
        conversation_id (str): Conversation ID
        tools_used (list[str]): Tools used in response
        confidence_score (float): Confidence score
        response_time (float): Response time in seconds
        timestamp (datetime.datetime): Response timestamp
    """

    agent_id: str
    response: str
    conversation_id: str
    tools_used: list[str]
    confidence_score: float
    response_time: float
    timestamp: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        response = self.response

        conversation_id = self.conversation_id

        tools_used = self.tools_used

        confidence_score = self.confidence_score

        response_time = self.response_time

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent_id": agent_id,
                "response": response,
                "conversation_id": conversation_id,
                "tools_used": tools_used,
                "confidence_score": confidence_score,
                "response_time": response_time,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agent_id = d.pop("agent_id")

        response = d.pop("response")

        conversation_id = d.pop("conversation_id")

        tools_used = cast(list[str], d.pop("tools_used"))

        confidence_score = d.pop("confidence_score")

        response_time = d.pop("response_time")

        timestamp = isoparse(d.pop("timestamp"))

        agent_interact_response = cls(
            agent_id=agent_id,
            response=response,
            conversation_id=conversation_id,
            tools_used=tools_used,
            confidence_score=confidence_score,
            response_time=response_time,
            timestamp=timestamp,
        )

        agent_interact_response.additional_properties = d
        return agent_interact_response

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
