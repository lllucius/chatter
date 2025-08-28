import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.job_priority import JobPriority
from ..models.job_status import JobStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="JobResponse")


@_attrs_define
class JobResponse:
    """Response schema for job data.

    Attributes:
        id (str): Job ID
        name (str): Job name
        function_name (str): Function name
        priority (JobPriority): Job priority levels.
        status (JobStatus): Job execution status.
        created_at (datetime.datetime): Creation timestamp
        retry_count (int): Number of retry attempts
        max_retries (int): Maximum retry attempts
        started_at (Union[None, Unset, datetime.datetime]): Start timestamp
        completed_at (Union[None, Unset, datetime.datetime]): Completion timestamp
        scheduled_at (Union[None, Unset, datetime.datetime]): Scheduled execution time
        error_message (Union[None, Unset, str]): Error message if failed
        result (Union[Any, None, Unset]): Job result if completed
        progress (Union[Unset, int]): Job progress percentage Default: 0.
        progress_message (Union[None, Unset, str]): Progress message
    """

    id: str
    name: str
    function_name: str
    priority: JobPriority
    status: JobStatus
    created_at: datetime.datetime
    retry_count: int
    max_retries: int
    started_at: Union[None, Unset, datetime.datetime] = UNSET
    completed_at: Union[None, Unset, datetime.datetime] = UNSET
    scheduled_at: Union[None, Unset, datetime.datetime] = UNSET
    error_message: Union[None, Unset, str] = UNSET
    result: Union[Any, None, Unset] = UNSET
    progress: Union[Unset, int] = 0
    progress_message: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        function_name = self.function_name

        priority = self.priority.value

        status = self.status.value

        created_at = self.created_at.isoformat()

        retry_count = self.retry_count

        max_retries = self.max_retries

        started_at: Union[None, Unset, str]
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        completed_at: Union[None, Unset, str]
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        scheduled_at: Union[None, Unset, str]
        if isinstance(self.scheduled_at, Unset):
            scheduled_at = UNSET
        elif isinstance(self.scheduled_at, datetime.datetime):
            scheduled_at = self.scheduled_at.isoformat()
        else:
            scheduled_at = self.scheduled_at

        error_message: Union[None, Unset, str]
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        result: Union[Any, None, Unset]
        if isinstance(self.result, Unset):
            result = UNSET
        else:
            result = self.result

        progress = self.progress

        progress_message: Union[None, Unset, str]
        if isinstance(self.progress_message, Unset):
            progress_message = UNSET
        else:
            progress_message = self.progress_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "function_name": function_name,
                "priority": priority,
                "status": status,
                "created_at": created_at,
                "retry_count": retry_count,
                "max_retries": max_retries,
            }
        )
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if scheduled_at is not UNSET:
            field_dict["scheduled_at"] = scheduled_at
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if result is not UNSET:
            field_dict["result"] = result
        if progress is not UNSET:
            field_dict["progress"] = progress
        if progress_message is not UNSET:
            field_dict["progress_message"] = progress_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        function_name = d.pop("function_name")

        priority = JobPriority(d.pop("priority"))

        status = JobStatus(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        retry_count = d.pop("retry_count")

        max_retries = d.pop("max_retries")

        def _parse_started_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

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

        def _parse_scheduled_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                scheduled_at_type_0 = isoparse(data)

                return scheduled_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        scheduled_at = _parse_scheduled_at(d.pop("scheduled_at", UNSET))

        def _parse_error_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        def _parse_result(data: object) -> Union[Any, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, None, Unset], data)

        result = _parse_result(d.pop("result", UNSET))

        progress = d.pop("progress", UNSET)

        def _parse_progress_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        progress_message = _parse_progress_message(d.pop("progress_message", UNSET))

        job_response = cls(
            id=id,
            name=name,
            function_name=function_name,
            priority=priority,
            status=status,
            created_at=created_at,
            retry_count=retry_count,
            max_retries=max_retries,
            started_at=started_at,
            completed_at=completed_at,
            scheduled_at=scheduled_at,
            error_message=error_message,
            result=result,
            progress=progress,
            progress_message=progress_message,
        )

        job_response.additional_properties = d
        return job_response

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
