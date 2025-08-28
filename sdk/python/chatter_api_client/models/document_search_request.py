from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_type import DocumentType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentSearchRequest")


@_attrs_define
class DocumentSearchRequest:
    """Schema for document search request.

    Attributes:
        query (str): Search query
        limit (Union[Unset, int]): Maximum number of results Default: 10.
        score_threshold (Union[Unset, float]): Minimum similarity score Default: 0.5.
        document_types (Union[None, Unset, list[DocumentType]]): Filter by document types
        tags (Union[None, Unset, list[str]]): Filter by tags
        include_content (Union[Unset, bool]): Include document content in results Default: False.
    """

    query: str
    limit: Union[Unset, int] = 10
    score_threshold: Union[Unset, float] = 0.5
    document_types: Union[None, Unset, list[DocumentType]] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    include_content: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        limit = self.limit

        score_threshold = self.score_threshold

        document_types: Union[None, Unset, list[str]]
        if isinstance(self.document_types, Unset):
            document_types = UNSET
        elif isinstance(self.document_types, list):
            document_types = []
            for document_types_type_0_item_data in self.document_types:
                document_types_type_0_item = document_types_type_0_item_data.value
                document_types.append(document_types_type_0_item)

        else:
            document_types = self.document_types

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        include_content = self.include_content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if limit is not UNSET:
            field_dict["limit"] = limit
        if score_threshold is not UNSET:
            field_dict["score_threshold"] = score_threshold
        if document_types is not UNSET:
            field_dict["document_types"] = document_types
        if tags is not UNSET:
            field_dict["tags"] = tags
        if include_content is not UNSET:
            field_dict["include_content"] = include_content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        limit = d.pop("limit", UNSET)

        score_threshold = d.pop("score_threshold", UNSET)

        def _parse_document_types(data: object) -> Union[None, Unset, list[DocumentType]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                document_types_type_0 = []
                _document_types_type_0 = data
                for document_types_type_0_item_data in _document_types_type_0:
                    document_types_type_0_item = DocumentType(document_types_type_0_item_data)

                    document_types_type_0.append(document_types_type_0_item)

                return document_types_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[DocumentType]], data)

        document_types = _parse_document_types(d.pop("document_types", UNSET))

        def _parse_tags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        tags = _parse_tags(d.pop("tags", UNSET))

        include_content = d.pop("include_content", UNSET)

        document_search_request = cls(
            query=query,
            limit=limit,
            score_threshold=score_threshold,
            document_types=document_types,
            tags=tags,
            include_content=include_content,
        )

        document_search_request.additional_properties = d
        return document_search_request

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
