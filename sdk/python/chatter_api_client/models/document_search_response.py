from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_search_result import DocumentSearchResult


T = TypeVar("T", bound="DocumentSearchResponse")


@_attrs_define
class DocumentSearchResponse:
    """Schema for document search response.

    Attributes:
        results (list['DocumentSearchResult']): Search results
        total_results (int): Total number of matching results
        query (str): Original search query
        score_threshold (float): Applied score threshold
    """

    results: list["DocumentSearchResult"]
    total_results: int
    query: str
    score_threshold: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        total_results = self.total_results

        query = self.query

        score_threshold = self.score_threshold

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results": results,
                "total_results": total_results,
                "query": query,
                "score_threshold": score_threshold,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_search_result import DocumentSearchResult

        d = dict(src_dict)
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = DocumentSearchResult.from_dict(results_item_data)

            results.append(results_item)

        total_results = d.pop("total_results")

        query = d.pop("query")

        score_threshold = d.pop("score_threshold")

        document_search_response = cls(
            results=results,
            total_results=total_results,
            query=query,
            score_threshold=score_threshold,
        )

        document_search_response.additional_properties = d
        return document_search_response

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
