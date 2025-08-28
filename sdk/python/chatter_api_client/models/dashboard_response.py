import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.conversation_stats_response import ConversationStatsResponse
    from ..models.dashboard_response_custom_metrics_item import DashboardResponseCustomMetricsItem
    from ..models.document_analytics_response import DocumentAnalyticsResponse
    from ..models.performance_metrics_response import PerformanceMetricsResponse
    from ..models.system_analytics_response import SystemAnalyticsResponse
    from ..models.usage_metrics_response import UsageMetricsResponse


T = TypeVar("T", bound="DashboardResponse")


@_attrs_define
class DashboardResponse:
    """Schema for analytics dashboard response.

    Attributes:
        conversation_stats (ConversationStatsResponse): Schema for conversation statistics response.
        usage_metrics (UsageMetricsResponse): Schema for usage metrics response.
        performance_metrics (PerformanceMetricsResponse): Schema for performance metrics response.
        document_analytics (DocumentAnalyticsResponse): Schema for document analytics response.
        system_health (SystemAnalyticsResponse): Schema for system analytics response.
        custom_metrics (list['DashboardResponseCustomMetricsItem']): Custom metrics
        generated_at (datetime.datetime): Dashboard generation time
    """

    conversation_stats: "ConversationStatsResponse"
    usage_metrics: "UsageMetricsResponse"
    performance_metrics: "PerformanceMetricsResponse"
    document_analytics: "DocumentAnalyticsResponse"
    system_health: "SystemAnalyticsResponse"
    custom_metrics: list["DashboardResponseCustomMetricsItem"]
    generated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conversation_stats = self.conversation_stats.to_dict()

        usage_metrics = self.usage_metrics.to_dict()

        performance_metrics = self.performance_metrics.to_dict()

        document_analytics = self.document_analytics.to_dict()

        system_health = self.system_health.to_dict()

        custom_metrics = []
        for custom_metrics_item_data in self.custom_metrics:
            custom_metrics_item = custom_metrics_item_data.to_dict()
            custom_metrics.append(custom_metrics_item)

        generated_at = self.generated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conversation_stats": conversation_stats,
                "usage_metrics": usage_metrics,
                "performance_metrics": performance_metrics,
                "document_analytics": document_analytics,
                "system_health": system_health,
                "custom_metrics": custom_metrics,
                "generated_at": generated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_stats_response import ConversationStatsResponse
        from ..models.dashboard_response_custom_metrics_item import DashboardResponseCustomMetricsItem
        from ..models.document_analytics_response import DocumentAnalyticsResponse
        from ..models.performance_metrics_response import PerformanceMetricsResponse
        from ..models.system_analytics_response import SystemAnalyticsResponse
        from ..models.usage_metrics_response import UsageMetricsResponse

        d = dict(src_dict)
        conversation_stats = ConversationStatsResponse.from_dict(d.pop("conversation_stats"))

        usage_metrics = UsageMetricsResponse.from_dict(d.pop("usage_metrics"))

        performance_metrics = PerformanceMetricsResponse.from_dict(d.pop("performance_metrics"))

        document_analytics = DocumentAnalyticsResponse.from_dict(d.pop("document_analytics"))

        system_health = SystemAnalyticsResponse.from_dict(d.pop("system_health"))

        custom_metrics = []
        _custom_metrics = d.pop("custom_metrics")
        for custom_metrics_item_data in _custom_metrics:
            custom_metrics_item = DashboardResponseCustomMetricsItem.from_dict(custom_metrics_item_data)

            custom_metrics.append(custom_metrics_item)

        generated_at = isoparse(d.pop("generated_at"))

        dashboard_response = cls(
            conversation_stats=conversation_stats,
            usage_metrics=usage_metrics,
            performance_metrics=performance_metrics,
            document_analytics=document_analytics,
            system_health=system_health,
            custom_metrics=custom_metrics,
            generated_at=generated_at,
        )

        dashboard_response.additional_properties = d
        return dashboard_response

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
