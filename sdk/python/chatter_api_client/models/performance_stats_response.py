from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.performance_stats_response_cache_stats import PerformanceStatsResponseCacheStats
    from ..models.performance_stats_response_error_counts import PerformanceStatsResponseErrorCounts
    from ..models.performance_stats_response_tool_stats import PerformanceStatsResponseToolStats
    from ..models.performance_stats_response_workflow_types import PerformanceStatsResponseWorkflowTypes


T = TypeVar("T", bound="PerformanceStatsResponse")


@_attrs_define
class PerformanceStatsResponse:
    """Schema for performance statistics response.

    Attributes:
        total_executions (int): Total number of executions
        avg_execution_time_ms (int): Average execution time in milliseconds
        min_execution_time_ms (int): Minimum execution time in milliseconds
        max_execution_time_ms (int): Maximum execution time in milliseconds
        workflow_types (PerformanceStatsResponseWorkflowTypes): Execution count by workflow type
        error_counts (PerformanceStatsResponseErrorCounts): Error count by type
        cache_stats (PerformanceStatsResponseCacheStats): Cache statistics
        tool_stats (PerformanceStatsResponseToolStats): Tool usage statistics
        timestamp (float): Statistics timestamp
    """

    total_executions: int
    avg_execution_time_ms: int
    min_execution_time_ms: int
    max_execution_time_ms: int
    workflow_types: "PerformanceStatsResponseWorkflowTypes"
    error_counts: "PerformanceStatsResponseErrorCounts"
    cache_stats: "PerformanceStatsResponseCacheStats"
    tool_stats: "PerformanceStatsResponseToolStats"
    timestamp: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_executions = self.total_executions

        avg_execution_time_ms = self.avg_execution_time_ms

        min_execution_time_ms = self.min_execution_time_ms

        max_execution_time_ms = self.max_execution_time_ms

        workflow_types = self.workflow_types.to_dict()

        error_counts = self.error_counts.to_dict()

        cache_stats = self.cache_stats.to_dict()

        tool_stats = self.tool_stats.to_dict()

        timestamp = self.timestamp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_executions": total_executions,
                "avg_execution_time_ms": avg_execution_time_ms,
                "min_execution_time_ms": min_execution_time_ms,
                "max_execution_time_ms": max_execution_time_ms,
                "workflow_types": workflow_types,
                "error_counts": error_counts,
                "cache_stats": cache_stats,
                "tool_stats": tool_stats,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.performance_stats_response_cache_stats import PerformanceStatsResponseCacheStats
        from ..models.performance_stats_response_error_counts import PerformanceStatsResponseErrorCounts
        from ..models.performance_stats_response_tool_stats import PerformanceStatsResponseToolStats
        from ..models.performance_stats_response_workflow_types import PerformanceStatsResponseWorkflowTypes

        d = dict(src_dict)
        total_executions = d.pop("total_executions")

        avg_execution_time_ms = d.pop("avg_execution_time_ms")

        min_execution_time_ms = d.pop("min_execution_time_ms")

        max_execution_time_ms = d.pop("max_execution_time_ms")

        workflow_types = PerformanceStatsResponseWorkflowTypes.from_dict(d.pop("workflow_types"))

        error_counts = PerformanceStatsResponseErrorCounts.from_dict(d.pop("error_counts"))

        cache_stats = PerformanceStatsResponseCacheStats.from_dict(d.pop("cache_stats"))

        tool_stats = PerformanceStatsResponseToolStats.from_dict(d.pop("tool_stats"))

        timestamp = d.pop("timestamp")

        performance_stats_response = cls(
            total_executions=total_executions,
            avg_execution_time_ms=avg_execution_time_ms,
            min_execution_time_ms=min_execution_time_ms,
            max_execution_time_ms=max_execution_time_ms,
            workflow_types=workflow_types,
            error_counts=error_counts,
            cache_stats=cache_stats,
            tool_stats=tool_stats,
            timestamp=timestamp,
        )

        performance_stats_response.additional_properties = d
        return performance_stats_response

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
