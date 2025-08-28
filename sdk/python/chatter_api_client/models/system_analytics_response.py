from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.system_analytics_response_requests_per_endpoint import SystemAnalyticsResponseRequestsPerEndpoint


T = TypeVar("T", bound="SystemAnalyticsResponse")


@_attrs_define
class SystemAnalyticsResponse:
    """Schema for system analytics response.

    Attributes:
        total_users (int): Total number of users
        active_users_today (int): Active users today
        active_users_week (int): Active users this week
        active_users_month (int): Active users this month
        system_uptime_seconds (float): System uptime in seconds
        avg_cpu_usage (float): Average CPU usage percentage
        avg_memory_usage (float): Average memory usage percentage
        database_connections (int): Current database connections
        total_api_requests (int): Total API requests
        requests_per_endpoint (SystemAnalyticsResponseRequestsPerEndpoint): Requests by endpoint
        avg_api_response_time (float): Average API response time
        api_error_rate (float): API error rate
        storage_usage_bytes (int): Total storage usage
        vector_database_size_bytes (int): Vector database size
        cache_hit_rate (float): Cache hit rate
    """

    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    system_uptime_seconds: float
    avg_cpu_usage: float
    avg_memory_usage: float
    database_connections: int
    total_api_requests: int
    requests_per_endpoint: "SystemAnalyticsResponseRequestsPerEndpoint"
    avg_api_response_time: float
    api_error_rate: float
    storage_usage_bytes: int
    vector_database_size_bytes: int
    cache_hit_rate: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_users = self.total_users

        active_users_today = self.active_users_today

        active_users_week = self.active_users_week

        active_users_month = self.active_users_month

        system_uptime_seconds = self.system_uptime_seconds

        avg_cpu_usage = self.avg_cpu_usage

        avg_memory_usage = self.avg_memory_usage

        database_connections = self.database_connections

        total_api_requests = self.total_api_requests

        requests_per_endpoint = self.requests_per_endpoint.to_dict()

        avg_api_response_time = self.avg_api_response_time

        api_error_rate = self.api_error_rate

        storage_usage_bytes = self.storage_usage_bytes

        vector_database_size_bytes = self.vector_database_size_bytes

        cache_hit_rate = self.cache_hit_rate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_users": total_users,
                "active_users_today": active_users_today,
                "active_users_week": active_users_week,
                "active_users_month": active_users_month,
                "system_uptime_seconds": system_uptime_seconds,
                "avg_cpu_usage": avg_cpu_usage,
                "avg_memory_usage": avg_memory_usage,
                "database_connections": database_connections,
                "total_api_requests": total_api_requests,
                "requests_per_endpoint": requests_per_endpoint,
                "avg_api_response_time": avg_api_response_time,
                "api_error_rate": api_error_rate,
                "storage_usage_bytes": storage_usage_bytes,
                "vector_database_size_bytes": vector_database_size_bytes,
                "cache_hit_rate": cache_hit_rate,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.system_analytics_response_requests_per_endpoint import SystemAnalyticsResponseRequestsPerEndpoint

        d = dict(src_dict)
        total_users = d.pop("total_users")

        active_users_today = d.pop("active_users_today")

        active_users_week = d.pop("active_users_week")

        active_users_month = d.pop("active_users_month")

        system_uptime_seconds = d.pop("system_uptime_seconds")

        avg_cpu_usage = d.pop("avg_cpu_usage")

        avg_memory_usage = d.pop("avg_memory_usage")

        database_connections = d.pop("database_connections")

        total_api_requests = d.pop("total_api_requests")

        requests_per_endpoint = SystemAnalyticsResponseRequestsPerEndpoint.from_dict(d.pop("requests_per_endpoint"))

        avg_api_response_time = d.pop("avg_api_response_time")

        api_error_rate = d.pop("api_error_rate")

        storage_usage_bytes = d.pop("storage_usage_bytes")

        vector_database_size_bytes = d.pop("vector_database_size_bytes")

        cache_hit_rate = d.pop("cache_hit_rate")

        system_analytics_response = cls(
            total_users=total_users,
            active_users_today=active_users_today,
            active_users_week=active_users_week,
            active_users_month=active_users_month,
            system_uptime_seconds=system_uptime_seconds,
            avg_cpu_usage=avg_cpu_usage,
            avg_memory_usage=avg_memory_usage,
            database_connections=database_connections,
            total_api_requests=total_api_requests,
            requests_per_endpoint=requests_per_endpoint,
            avg_api_response_time=avg_api_response_time,
            api_error_rate=api_error_rate,
            storage_usage_bytes=storage_usage_bytes,
            vector_database_size_bytes=vector_database_size_bytes,
            cache_hit_rate=cache_hit_rate,
        )

        system_analytics_response.additional_properties = d
        return system_analytics_response

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
