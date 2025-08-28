from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.usage_metrics_response_cost_by_model import UsageMetricsResponseCostByModel
    from ..models.usage_metrics_response_cost_by_provider import UsageMetricsResponseCostByProvider
    from ..models.usage_metrics_response_daily_cost import UsageMetricsResponseDailyCost
    from ..models.usage_metrics_response_daily_usage import UsageMetricsResponseDailyUsage
    from ..models.usage_metrics_response_response_times_by_model import UsageMetricsResponseResponseTimesByModel
    from ..models.usage_metrics_response_tokens_by_model import UsageMetricsResponseTokensByModel
    from ..models.usage_metrics_response_tokens_by_provider import UsageMetricsResponseTokensByProvider


T = TypeVar("T", bound="UsageMetricsResponse")


@_attrs_define
class UsageMetricsResponse:
    """Schema for usage metrics response.

    Attributes:
        total_prompt_tokens (int): Total prompt tokens
        total_completion_tokens (int): Total completion tokens
        total_tokens (int): Total tokens used
        tokens_by_model (UsageMetricsResponseTokensByModel): Token usage by model
        tokens_by_provider (UsageMetricsResponseTokensByProvider): Token usage by provider
        total_cost (float): Total cost
        cost_by_model (UsageMetricsResponseCostByModel): Cost by model
        cost_by_provider (UsageMetricsResponseCostByProvider): Cost by provider
        daily_usage (UsageMetricsResponseDailyUsage): Daily token usage
        daily_cost (UsageMetricsResponseDailyCost): Daily cost
        avg_response_time (float): Average response time
        response_times_by_model (UsageMetricsResponseResponseTimesByModel): Response times by model
        active_days (int): Number of active days
        peak_usage_hour (int): Peak usage hour
        conversations_per_day (float): Average conversations per day
    """

    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    tokens_by_model: "UsageMetricsResponseTokensByModel"
    tokens_by_provider: "UsageMetricsResponseTokensByProvider"
    total_cost: float
    cost_by_model: "UsageMetricsResponseCostByModel"
    cost_by_provider: "UsageMetricsResponseCostByProvider"
    daily_usage: "UsageMetricsResponseDailyUsage"
    daily_cost: "UsageMetricsResponseDailyCost"
    avg_response_time: float
    response_times_by_model: "UsageMetricsResponseResponseTimesByModel"
    active_days: int
    peak_usage_hour: int
    conversations_per_day: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_prompt_tokens = self.total_prompt_tokens

        total_completion_tokens = self.total_completion_tokens

        total_tokens = self.total_tokens

        tokens_by_model = self.tokens_by_model.to_dict()

        tokens_by_provider = self.tokens_by_provider.to_dict()

        total_cost = self.total_cost

        cost_by_model = self.cost_by_model.to_dict()

        cost_by_provider = self.cost_by_provider.to_dict()

        daily_usage = self.daily_usage.to_dict()

        daily_cost = self.daily_cost.to_dict()

        avg_response_time = self.avg_response_time

        response_times_by_model = self.response_times_by_model.to_dict()

        active_days = self.active_days

        peak_usage_hour = self.peak_usage_hour

        conversations_per_day = self.conversations_per_day

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_prompt_tokens": total_prompt_tokens,
                "total_completion_tokens": total_completion_tokens,
                "total_tokens": total_tokens,
                "tokens_by_model": tokens_by_model,
                "tokens_by_provider": tokens_by_provider,
                "total_cost": total_cost,
                "cost_by_model": cost_by_model,
                "cost_by_provider": cost_by_provider,
                "daily_usage": daily_usage,
                "daily_cost": daily_cost,
                "avg_response_time": avg_response_time,
                "response_times_by_model": response_times_by_model,
                "active_days": active_days,
                "peak_usage_hour": peak_usage_hour,
                "conversations_per_day": conversations_per_day,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_metrics_response_cost_by_model import UsageMetricsResponseCostByModel
        from ..models.usage_metrics_response_cost_by_provider import UsageMetricsResponseCostByProvider
        from ..models.usage_metrics_response_daily_cost import UsageMetricsResponseDailyCost
        from ..models.usage_metrics_response_daily_usage import UsageMetricsResponseDailyUsage
        from ..models.usage_metrics_response_response_times_by_model import UsageMetricsResponseResponseTimesByModel
        from ..models.usage_metrics_response_tokens_by_model import UsageMetricsResponseTokensByModel
        from ..models.usage_metrics_response_tokens_by_provider import UsageMetricsResponseTokensByProvider

        d = dict(src_dict)
        total_prompt_tokens = d.pop("total_prompt_tokens")

        total_completion_tokens = d.pop("total_completion_tokens")

        total_tokens = d.pop("total_tokens")

        tokens_by_model = UsageMetricsResponseTokensByModel.from_dict(d.pop("tokens_by_model"))

        tokens_by_provider = UsageMetricsResponseTokensByProvider.from_dict(d.pop("tokens_by_provider"))

        total_cost = d.pop("total_cost")

        cost_by_model = UsageMetricsResponseCostByModel.from_dict(d.pop("cost_by_model"))

        cost_by_provider = UsageMetricsResponseCostByProvider.from_dict(d.pop("cost_by_provider"))

        daily_usage = UsageMetricsResponseDailyUsage.from_dict(d.pop("daily_usage"))

        daily_cost = UsageMetricsResponseDailyCost.from_dict(d.pop("daily_cost"))

        avg_response_time = d.pop("avg_response_time")

        response_times_by_model = UsageMetricsResponseResponseTimesByModel.from_dict(d.pop("response_times_by_model"))

        active_days = d.pop("active_days")

        peak_usage_hour = d.pop("peak_usage_hour")

        conversations_per_day = d.pop("conversations_per_day")

        usage_metrics_response = cls(
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            tokens_by_model=tokens_by_model,
            tokens_by_provider=tokens_by_provider,
            total_cost=total_cost,
            cost_by_model=cost_by_model,
            cost_by_provider=cost_by_provider,
            daily_usage=daily_usage,
            daily_cost=daily_cost,
            avg_response_time=avg_response_time,
            response_times_by_model=response_times_by_model,
            active_days=active_days,
            peak_usage_hour=peak_usage_hour,
            conversations_per_day=conversations_per_day,
        )

        usage_metrics_response.additional_properties = d
        return usage_metrics_response

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
