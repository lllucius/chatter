import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.storage_stats_response_storage_by_type import StorageStatsResponseStorageByType
    from ..models.storage_stats_response_storage_by_user import StorageStatsResponseStorageByUser


T = TypeVar("T", bound="StorageStatsResponse")


@_attrs_define
class StorageStatsResponse:
    """Response schema for storage statistics.

    Attributes:
        total_size (int): Total storage used in bytes
        database_size (int): Database size in bytes
        files_size (int): Uploaded files size in bytes
        backups_size (int): Backups size in bytes
        exports_size (int): Exports size in bytes
        total_records (int): Total number of records
        total_files (int): Total number of files
        total_backups (int): Total number of backups
        storage_by_type (StorageStatsResponseStorageByType): Storage usage by data type
        storage_by_user (StorageStatsResponseStorageByUser): Storage usage by user
        growth_rate_mb_per_day (float): Storage growth rate in MB per day
        projected_size_30_days (int): Projected size in 30 days
        last_updated (datetime.datetime): Statistics last updated timestamp
    """

    total_size: int
    database_size: int
    files_size: int
    backups_size: int
    exports_size: int
    total_records: int
    total_files: int
    total_backups: int
    storage_by_type: "StorageStatsResponseStorageByType"
    storage_by_user: "StorageStatsResponseStorageByUser"
    growth_rate_mb_per_day: float
    projected_size_30_days: int
    last_updated: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_size = self.total_size

        database_size = self.database_size

        files_size = self.files_size

        backups_size = self.backups_size

        exports_size = self.exports_size

        total_records = self.total_records

        total_files = self.total_files

        total_backups = self.total_backups

        storage_by_type = self.storage_by_type.to_dict()

        storage_by_user = self.storage_by_user.to_dict()

        growth_rate_mb_per_day = self.growth_rate_mb_per_day

        projected_size_30_days = self.projected_size_30_days

        last_updated = self.last_updated.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_size": total_size,
                "database_size": database_size,
                "files_size": files_size,
                "backups_size": backups_size,
                "exports_size": exports_size,
                "total_records": total_records,
                "total_files": total_files,
                "total_backups": total_backups,
                "storage_by_type": storage_by_type,
                "storage_by_user": storage_by_user,
                "growth_rate_mb_per_day": growth_rate_mb_per_day,
                "projected_size_30_days": projected_size_30_days,
                "last_updated": last_updated,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.storage_stats_response_storage_by_type import StorageStatsResponseStorageByType
        from ..models.storage_stats_response_storage_by_user import StorageStatsResponseStorageByUser

        d = dict(src_dict)
        total_size = d.pop("total_size")

        database_size = d.pop("database_size")

        files_size = d.pop("files_size")

        backups_size = d.pop("backups_size")

        exports_size = d.pop("exports_size")

        total_records = d.pop("total_records")

        total_files = d.pop("total_files")

        total_backups = d.pop("total_backups")

        storage_by_type = StorageStatsResponseStorageByType.from_dict(d.pop("storage_by_type"))

        storage_by_user = StorageStatsResponseStorageByUser.from_dict(d.pop("storage_by_user"))

        growth_rate_mb_per_day = d.pop("growth_rate_mb_per_day")

        projected_size_30_days = d.pop("projected_size_30_days")

        last_updated = isoparse(d.pop("last_updated"))

        storage_stats_response = cls(
            total_size=total_size,
            database_size=database_size,
            files_size=files_size,
            backups_size=backups_size,
            exports_size=exports_size,
            total_records=total_records,
            total_files=total_files,
            total_backups=total_backups,
            storage_by_type=storage_by_type,
            storage_by_user=storage_by_user,
            growth_rate_mb_per_day=growth_rate_mb_per_day,
            projected_size_30_days=projected_size_30_days,
            last_updated=last_updated,
        )

        storage_stats_response.additional_properties = d
        return storage_stats_response

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
