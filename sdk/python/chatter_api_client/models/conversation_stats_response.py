from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.conversation_stats_response_conversations_by_date import ConversationStatsResponseConversationsByDate
    from ..models.conversation_stats_response_conversations_by_status import (
        ConversationStatsResponseConversationsByStatus,
    )
    from ..models.conversation_stats_response_messages_by_role import ConversationStatsResponseMessagesByRole
    from ..models.conversation_stats_response_most_active_hours import ConversationStatsResponseMostActiveHours
    from ..models.conversation_stats_response_popular_models import ConversationStatsResponsePopularModels
    from ..models.conversation_stats_response_popular_providers import ConversationStatsResponsePopularProviders


T = TypeVar("T", bound="ConversationStatsResponse")


@_attrs_define
class ConversationStatsResponse:
    """Schema for conversation statistics response.

    Attributes:
        total_conversations (int): Total number of conversations
        conversations_by_status (ConversationStatsResponseConversationsByStatus): Conversations grouped by status
        total_messages (int): Total number of messages
        messages_by_role (ConversationStatsResponseMessagesByRole): Messages grouped by role
        avg_messages_per_conversation (float): Average messages per conversation
        total_tokens_used (int): Total tokens used
        total_cost (float): Total cost incurred
        avg_response_time_ms (float): Average response time in milliseconds
        conversations_by_date (ConversationStatsResponseConversationsByDate): Conversations by date
        most_active_hours (ConversationStatsResponseMostActiveHours): Most active hours
        popular_models (ConversationStatsResponsePopularModels): Popular LLM models
        popular_providers (ConversationStatsResponsePopularProviders): Popular LLM providers
    """

    total_conversations: int
    conversations_by_status: "ConversationStatsResponseConversationsByStatus"
    total_messages: int
    messages_by_role: "ConversationStatsResponseMessagesByRole"
    avg_messages_per_conversation: float
    total_tokens_used: int
    total_cost: float
    avg_response_time_ms: float
    conversations_by_date: "ConversationStatsResponseConversationsByDate"
    most_active_hours: "ConversationStatsResponseMostActiveHours"
    popular_models: "ConversationStatsResponsePopularModels"
    popular_providers: "ConversationStatsResponsePopularProviders"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_conversations = self.total_conversations

        conversations_by_status = self.conversations_by_status.to_dict()

        total_messages = self.total_messages

        messages_by_role = self.messages_by_role.to_dict()

        avg_messages_per_conversation = self.avg_messages_per_conversation

        total_tokens_used = self.total_tokens_used

        total_cost = self.total_cost

        avg_response_time_ms = self.avg_response_time_ms

        conversations_by_date = self.conversations_by_date.to_dict()

        most_active_hours = self.most_active_hours.to_dict()

        popular_models = self.popular_models.to_dict()

        popular_providers = self.popular_providers.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_conversations": total_conversations,
                "conversations_by_status": conversations_by_status,
                "total_messages": total_messages,
                "messages_by_role": messages_by_role,
                "avg_messages_per_conversation": avg_messages_per_conversation,
                "total_tokens_used": total_tokens_used,
                "total_cost": total_cost,
                "avg_response_time_ms": avg_response_time_ms,
                "conversations_by_date": conversations_by_date,
                "most_active_hours": most_active_hours,
                "popular_models": popular_models,
                "popular_providers": popular_providers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_stats_response_conversations_by_date import (
            ConversationStatsResponseConversationsByDate,
        )
        from ..models.conversation_stats_response_conversations_by_status import (
            ConversationStatsResponseConversationsByStatus,
        )
        from ..models.conversation_stats_response_messages_by_role import ConversationStatsResponseMessagesByRole
        from ..models.conversation_stats_response_most_active_hours import ConversationStatsResponseMostActiveHours
        from ..models.conversation_stats_response_popular_models import ConversationStatsResponsePopularModels
        from ..models.conversation_stats_response_popular_providers import ConversationStatsResponsePopularProviders

        d = dict(src_dict)
        total_conversations = d.pop("total_conversations")

        conversations_by_status = ConversationStatsResponseConversationsByStatus.from_dict(
            d.pop("conversations_by_status")
        )

        total_messages = d.pop("total_messages")

        messages_by_role = ConversationStatsResponseMessagesByRole.from_dict(d.pop("messages_by_role"))

        avg_messages_per_conversation = d.pop("avg_messages_per_conversation")

        total_tokens_used = d.pop("total_tokens_used")

        total_cost = d.pop("total_cost")

        avg_response_time_ms = d.pop("avg_response_time_ms")

        conversations_by_date = ConversationStatsResponseConversationsByDate.from_dict(d.pop("conversations_by_date"))

        most_active_hours = ConversationStatsResponseMostActiveHours.from_dict(d.pop("most_active_hours"))

        popular_models = ConversationStatsResponsePopularModels.from_dict(d.pop("popular_models"))

        popular_providers = ConversationStatsResponsePopularProviders.from_dict(d.pop("popular_providers"))

        conversation_stats_response = cls(
            total_conversations=total_conversations,
            conversations_by_status=conversations_by_status,
            total_messages=total_messages,
            messages_by_role=messages_by_role,
            avg_messages_per_conversation=avg_messages_per_conversation,
            total_tokens_used=total_tokens_used,
            total_cost=total_cost,
            avg_response_time_ms=avg_response_time_ms,
            conversations_by_date=conversations_by_date,
            most_active_hours=most_active_hours,
            popular_models=popular_models,
            popular_providers=popular_providers,
        )

        conversation_stats_response.additional_properties = d
        return conversation_stats_response

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
