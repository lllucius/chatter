from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_update_extra_metadata_type_0 import DocumentUpdateExtraMetadataType0


T = TypeVar("T", bound="DocumentUpdate")


@_attrs_define
class DocumentUpdate:
    """Schema for updating a document.

    Attributes:
        title (Union[None, Unset, str]): Document title
        description (Union[None, Unset, str]): Document description
        tags (Union[None, Unset, list[str]]): Document tags
        extra_metadata (Union['DocumentUpdateExtraMetadataType0', None, Unset]): Additional metadata
        is_public (Union[None, Unset, bool]): Whether document is public
    """

    title: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    extra_metadata: Union["DocumentUpdateExtraMetadataType0", None, Unset] = UNSET
    is_public: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_update_extra_metadata_type_0 import DocumentUpdateExtraMetadataType0

        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        extra_metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.extra_metadata, Unset):
            extra_metadata = UNSET
        elif isinstance(self.extra_metadata, DocumentUpdateExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        is_public: Union[None, Unset, bool]
        if isinstance(self.is_public, Unset):
            is_public = UNSET
        else:
            is_public = self.is_public

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata
        if is_public is not UNSET:
            field_dict["is_public"] = is_public

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_update_extra_metadata_type_0 import DocumentUpdateExtraMetadataType0

        d = dict(src_dict)

        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

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

        def _parse_extra_metadata(data: object) -> Union["DocumentUpdateExtraMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = DocumentUpdateExtraMetadataType0.from_dict(data)

                return extra_metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DocumentUpdateExtraMetadataType0", None, Unset], data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))

        def _parse_is_public(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_public = _parse_is_public(d.pop("is_public", UNSET))

        document_update = cls(
            title=title,
            description=description,
            tags=tags,
            extra_metadata=extra_metadata,
            is_public=is_public,
        )

        document_update.additional_properties = d
        return document_update

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
