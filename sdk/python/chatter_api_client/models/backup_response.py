import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.backup_type import BackupType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.backup_response_metadata import BackupResponseMetadata


T = TypeVar("T", bound="BackupResponse")


@_attrs_define
class BackupResponse:
    """Response schema for backup data.

    Attributes:
        id (str): Backup ID
        name (str): Backup name
        backup_type (BackupType): Types of backups.
        status (str): Backup status
        created_at (datetime.datetime): Backup creation timestamp
        encrypted (bool): Whether backup is encrypted
        compressed (bool): Whether backup is compressed
        metadata (BackupResponseMetadata): Backup metadata
        description (Union[None, Unset, str]): Backup description
        file_size (Union[None, Unset, int]): Backup file size in bytes
        compressed_size (Union[None, Unset, int]): Compressed size in bytes
        record_count (Union[None, Unset, int]): Number of records backed up
        completed_at (Union[None, Unset, datetime.datetime]): Backup completion timestamp
        expires_at (Union[None, Unset, datetime.datetime]): Backup expiration timestamp
    """

    id: str
    name: str
    backup_type: BackupType
    status: str
    created_at: datetime.datetime
    encrypted: bool
    compressed: bool
    metadata: "BackupResponseMetadata"
    description: Union[None, Unset, str] = UNSET
    file_size: Union[None, Unset, int] = UNSET
    compressed_size: Union[None, Unset, int] = UNSET
    record_count: Union[None, Unset, int] = UNSET
    completed_at: Union[None, Unset, datetime.datetime] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        backup_type = self.backup_type.value

        status = self.status

        created_at = self.created_at.isoformat()

        encrypted = self.encrypted

        compressed = self.compressed

        metadata = self.metadata.to_dict()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        file_size: Union[None, Unset, int]
        if isinstance(self.file_size, Unset):
            file_size = UNSET
        else:
            file_size = self.file_size

        compressed_size: Union[None, Unset, int]
        if isinstance(self.compressed_size, Unset):
            compressed_size = UNSET
        else:
            compressed_size = self.compressed_size

        record_count: Union[None, Unset, int]
        if isinstance(self.record_count, Unset):
            record_count = UNSET
        else:
            record_count = self.record_count

        completed_at: Union[None, Unset, str]
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "backup_type": backup_type,
                "status": status,
                "created_at": created_at,
                "encrypted": encrypted,
                "compressed": compressed,
                "metadata": metadata,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if file_size is not UNSET:
            field_dict["file_size"] = file_size
        if compressed_size is not UNSET:
            field_dict["compressed_size"] = compressed_size
        if record_count is not UNSET:
            field_dict["record_count"] = record_count
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.backup_response_metadata import BackupResponseMetadata

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        backup_type = BackupType(d.pop("backup_type"))

        status = d.pop("status")

        created_at = isoparse(d.pop("created_at"))

        encrypted = d.pop("encrypted")

        compressed = d.pop("compressed")

        metadata = BackupResponseMetadata.from_dict(d.pop("metadata"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_file_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        file_size = _parse_file_size(d.pop("file_size", UNSET))

        def _parse_compressed_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        compressed_size = _parse_compressed_size(d.pop("compressed_size", UNSET))

        def _parse_record_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        record_count = _parse_record_count(d.pop("record_count", UNSET))

        def _parse_completed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = isoparse(data)

                return completed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        backup_response = cls(
            id=id,
            name=name,
            backup_type=backup_type,
            status=status,
            created_at=created_at,
            encrypted=encrypted,
            compressed=compressed,
            metadata=metadata,
            description=description,
            file_size=file_size,
            compressed_size=compressed_size,
            record_count=record_count,
            completed_at=completed_at,
            expires_at=expires_at,
        )

        backup_response.additional_properties = d
        return backup_response

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
