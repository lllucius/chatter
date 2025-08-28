import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExportDataResponse")


@_attrs_define
class ExportDataResponse:
    """Response schema for data export.

    Attributes:
        export_id (str): Export ID
        status (str): Export status
        created_at (datetime.datetime): Export creation timestamp
        download_url (Union[None, Unset, str]): Download URL when ready
        file_size (Union[None, Unset, int]): File size in bytes
        record_count (Union[None, Unset, int]): Number of records exported
        completed_at (Union[None, Unset, datetime.datetime]): Export completion timestamp
        expires_at (Union[None, Unset, datetime.datetime]): Download link expiration
    """

    export_id: str
    status: str
    created_at: datetime.datetime
    download_url: Union[None, Unset, str] = UNSET
    file_size: Union[None, Unset, int] = UNSET
    record_count: Union[None, Unset, int] = UNSET
    completed_at: Union[None, Unset, datetime.datetime] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        export_id = self.export_id

        status = self.status

        created_at = self.created_at.isoformat()

        download_url: Union[None, Unset, str]
        if isinstance(self.download_url, Unset):
            download_url = UNSET
        else:
            download_url = self.download_url

        file_size: Union[None, Unset, int]
        if isinstance(self.file_size, Unset):
            file_size = UNSET
        else:
            file_size = self.file_size

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
                "export_id": export_id,
                "status": status,
                "created_at": created_at,
            }
        )
        if download_url is not UNSET:
            field_dict["download_url"] = download_url
        if file_size is not UNSET:
            field_dict["file_size"] = file_size
        if record_count is not UNSET:
            field_dict["record_count"] = record_count
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        export_id = d.pop("export_id")

        status = d.pop("status")

        created_at = isoparse(d.pop("created_at"))

        def _parse_download_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        download_url = _parse_download_url(d.pop("download_url", UNSET))

        def _parse_file_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        file_size = _parse_file_size(d.pop("file_size", UNSET))

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

        export_data_response = cls(
            export_id=export_id,
            status=status,
            created_at=created_at,
            download_url=download_url,
            file_size=file_size,
            record_count=record_count,
            completed_at=completed_at,
            expires_at=expires_at,
        )

        export_data_response.additional_properties = d
        return export_data_response

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
