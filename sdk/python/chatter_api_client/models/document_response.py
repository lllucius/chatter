import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.document_status import DocumentStatus
from ..models.document_type import DocumentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_response_extra_metadata_type_0 import DocumentResponseExtraMetadataType0


T = TypeVar("T", bound="DocumentResponse")


@_attrs_define
class DocumentResponse:
    """Schema for document response.

    Attributes:
        id (str): Document ID
        owner_id (str): Owner user ID
        filename (str): Document filename
        original_filename (str): Original filename
        file_size (int): File size in bytes
        file_hash (str): File hash (SHA-256)
        mime_type (str): MIME type
        document_type (DocumentType): Enumeration for document types.
        status (DocumentStatus): Enumeration for document processing status.
        chunk_size (int): Chunk size
        chunk_overlap (int): Chunk overlap
        chunk_count (int): Number of chunks
        version (int): Document version
        view_count (int): View count
        search_count (int): Search count
        created_at (datetime.datetime): Creation time
        updated_at (datetime.datetime): Last update time
        title (Union[None, Unset, str]): Document title
        description (Union[None, Unset, str]): Document description
        tags (Union[None, Unset, list[str]]): Document tags
        extra_metadata (Union['DocumentResponseExtraMetadataType0', None, Unset]): Additional metadata
        is_public (Union[Unset, bool]): Whether document is public Default: False.
        processing_started_at (Union[None, Unset, datetime.datetime]): Processing start time
        processing_completed_at (Union[None, Unset, datetime.datetime]): Processing completion time
        processing_error (Union[None, Unset, str]): Processing error message
        parent_document_id (Union[None, Unset, str]): Parent document ID
        last_accessed_at (Union[None, Unset, datetime.datetime]): Last access time
    """

    id: str
    owner_id: str
    filename: str
    original_filename: str
    file_size: int
    file_hash: str
    mime_type: str
    document_type: DocumentType
    status: DocumentStatus
    chunk_size: int
    chunk_overlap: int
    chunk_count: int
    version: int
    view_count: int
    search_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    title: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    extra_metadata: Union["DocumentResponseExtraMetadataType0", None, Unset] = UNSET
    is_public: Union[Unset, bool] = False
    processing_started_at: Union[None, Unset, datetime.datetime] = UNSET
    processing_completed_at: Union[None, Unset, datetime.datetime] = UNSET
    processing_error: Union[None, Unset, str] = UNSET
    parent_document_id: Union[None, Unset, str] = UNSET
    last_accessed_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_response_extra_metadata_type_0 import DocumentResponseExtraMetadataType0

        id = self.id

        owner_id = self.owner_id

        filename = self.filename

        original_filename = self.original_filename

        file_size = self.file_size

        file_hash = self.file_hash

        mime_type = self.mime_type

        document_type = self.document_type.value

        status = self.status.value

        chunk_size = self.chunk_size

        chunk_overlap = self.chunk_overlap

        chunk_count = self.chunk_count

        version = self.version

        view_count = self.view_count

        search_count = self.search_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

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
        elif isinstance(self.extra_metadata, DocumentResponseExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        is_public = self.is_public

        processing_started_at: Union[None, Unset, str]
        if isinstance(self.processing_started_at, Unset):
            processing_started_at = UNSET
        elif isinstance(self.processing_started_at, datetime.datetime):
            processing_started_at = self.processing_started_at.isoformat()
        else:
            processing_started_at = self.processing_started_at

        processing_completed_at: Union[None, Unset, str]
        if isinstance(self.processing_completed_at, Unset):
            processing_completed_at = UNSET
        elif isinstance(self.processing_completed_at, datetime.datetime):
            processing_completed_at = self.processing_completed_at.isoformat()
        else:
            processing_completed_at = self.processing_completed_at

        processing_error: Union[None, Unset, str]
        if isinstance(self.processing_error, Unset):
            processing_error = UNSET
        else:
            processing_error = self.processing_error

        parent_document_id: Union[None, Unset, str]
        if isinstance(self.parent_document_id, Unset):
            parent_document_id = UNSET
        else:
            parent_document_id = self.parent_document_id

        last_accessed_at: Union[None, Unset, str]
        if isinstance(self.last_accessed_at, Unset):
            last_accessed_at = UNSET
        elif isinstance(self.last_accessed_at, datetime.datetime):
            last_accessed_at = self.last_accessed_at.isoformat()
        else:
            last_accessed_at = self.last_accessed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "owner_id": owner_id,
                "filename": filename,
                "original_filename": original_filename,
                "file_size": file_size,
                "file_hash": file_hash,
                "mime_type": mime_type,
                "document_type": document_type,
                "status": status,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "chunk_count": chunk_count,
                "version": version,
                "view_count": view_count,
                "search_count": search_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
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
        if processing_started_at is not UNSET:
            field_dict["processing_started_at"] = processing_started_at
        if processing_completed_at is not UNSET:
            field_dict["processing_completed_at"] = processing_completed_at
        if processing_error is not UNSET:
            field_dict["processing_error"] = processing_error
        if parent_document_id is not UNSET:
            field_dict["parent_document_id"] = parent_document_id
        if last_accessed_at is not UNSET:
            field_dict["last_accessed_at"] = last_accessed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_response_extra_metadata_type_0 import DocumentResponseExtraMetadataType0

        d = dict(src_dict)
        id = d.pop("id")

        owner_id = d.pop("owner_id")

        filename = d.pop("filename")

        original_filename = d.pop("original_filename")

        file_size = d.pop("file_size")

        file_hash = d.pop("file_hash")

        mime_type = d.pop("mime_type")

        document_type = DocumentType(d.pop("document_type"))

        status = DocumentStatus(d.pop("status"))

        chunk_size = d.pop("chunk_size")

        chunk_overlap = d.pop("chunk_overlap")

        chunk_count = d.pop("chunk_count")

        version = d.pop("version")

        view_count = d.pop("view_count")

        search_count = d.pop("search_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

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

        def _parse_extra_metadata(data: object) -> Union["DocumentResponseExtraMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = DocumentResponseExtraMetadataType0.from_dict(data)

                return extra_metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DocumentResponseExtraMetadataType0", None, Unset], data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))

        is_public = d.pop("is_public", UNSET)

        def _parse_processing_started_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                processing_started_at_type_0 = isoparse(data)

                return processing_started_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        processing_started_at = _parse_processing_started_at(d.pop("processing_started_at", UNSET))

        def _parse_processing_completed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                processing_completed_at_type_0 = isoparse(data)

                return processing_completed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        processing_completed_at = _parse_processing_completed_at(d.pop("processing_completed_at", UNSET))

        def _parse_processing_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        processing_error = _parse_processing_error(d.pop("processing_error", UNSET))

        def _parse_parent_document_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_document_id = _parse_parent_document_id(d.pop("parent_document_id", UNSET))

        def _parse_last_accessed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_accessed_at_type_0 = isoparse(data)

                return last_accessed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_accessed_at = _parse_last_accessed_at(d.pop("last_accessed_at", UNSET))

        document_response = cls(
            id=id,
            owner_id=owner_id,
            filename=filename,
            original_filename=original_filename,
            file_size=file_size,
            file_hash=file_hash,
            mime_type=mime_type,
            document_type=document_type,
            status=status,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_count=chunk_count,
            version=version,
            view_count=view_count,
            search_count=search_count,
            created_at=created_at,
            updated_at=updated_at,
            title=title,
            description=description,
            tags=tags,
            extra_metadata=extra_metadata,
            is_public=is_public,
            processing_started_at=processing_started_at,
            processing_completed_at=processing_completed_at,
            processing_error=processing_error,
            parent_document_id=parent_document_id,
            last_accessed_at=last_accessed_at,
        )

        document_response.additional_properties = d
        return document_response

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
