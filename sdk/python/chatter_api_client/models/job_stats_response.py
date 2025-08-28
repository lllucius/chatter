from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="JobStatsResponse")


@_attrs_define
class JobStatsResponse:
    """Response schema for job statistics.

    Attributes:
        total_jobs (int): Total number of jobs
        pending_jobs (int): Number of pending jobs
        running_jobs (int): Number of running jobs
        completed_jobs (int): Number of completed jobs
        failed_jobs (int): Number of failed jobs
        queue_size (int): Current queue size
        active_workers (int): Number of active workers
    """

    total_jobs: int
    pending_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    queue_size: int
    active_workers: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_jobs = self.total_jobs

        pending_jobs = self.pending_jobs

        running_jobs = self.running_jobs

        completed_jobs = self.completed_jobs

        failed_jobs = self.failed_jobs

        queue_size = self.queue_size

        active_workers = self.active_workers

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_jobs": total_jobs,
                "pending_jobs": pending_jobs,
                "running_jobs": running_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
                "queue_size": queue_size,
                "active_workers": active_workers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_jobs = d.pop("total_jobs")

        pending_jobs = d.pop("pending_jobs")

        running_jobs = d.pop("running_jobs")

        completed_jobs = d.pop("completed_jobs")

        failed_jobs = d.pop("failed_jobs")

        queue_size = d.pop("queue_size")

        active_workers = d.pop("active_workers")

        job_stats_response = cls(
            total_jobs=total_jobs,
            pending_jobs=pending_jobs,
            running_jobs=running_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            queue_size=queue_size,
            active_workers=active_workers,
        )

        job_stats_response.additional_properties = d
        return job_stats_response

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
