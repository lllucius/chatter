import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RestoreResponse")


@_attrs_define
class RestoreResponse:
    """Response schema for restore operation.

    Attributes:
        restore_id (str): Restore operation ID
        backup_id (str): Source backup ID
        status (str): Restore status
        started_at (datetime.datetime): Restore start timestamp
        progress (Union[Unset, int]): Restore progress percentage Default: 0.
        records_restored (Union[Unset, int]): Number of records restored Default: 0.
        completed_at (Union[None, Unset, datetime.datetime]): Restore completion timestamp
        error_message (Union[None, Unset, str]): Error message if failed
    """

    restore_id: str
    backup_id: str
    status: str
    started_at: datetime.datetime
    progress: Union[Unset, int] = 0
    records_restored: Union[Unset, int] = 0
    completed_at: Union[None, Unset, datetime.datetime] = UNSET
    error_message: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        restore_id = self.restore_id

        backup_id = self.backup_id

        status = self.status

        started_at = self.started_at.isoformat()

        progress = self.progress

        records_restored = self.records_restored

        completed_at: Union[None, Unset, str]
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        error_message: Union[None, Unset, str]
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "restore_id": restore_id,
                "backup_id": backup_id,
                "status": status,
                "started_at": started_at,
            }
        )
        if progress is not UNSET:
            field_dict["progress"] = progress
        if records_restored is not UNSET:
            field_dict["records_restored"] = records_restored
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if error_message is not UNSET:
            field_dict["error_message"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        restore_id = d.pop("restore_id")

        backup_id = d.pop("backup_id")

        status = d.pop("status")

        started_at = isoparse(d.pop("started_at"))

        progress = d.pop("progress", UNSET)

        records_restored = d.pop("records_restored", UNSET)

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

        def _parse_error_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        restore_response = cls(
            restore_id=restore_id,
            backup_id=backup_id,
            status=status,
            started_at=started_at,
            progress=progress,
            records_restored=records_restored,
            completed_at=completed_at,
            error_message=error_message,
        )

        restore_response.additional_properties = d
        return restore_response

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
