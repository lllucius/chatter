import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_chunk_response_extra_metadata_type_0 import DocumentChunkResponseExtraMetadataType0


T = TypeVar("T", bound="DocumentChunkResponse")


@_attrs_define
class DocumentChunkResponse:
    """Schema for document chunk response.

    Attributes:
        id (str): Chunk ID
        document_id (str): Document ID
        content (str): Chunk content
        chunk_index (int): Chunk index
        content_hash (str): Content hash
        created_at (datetime.datetime): Creation time
        updated_at (datetime.datetime): Last update time
        start_char (Union[None, Unset, int]): Start character position
        end_char (Union[None, Unset, int]): End character position
        extra_metadata (Union['DocumentChunkResponseExtraMetadataType0', None, Unset]): Chunk metadata
        token_count (Union[None, Unset, int]): Token count
        language (Union[None, Unset, str]): Detected language
        embedding_model (Union[None, Unset, str]): Embedding model used
        embedding_provider (Union[None, Unset, str]): Embedding provider
        embedding_created_at (Union[None, Unset, datetime.datetime]): Embedding creation time
    """

    id: str
    document_id: str
    content: str
    chunk_index: int
    content_hash: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    start_char: Union[None, Unset, int] = UNSET
    end_char: Union[None, Unset, int] = UNSET
    extra_metadata: Union["DocumentChunkResponseExtraMetadataType0", None, Unset] = UNSET
    token_count: Union[None, Unset, int] = UNSET
    language: Union[None, Unset, str] = UNSET
    embedding_model: Union[None, Unset, str] = UNSET
    embedding_provider: Union[None, Unset, str] = UNSET
    embedding_created_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_chunk_response_extra_metadata_type_0 import DocumentChunkResponseExtraMetadataType0

        id = self.id

        document_id = self.document_id

        content = self.content

        chunk_index = self.chunk_index

        content_hash = self.content_hash

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        start_char: Union[None, Unset, int]
        if isinstance(self.start_char, Unset):
            start_char = UNSET
        else:
            start_char = self.start_char

        end_char: Union[None, Unset, int]
        if isinstance(self.end_char, Unset):
            end_char = UNSET
        else:
            end_char = self.end_char

        extra_metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.extra_metadata, Unset):
            extra_metadata = UNSET
        elif isinstance(self.extra_metadata, DocumentChunkResponseExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        token_count: Union[None, Unset, int]
        if isinstance(self.token_count, Unset):
            token_count = UNSET
        else:
            token_count = self.token_count

        language: Union[None, Unset, str]
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

        embedding_model: Union[None, Unset, str]
        if isinstance(self.embedding_model, Unset):
            embedding_model = UNSET
        else:
            embedding_model = self.embedding_model

        embedding_provider: Union[None, Unset, str]
        if isinstance(self.embedding_provider, Unset):
            embedding_provider = UNSET
        else:
            embedding_provider = self.embedding_provider

        embedding_created_at: Union[None, Unset, str]
        if isinstance(self.embedding_created_at, Unset):
            embedding_created_at = UNSET
        elif isinstance(self.embedding_created_at, datetime.datetime):
            embedding_created_at = self.embedding_created_at.isoformat()
        else:
            embedding_created_at = self.embedding_created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "document_id": document_id,
                "content": content,
                "chunk_index": chunk_index,
                "content_hash": content_hash,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if start_char is not UNSET:
            field_dict["start_char"] = start_char
        if end_char is not UNSET:
            field_dict["end_char"] = end_char
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata
        if token_count is not UNSET:
            field_dict["token_count"] = token_count
        if language is not UNSET:
            field_dict["language"] = language
        if embedding_model is not UNSET:
            field_dict["embedding_model"] = embedding_model
        if embedding_provider is not UNSET:
            field_dict["embedding_provider"] = embedding_provider
        if embedding_created_at is not UNSET:
            field_dict["embedding_created_at"] = embedding_created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_chunk_response_extra_metadata_type_0 import DocumentChunkResponseExtraMetadataType0

        d = dict(src_dict)
        id = d.pop("id")

        document_id = d.pop("document_id")

        content = d.pop("content")

        chunk_index = d.pop("chunk_index")

        content_hash = d.pop("content_hash")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_start_char(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        start_char = _parse_start_char(d.pop("start_char", UNSET))

        def _parse_end_char(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        end_char = _parse_end_char(d.pop("end_char", UNSET))

        def _parse_extra_metadata(data: object) -> Union["DocumentChunkResponseExtraMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = DocumentChunkResponseExtraMetadataType0.from_dict(data)

                return extra_metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DocumentChunkResponseExtraMetadataType0", None, Unset], data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))

        def _parse_token_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        token_count = _parse_token_count(d.pop("token_count", UNSET))

        def _parse_language(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        language = _parse_language(d.pop("language", UNSET))

        def _parse_embedding_model(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        embedding_model = _parse_embedding_model(d.pop("embedding_model", UNSET))

        def _parse_embedding_provider(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        embedding_provider = _parse_embedding_provider(d.pop("embedding_provider", UNSET))

        def _parse_embedding_created_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                embedding_created_at_type_0 = isoparse(data)

                return embedding_created_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        embedding_created_at = _parse_embedding_created_at(d.pop("embedding_created_at", UNSET))

        document_chunk_response = cls(
            id=id,
            document_id=document_id,
            content=content,
            chunk_index=chunk_index,
            content_hash=content_hash,
            created_at=created_at,
            updated_at=updated_at,
            start_char=start_char,
            end_char=end_char,
            extra_metadata=extra_metadata,
            token_count=token_count,
            language=language,
            embedding_model=embedding_model,
            embedding_provider=embedding_provider,
            embedding_created_at=embedding_created_at,
        )

        document_chunk_response.additional_properties = d
        return document_chunk_response

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
