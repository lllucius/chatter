from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="BodyUploadDocumentApiV1DocumentsUploadPost")


@_attrs_define
class BodyUploadDocumentApiV1DocumentsUploadPost:
    """
    Attributes:
        file (File):
        title (Union[Unset, str]):
        description (Union[Unset, str]):
        tags (Union[Unset, str]):
        chunk_size (Union[Unset, int]):  Default: 1000.
        chunk_overlap (Union[Unset, int]):  Default: 200.
        is_public (Union[Unset, bool]):  Default: False.
    """

    file: File
    title: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    tags: Union[Unset, str] = UNSET
    chunk_size: Union[Unset, int] = 1000
    chunk_overlap: Union[Unset, int] = 200
    is_public: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        title = self.title

        description = self.description

        tags = self.tags

        chunk_size = self.chunk_size

        chunk_overlap = self.chunk_overlap

        is_public = self.is_public

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags
        if chunk_size is not UNSET:
            field_dict["chunk_size"] = chunk_size
        if chunk_overlap is not UNSET:
            field_dict["chunk_overlap"] = chunk_overlap
        if is_public is not UNSET:
            field_dict["is_public"] = is_public

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", self.file.to_tuple()))

        if not isinstance(self.title, Unset):
            files.append(("title", (None, str(self.title).encode(), "text/plain")))

        if not isinstance(self.description, Unset):
            files.append(("description", (None, str(self.description).encode(), "text/plain")))

        if not isinstance(self.tags, Unset):
            files.append(("tags", (None, str(self.tags).encode(), "text/plain")))

        if not isinstance(self.chunk_size, Unset):
            files.append(("chunk_size", (None, str(self.chunk_size).encode(), "text/plain")))

        if not isinstance(self.chunk_overlap, Unset):
            files.append(("chunk_overlap", (None, str(self.chunk_overlap).encode(), "text/plain")))

        if not isinstance(self.is_public, Unset):
            files.append(("is_public", (None, str(self.is_public).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        tags = d.pop("tags", UNSET)

        chunk_size = d.pop("chunk_size", UNSET)

        chunk_overlap = d.pop("chunk_overlap", UNSET)

        is_public = d.pop("is_public", UNSET)

        body_upload_document_api_v1_documents_upload_post = cls(
            file=file,
            title=title,
            description=description,
            tags=tags,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            is_public=is_public,
        )

        body_upload_document_api_v1_documents_upload_post.additional_properties = d
        return body_upload_document_api_v1_documents_upload_post

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
