from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent_stats_response_agent_types import AgentStatsResponseAgentTypes


T = TypeVar("T", bound="AgentStatsResponse")


@_attrs_define
class AgentStatsResponse:
    """Response schema for agent statistics.

    Attributes:
        total_agents (int): Total number of agents
        active_agents (int): Number of active agents
        agent_types (AgentStatsResponseAgentTypes): Agents by type
        total_interactions (int): Total interactions across all agents
    """

    total_agents: int
    active_agents: int
    agent_types: "AgentStatsResponseAgentTypes"
    total_interactions: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_agents = self.total_agents

        active_agents = self.active_agents

        agent_types = self.agent_types.to_dict()

        total_interactions = self.total_interactions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "agent_types": agent_types,
                "total_interactions": total_interactions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_stats_response_agent_types import AgentStatsResponseAgentTypes

        d = dict(src_dict)
        total_agents = d.pop("total_agents")

        active_agents = d.pop("active_agents")

        agent_types = AgentStatsResponseAgentTypes.from_dict(d.pop("agent_types"))

        total_interactions = d.pop("total_interactions")

        agent_stats_response = cls(
            total_agents=total_agents,
            active_agents=active_agents,
            agent_types=agent_types,
            total_interactions=total_interactions,
        )

        agent_stats_response.additional_properties = d
        return agent_stats_response

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
