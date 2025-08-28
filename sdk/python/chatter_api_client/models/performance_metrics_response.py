from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.performance_metrics_response_errors_by_type import PerformanceMetricsResponseErrorsByType
    from ..models.performance_metrics_response_performance_by_model import PerformanceMetricsResponsePerformanceByModel
    from ..models.performance_metrics_response_performance_by_provider import (
        PerformanceMetricsResponsePerformanceByProvider,
    )


T = TypeVar("T", bound="PerformanceMetricsResponse")


@_attrs_define
class PerformanceMetricsResponse:
    """Schema for performance metrics response.

    Attributes:
        avg_response_time_ms (float): Average response time
        median_response_time_ms (float): Median response time
        p95_response_time_ms (float): 95th percentile response time
        p99_response_time_ms (float): 99th percentile response time
        requests_per_minute (float): Average requests per minute
        tokens_per_minute (float): Average tokens per minute
        total_errors (int): Total number of errors
        error_rate (float): Error rate percentage
        errors_by_type (PerformanceMetricsResponseErrorsByType): Errors grouped by type
        performance_by_model (PerformanceMetricsResponsePerformanceByModel): Performance metrics by model
        performance_by_provider (PerformanceMetricsResponsePerformanceByProvider): Performance metrics by provider
        database_response_time_ms (float): Average database response time
        vector_search_time_ms (float): Average vector search time
        embedding_generation_time_ms (float): Average embedding generation time
    """

    avg_response_time_ms: float
    median_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_minute: float
    tokens_per_minute: float
    total_errors: int
    error_rate: float
    errors_by_type: "PerformanceMetricsResponseErrorsByType"
    performance_by_model: "PerformanceMetricsResponsePerformanceByModel"
    performance_by_provider: "PerformanceMetricsResponsePerformanceByProvider"
    database_response_time_ms: float
    vector_search_time_ms: float
    embedding_generation_time_ms: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        avg_response_time_ms = self.avg_response_time_ms

        median_response_time_ms = self.median_response_time_ms

        p95_response_time_ms = self.p95_response_time_ms

        p99_response_time_ms = self.p99_response_time_ms

        requests_per_minute = self.requests_per_minute

        tokens_per_minute = self.tokens_per_minute

        total_errors = self.total_errors

        error_rate = self.error_rate

        errors_by_type = self.errors_by_type.to_dict()

        performance_by_model = self.performance_by_model.to_dict()

        performance_by_provider = self.performance_by_provider.to_dict()

        database_response_time_ms = self.database_response_time_ms

        vector_search_time_ms = self.vector_search_time_ms

        embedding_generation_time_ms = self.embedding_generation_time_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "avg_response_time_ms": avg_response_time_ms,
                "median_response_time_ms": median_response_time_ms,
                "p95_response_time_ms": p95_response_time_ms,
                "p99_response_time_ms": p99_response_time_ms,
                "requests_per_minute": requests_per_minute,
                "tokens_per_minute": tokens_per_minute,
                "total_errors": total_errors,
                "error_rate": error_rate,
                "errors_by_type": errors_by_type,
                "performance_by_model": performance_by_model,
                "performance_by_provider": performance_by_provider,
                "database_response_time_ms": database_response_time_ms,
                "vector_search_time_ms": vector_search_time_ms,
                "embedding_generation_time_ms": embedding_generation_time_ms,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.performance_metrics_response_errors_by_type import PerformanceMetricsResponseErrorsByType
        from ..models.performance_metrics_response_performance_by_model import (
            PerformanceMetricsResponsePerformanceByModel,
        )
        from ..models.performance_metrics_response_performance_by_provider import (
            PerformanceMetricsResponsePerformanceByProvider,
        )

        d = dict(src_dict)
        avg_response_time_ms = d.pop("avg_response_time_ms")

        median_response_time_ms = d.pop("median_response_time_ms")

        p95_response_time_ms = d.pop("p95_response_time_ms")

        p99_response_time_ms = d.pop("p99_response_time_ms")

        requests_per_minute = d.pop("requests_per_minute")

        tokens_per_minute = d.pop("tokens_per_minute")

        total_errors = d.pop("total_errors")

        error_rate = d.pop("error_rate")

        errors_by_type = PerformanceMetricsResponseErrorsByType.from_dict(d.pop("errors_by_type"))

        performance_by_model = PerformanceMetricsResponsePerformanceByModel.from_dict(d.pop("performance_by_model"))

        performance_by_provider = PerformanceMetricsResponsePerformanceByProvider.from_dict(
            d.pop("performance_by_provider")
        )

        database_response_time_ms = d.pop("database_response_time_ms")

        vector_search_time_ms = d.pop("vector_search_time_ms")

        embedding_generation_time_ms = d.pop("embedding_generation_time_ms")

        performance_metrics_response = cls(
            avg_response_time_ms=avg_response_time_ms,
            median_response_time_ms=median_response_time_ms,
            p95_response_time_ms=p95_response_time_ms,
            p99_response_time_ms=p99_response_time_ms,
            requests_per_minute=requests_per_minute,
            tokens_per_minute=tokens_per_minute,
            total_errors=total_errors,
            error_rate=error_rate,
            errors_by_type=errors_by_type,
            performance_by_model=performance_by_model,
            performance_by_provider=performance_by_provider,
            database_response_time_ms=database_response_time_ms,
            vector_search_time_ms=vector_search_time_ms,
            embedding_generation_time_ms=embedding_generation_time_ms,
        )

        performance_metrics_response.additional_properties = d
        return performance_metrics_response

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
