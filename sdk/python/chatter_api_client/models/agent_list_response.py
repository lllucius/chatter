from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent_response import AgentResponse


T = TypeVar("T", bound="AgentListResponse")


@_attrs_define
class AgentListResponse:
    """Response schema for agent list.

    Attributes:
        agents (list['AgentResponse']): List of agents
        total (int): Total number of agents
        page (int): Current page number
        per_page (int): Number of items per page
        total_pages (int): Total number of pages
    """

    agents: list["AgentResponse"]
    total: int
    page: int
    per_page: int
    total_pages: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agents = []
        for agents_item_data in self.agents:
            agents_item = agents_item_data.to_dict()
            agents.append(agents_item)

        total = self.total

        page = self.page

        per_page = self.per_page

        total_pages = self.total_pages

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agents": agents,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_response import AgentResponse

        d = dict(src_dict)
        agents = []
        _agents = d.pop("agents")
        for agents_item_data in _agents:
            agents_item = AgentResponse.from_dict(agents_item_data)

            agents.append(agents_item)

        total = d.pop("total")

        page = d.pop("page")

        per_page = d.pop("per_page")

        total_pages = d.pop("total_pages")

        agent_list_response = cls(
            agents=agents,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

        agent_list_response.additional_properties = d
        return agent_list_response

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
