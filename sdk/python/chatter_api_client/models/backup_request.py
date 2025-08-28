from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.backup_type import BackupType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BackupRequest")


@_attrs_define
class BackupRequest:
    """Request schema for creating a backup via API.

    Attributes:
        backup_type (Union[Unset, BackupType]): Types of backups.
        name (Union[None, Unset, str]): Backup name
        description (Union[None, Unset, str]): Backup description
        include_files (Union[Unset, bool]): Include uploaded files Default: True.
        include_logs (Union[Unset, bool]): Include system logs Default: False.
        compress (Union[Unset, bool]): Compress backup Default: True.
        encrypt (Union[Unset, bool]): Encrypt backup Default: True.
        retention_days (Union[Unset, int]): Backup retention in days Default: 30.
    """

    backup_type: Union[Unset, BackupType] = UNSET
    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    include_files: Union[Unset, bool] = True
    include_logs: Union[Unset, bool] = False
    compress: Union[Unset, bool] = True
    encrypt: Union[Unset, bool] = True
    retention_days: Union[Unset, int] = 30
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        backup_type: Union[Unset, str] = UNSET
        if not isinstance(self.backup_type, Unset):
            backup_type = self.backup_type.value

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        include_files = self.include_files

        include_logs = self.include_logs

        compress = self.compress

        encrypt = self.encrypt

        retention_days = self.retention_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if backup_type is not UNSET:
            field_dict["backup_type"] = backup_type
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if include_files is not UNSET:
            field_dict["include_files"] = include_files
        if include_logs is not UNSET:
            field_dict["include_logs"] = include_logs
        if compress is not UNSET:
            field_dict["compress"] = compress
        if encrypt is not UNSET:
            field_dict["encrypt"] = encrypt
        if retention_days is not UNSET:
            field_dict["retention_days"] = retention_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _backup_type = d.pop("backup_type", UNSET)
        backup_type: Union[Unset, BackupType]
        if isinstance(_backup_type, Unset):
            backup_type = UNSET
        else:
            backup_type = BackupType(_backup_type)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        include_files = d.pop("include_files", UNSET)

        include_logs = d.pop("include_logs", UNSET)

        compress = d.pop("compress", UNSET)

        encrypt = d.pop("encrypt", UNSET)

        retention_days = d.pop("retention_days", UNSET)

        backup_request = cls(
            backup_type=backup_type,
            name=name,
            description=description,
            include_files=include_files,
            include_logs=include_logs,
            compress=compress,
            encrypt=encrypt,
            retention_days=retention_days,
        )

        backup_request.additional_properties = d
        return backup_request

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
