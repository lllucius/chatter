"""Webhook management schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chatter.schemas.common import (
    ListRequestBase,
)
from chatter.services.webhooks import WebhookEventType


class WebhookCreateRequest(BaseModel):
    """Request schema for creating a webhook endpoint."""

    name: str = Field(..., description="Webhook endpoint name")
    url: str = Field(..., description="Webhook URL")
    events: list[WebhookEventType] = Field(..., min_items=1, description="Events to subscribe to")

    # Optional configuration
    secret: str | None = Field(None, description="Webhook secret for signature verification")
    headers: dict[str, str] | None = Field(None, description="Additional headers to send")
    timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class WebhookUpdateRequest(BaseModel):
    """Request schema for updating a webhook endpoint."""

    name: str | None = Field(None, description="Webhook endpoint name")
    url: str | None = Field(None, description="Webhook URL")
    events: list[WebhookEventType] | None = Field(None, description="Events to subscribe to")
    active: bool | None = Field(None, description="Whether webhook is active")

    # Optional configuration
    secret: str | None = Field(None, description="Webhook secret")
    headers: dict[str, str] | None = Field(None, description="Additional headers")
    timeout: int | None = Field(None, ge=1, le=300, description="Request timeout")
    max_retries: int | None = Field(None, ge=0, le=10, description="Maximum retries")

    # Metadata
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class WebhookResponse(BaseModel):
    """Response schema for webhook endpoint data."""

    id: str = Field(..., description="Webhook endpoint ID")
    name: str = Field(..., description="Webhook endpoint name")
    url: str = Field(..., description="Webhook URL")
    events: list[WebhookEventType] = Field(..., description="Subscribed events")
    active: bool = Field(..., description="Whether webhook is active")

    # Configuration
    timeout: int = Field(..., description="Request timeout in seconds")
    max_retries: int = Field(..., description="Maximum retry attempts")

    # Statistics
    total_deliveries: int = Field(0, description="Total delivery attempts")
    successful_deliveries: int = Field(0, description="Successful deliveries")
    failed_deliveries: int = Field(0, description="Failed deliveries")
    last_delivery_at: datetime | None = Field(None, description="Last delivery attempt")
    last_success_at: datetime | None = Field(None, description="Last successful delivery")

    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: dict[str, Any] = Field(..., description="Additional metadata")


class WebhookListRequest(ListRequestBase):
    """Request schema for listing webhook endpoints."""

    active: bool | None = Field(None, description="Filter by active status")
    event_type: WebhookEventType | None = Field(None, description="Filter by event type")


class WebhookListResponse(BaseModel):
    """Response schema for webhook endpoint list."""

    webhooks: list[WebhookResponse] = Field(..., description="List of webhook endpoints")
    total: int = Field(..., description="Total number of webhooks")


class WebhookDeleteResponse(BaseModel):
    """Response schema for webhook deletion."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion result message")


class WebhookTestResponse(BaseModel):
    """Response schema for webhook endpoint testing."""

    success: bool = Field(..., description="Whether test was successful")
    status_code: int | None = Field(None, description="HTTP status code")
    response_body: str | None = Field(None, description="Response body")
    response_time: float | None = Field(None, description="Response time in seconds")
    error: str | None = Field(None, description="Error message if failed")


class WebhookEventResponse(BaseModel):
    """Response schema for webhook event data."""

    id: str = Field(..., description="Event ID")
    event_type: WebhookEventType = Field(..., description="Event type")
    data: dict[str, Any] = Field(..., description="Event data")
    timestamp: datetime = Field(..., description="Event timestamp")
    metadata: dict[str, Any] = Field(..., description="Event metadata")


class WebhookEventsListResponse(BaseModel):
    """Response schema for webhook events list."""

    events: list[WebhookEventResponse] = Field(..., description="List of webhook events")
    total: int = Field(..., description="Total number of events")


class WebhookDeliveryResponse(BaseModel):
    """Response schema for webhook delivery data."""

    id: str = Field(..., description="Delivery ID")
    webhook_endpoint_id: str = Field(..., description="Webhook endpoint ID")
    event_id: str = Field(..., description="Event ID")
    event_type: WebhookEventType = Field(..., description="Event type")

    # Delivery details
    attempt_number: int = Field(..., description="Delivery attempt number")
    status: str = Field(..., description="Delivery status")

    # Response details
    response_status: int | None = Field(None, description="HTTP response status")
    response_body: str | None = Field(None, description="Response body")
    response_time: float | None = Field(None, description="Response time in seconds")
    error_message: str | None = Field(None, description="Error message if failed")

    # Timing
    attempted_at: datetime = Field(..., description="Delivery attempt timestamp")
    completed_at: datetime | None = Field(None, description="Delivery completion timestamp")
    next_retry_at: datetime | None = Field(None, description="Next retry timestamp")


class WebhookDeliveriesListResponse(BaseModel):
    """Response schema for webhook deliveries list."""

    deliveries: list[WebhookDeliveryResponse] = Field(..., description="List of webhook deliveries")
    total: int = Field(..., description="Total number of deliveries")
