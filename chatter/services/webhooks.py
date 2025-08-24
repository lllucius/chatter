"""Webhook system for external integrations."""

import asyncio
import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, Field

from chatter.config import settings
from chatter.services.job_queue import job_queue
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WebhookEventType(str, Enum):
    """Types of webhook events."""
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_ENDED = "conversation.ended"
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSED = "document.processed"
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    SYSTEM_ALERT = "system.alert"


class WebhookStatus(str, Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class WebhookEndpoint(BaseModel):
    """Webhook endpoint configuration."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    secret: Optional[str] = None
    active: bool = True
    events: List[WebhookEventType] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 60
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WebhookEvent(BaseModel):
    """Webhook event data."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: WebhookEventType
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: str = "chatter"
    version: str = "1.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WebhookDelivery(BaseModel):
    """Webhook delivery record."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    webhook_endpoint_id: str
    event_id: str
    status: WebhookStatus = WebhookStatus.PENDING
    attempts: int = 0
    last_attempt_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WebhookManager:
    """Manages webhook endpoints and event delivery."""

    def __init__(self):
        """Initialize the webhook manager."""
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.deliveries: Dict[str, WebhookDelivery] = {}
        self.event_history: List[WebhookEvent] = []
        self.max_history_size = 10000

    async def register_endpoint(
        self,
        name: str,
        url: str,
        events: List[WebhookEventType],
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Register a new webhook endpoint.
        
        Args:
            name: Endpoint name
            url: Webhook URL
            events: List of events to subscribe to
            secret: Optional secret for signature verification
            headers: Additional headers to send
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            metadata: Additional metadata
            
        Returns:
            Endpoint ID
        """
        endpoint = WebhookEndpoint(
            name=name,
            url=url,
            events=events,
            secret=secret,
            headers=headers or {},
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {},
        )

        self.endpoints[endpoint.id] = endpoint

        logger.info(
            f"Registered webhook endpoint",
            endpoint_id=endpoint.id,
            name=name,
            url=url,
            events=[e.value for e in events],
        )

        return endpoint.id

    async def update_endpoint(
        self, endpoint_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Update a webhook endpoint.
        
        Args:
            endpoint_id: Endpoint ID
            updates: Updates to apply
            
        Returns:
            True if updated, False if not found
        """
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return False

        for key, value in updates.items():
            if hasattr(endpoint, key):
                setattr(endpoint, key, value)

        endpoint.updated_at = datetime.now(UTC)

        logger.info(f"Updated webhook endpoint {endpoint_id}")
        return True

    async def delete_endpoint(self, endpoint_id: str) -> bool:
        """Delete a webhook endpoint.
        
        Args:
            endpoint_id: Endpoint ID
            
        Returns:
            True if deleted, False if not found
        """
        if endpoint_id in self.endpoints:
            del self.endpoints[endpoint_id]
            logger.info(f"Deleted webhook endpoint {endpoint_id}")
            return True
        return False

    async def list_endpoints(
        self, active_only: bool = True
    ) -> List[WebhookEndpoint]:
        """List webhook endpoints.
        
        Args:
            active_only: Only return active endpoints
            
        Returns:
            List of webhook endpoints
        """
        endpoints = list(self.endpoints.values())
        if active_only:
            endpoints = [ep for ep in endpoints if ep.active]
        return endpoints

    async def trigger_event(
        self,
        event_type: WebhookEventType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Trigger a webhook event.
        
        Args:
            event_type: Type of event
            data: Event data
            metadata: Additional metadata
            
        Returns:
            Event ID
        """
        event = WebhookEvent(
            event_type=event_type,
            data=data,
            metadata=metadata or {},
        )

        # Store event in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)

        # Find matching endpoints
        matching_endpoints = [
            endpoint for endpoint in self.endpoints.values()
            if endpoint.active and event_type in endpoint.events
        ]

        logger.info(
            f"Triggered webhook event",
            event_id=event.id,
            event_type=event_type.value,
            matching_endpoints=len(matching_endpoints),
        )

        # Schedule deliveries
        for endpoint in matching_endpoints:
            await self._schedule_delivery(endpoint, event)

        return event.id

    async def _schedule_delivery(
        self, endpoint: WebhookEndpoint, event: WebhookEvent
    ) -> None:
        """Schedule webhook delivery.
        
        Args:
            endpoint: Webhook endpoint
            event: Event to deliver
        """
        delivery = WebhookDelivery(
            webhook_endpoint_id=endpoint.id,
            event_id=event.id,
        )

        self.deliveries[delivery.id] = delivery

        # Add delivery job to queue
        await job_queue.add_job(
            name=f"webhook_delivery_{delivery.id}",
            function_name="webhook_delivery",
            args=[delivery.id],
            priority="high",
            max_retries=endpoint.max_retries,
            timeout=endpoint.timeout,
            tags=["webhook", "delivery"],
            metadata={
                "endpoint_id": endpoint.id,
                "event_type": event.event_type.value,
                "delivery_id": delivery.id,
            },
        )

    async def deliver_webhook(self, delivery_id: str) -> bool:
        """Deliver a webhook.
        
        Args:
            delivery_id: Delivery ID
            
        Returns:
            True if delivered successfully, False otherwise
        """
        delivery = self.deliveries.get(delivery_id)
        if not delivery:
            logger.error(f"Delivery {delivery_id} not found")
            return False

        endpoint = self.endpoints.get(delivery.webhook_endpoint_id)
        if not endpoint:
            logger.error(f"Endpoint {delivery.webhook_endpoint_id} not found")
            return False

        # Find the event
        event = None
        for e in self.event_history:
            if e.id == delivery.event_id:
                event = e
                break

        if not event:
            logger.error(f"Event {delivery.event_id} not found")
            return False

        delivery.attempts += 1
        delivery.last_attempt_at = datetime.now(UTC)
        delivery.status = WebhookStatus.RETRYING if delivery.attempts > 1 else WebhookStatus.PENDING

        try:
            # Prepare payload
            payload = {
                "event": {
                    "id": event.id,
                    "type": event.event_type.value,
                    "created_at": event.timestamp.isoformat(),
                    "data": event.data,
                    "metadata": event.metadata,
                },
                "webhook": {
                    "id": endpoint.id,
                    "name": endpoint.name,
                },
                "delivery": {
                    "id": delivery.id,
                    "attempt": delivery.attempts,
                },
            }

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"Chatter-Webhook/1.0",
                "X-Webhook-Event": event.event_type.value,
                "X-Webhook-Delivery": delivery.id,
                **endpoint.headers,
            }

            # Add signature if secret is provided
            if endpoint.secret:
                payload_bytes = json.dumps(payload, sort_keys=True).encode()
                signature = hmac.new(
                    endpoint.secret.encode(),
                    payload_bytes,
                    hashlib.sha256,
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"

            # Send webhook
            async with httpx.AsyncClient(timeout=endpoint.timeout) as client:
                response = await client.post(
                    endpoint.url,
                    json=payload,
                    headers=headers,
                )

                delivery.response_status = response.status_code
                delivery.response_body = response.text[:1000]  # Limit response body size

                if response.status_code >= 200 and response.status_code < 300:
                    delivery.status = WebhookStatus.DELIVERED
                    delivery.delivered_at = datetime.now(UTC)
                    
                    logger.info(
                        f"Webhook delivered successfully",
                        delivery_id=delivery_id,
                        endpoint_id=endpoint.id,
                        status_code=response.status_code,
                        attempt=delivery.attempts,
                    )
                    return True
                else:
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}",
                        request=response.request,
                        response=response,
                    )

        except Exception as e:
            delivery.error_message = str(e)
            delivery.status = WebhookStatus.FAILED

            logger.error(
                f"Webhook delivery failed",
                delivery_id=delivery_id,
                endpoint_id=endpoint.id,
                attempt=delivery.attempts,
                error=str(e),
            )

            # Schedule retry if we haven't exceeded max attempts
            if delivery.attempts < endpoint.max_retries:
                await asyncio.sleep(endpoint.retry_delay)
                return await self.deliver_webhook(delivery_id)

            return False

    async def get_delivery_status(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Get delivery status.
        
        Args:
            delivery_id: Delivery ID
            
        Returns:
            Delivery record or None if not found
        """
        return self.deliveries.get(delivery_id)

    async def get_delivery_history(
        self,
        endpoint_id: Optional[str] = None,
        event_type: Optional[WebhookEventType] = None,
        status: Optional[WebhookStatus] = None,
        limit: int = 100,
    ) -> List[WebhookDelivery]:
        """Get delivery history with optional filtering.
        
        Args:
            endpoint_id: Filter by endpoint ID
            event_type: Filter by event type
            status: Filter by delivery status
            limit: Maximum number of records to return
            
        Returns:
            List of delivery records
        """
        deliveries = list(self.deliveries.values())

        if endpoint_id:
            deliveries = [d for d in deliveries if d.webhook_endpoint_id == endpoint_id]

        if status:
            deliveries = [d for d in deliveries if d.status == status]

        # Sort by creation time descending
        deliveries.sort(key=lambda x: x.created_at, reverse=True)

        return deliveries[:limit]

    async def get_event_history(
        self,
        event_type: Optional[WebhookEventType] = None,
        limit: int = 100,
    ) -> List[WebhookEvent]:
        """Get event history with optional filtering.
        
        Args:
            event_type: Filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = self.event_history.copy()

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Sort by timestamp descending
        events.sort(key=lambda x: x.timestamp, reverse=True)

        return events[:limit]

    async def test_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Test a webhook endpoint.
        
        Args:
            endpoint_id: Endpoint ID
            
        Returns:
            Test result
        """
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return {"success": False, "error": "Endpoint not found"}

        # Send test event
        test_event = WebhookEvent(
            event_type=WebhookEventType.SYSTEM_ALERT,
            data={"message": "This is a test webhook"},
            metadata={"test": True},
        )

        try:
            # Create temporary delivery for testing
            delivery = WebhookDelivery(
                webhook_endpoint_id=endpoint.id,
                event_id=test_event.id,
            )

            success = await self.deliver_webhook(delivery.id)

            return {
                "success": success,
                "status_code": delivery.response_status,
                "response_body": delivery.response_body,
                "error": delivery.error_message,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Global webhook manager
webhook_manager = WebhookManager()


# Register webhook delivery job handler
async def webhook_delivery_job(delivery_id: str) -> Dict[str, Any]:
    """Job handler for webhook delivery.
    
    Args:
        delivery_id: Delivery ID
        
    Returns:
        Delivery result
    """
    success = await webhook_manager.deliver_webhook(delivery_id)
    delivery = await webhook_manager.get_delivery_status(delivery_id)
    
    return {
        "delivery_id": delivery_id,
        "success": success,
        "status": delivery.status.value if delivery else "unknown",
        "attempts": delivery.attempts if delivery else 0,
    }


# Register the webhook delivery handler
job_queue.register_handler("webhook_delivery", webhook_delivery_job)


# Helper functions for common webhook events
async def trigger_conversation_started(conversation_id: str, user_id: str) -> str:
    """Trigger conversation started event."""
    return await webhook_manager.trigger_event(
        WebhookEventType.CONVERSATION_STARTED,
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "started_at": datetime.now(UTC).isoformat(),
        }
    )


async def trigger_message_received(
    conversation_id: str, user_id: str, message: str
) -> str:
    """Trigger message received event."""
    return await webhook_manager.trigger_event(
        WebhookEventType.MESSAGE_RECEIVED,
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "message": message,
            "received_at": datetime.now(UTC).isoformat(),
        }
    )


async def trigger_document_processed(
    document_id: str, user_id: str, processing_result: Dict[str, Any]
) -> str:
    """Trigger document processed event."""
    return await webhook_manager.trigger_event(
        WebhookEventType.DOCUMENT_PROCESSED,
        {
            "document_id": document_id,
            "user_id": user_id,
            "processing_result": processing_result,
            "processed_at": datetime.now(UTC).isoformat(),
        }
    )


async def trigger_job_completed(job_id: str, result: Dict[str, Any]) -> str:
    """Trigger job completed event."""
    return await webhook_manager.trigger_event(
        WebhookEventType.JOB_COMPLETED,
        {
            "job_id": job_id,
            "result": result,
            "completed_at": datetime.now(UTC).isoformat(),
        }
    )