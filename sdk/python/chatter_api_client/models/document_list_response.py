from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_response import DocumentResponse


T = TypeVar("T", bound="DocumentListResponse")


@_attrs_define
class DocumentListResponse:
    """Schema for document list response.

    Attributes:
        documents (list['DocumentResponse']): List of documents
        total_count (int): Total number of documents
        limit (int): Applied limit
        offset (int): Applied offset
    """

    documents: list["DocumentResponse"]
    total_count: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        total_count = self.total_count

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "documents": documents,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_response import DocumentResponse

        d = dict(src_dict)
        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = DocumentResponse.from_dict(documents_item_data)

            documents.append(documents_item)

        total_count = d.pop("total_count")

        limit = d.pop("limit")

        offset = d.pop("offset")

        document_list_response = cls(
            documents=documents,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

        document_list_response.additional_properties = d
        return document_list_response

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
