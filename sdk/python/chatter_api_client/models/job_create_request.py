import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.job_priority import JobPriority
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_create_request_kwargs import JobCreateRequestKwargs


T = TypeVar("T", bound="JobCreateRequest")


@_attrs_define
class JobCreateRequest:
    """Request schema for creating a job.

    Attributes:
        name (str): Job name
        function_name (str): Function to execute
        args (Union[Unset, list[Any]]): Function arguments
        kwargs (Union[Unset, JobCreateRequestKwargs]): Function keyword arguments
        priority (Union[Unset, JobPriority]): Job priority levels.
        max_retries (Union[Unset, int]): Maximum retry attempts Default: 3.
        schedule_at (Union[None, Unset, datetime.datetime]): Schedule job for later execution
    """

    name: str
    function_name: str
    args: Union[Unset, list[Any]] = UNSET
    kwargs: Union[Unset, "JobCreateRequestKwargs"] = UNSET
    priority: Union[Unset, JobPriority] = UNSET
    max_retries: Union[Unset, int] = 3
    schedule_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        function_name = self.function_name

        args: Union[Unset, list[Any]] = UNSET
        if not isinstance(self.args, Unset):
            args = self.args

        kwargs: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.kwargs, Unset):
            kwargs = self.kwargs.to_dict()

        priority: Union[Unset, str] = UNSET
        if not isinstance(self.priority, Unset):
            priority = self.priority.value

        max_retries = self.max_retries

        schedule_at: Union[None, Unset, str]
        if isinstance(self.schedule_at, Unset):
            schedule_at = UNSET
        elif isinstance(self.schedule_at, datetime.datetime):
            schedule_at = self.schedule_at.isoformat()
        else:
            schedule_at = self.schedule_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "function_name": function_name,
            }
        )
        if args is not UNSET:
            field_dict["args"] = args
        if kwargs is not UNSET:
            field_dict["kwargs"] = kwargs
        if priority is not UNSET:
            field_dict["priority"] = priority
        if max_retries is not UNSET:
            field_dict["max_retries"] = max_retries
        if schedule_at is not UNSET:
            field_dict["schedule_at"] = schedule_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_create_request_kwargs import JobCreateRequestKwargs

        d = dict(src_dict)
        name = d.pop("name")

        function_name = d.pop("function_name")

        args = cast(list[Any], d.pop("args", UNSET))

        _kwargs = d.pop("kwargs", UNSET)
        kwargs: Union[Unset, JobCreateRequestKwargs]
        if isinstance(_kwargs, Unset):
            kwargs = UNSET
        else:
            kwargs = JobCreateRequestKwargs.from_dict(_kwargs)

        _priority = d.pop("priority", UNSET)
        priority: Union[Unset, JobPriority]
        if isinstance(_priority, Unset):
            priority = UNSET
        else:
            priority = JobPriority(_priority)

        max_retries = d.pop("max_retries", UNSET)

        def _parse_schedule_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                schedule_at_type_0 = isoparse(data)

                return schedule_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        schedule_at = _parse_schedule_at(d.pop("schedule_at", UNSET))

        job_create_request = cls(
            name=name,
            function_name=function_name,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries,
            schedule_at=schedule_at,
        )

        job_create_request.additional_properties = d
        return job_create_request

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
