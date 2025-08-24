"""Webhook management endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.webhooks import (
    WebhookCreateRequest,
    WebhookDeleteResponse,
    WebhookListRequest,
    WebhookListResponse,
    WebhookResponse,
    WebhookTestResponse,
    WebhookUpdateRequest,
    WebhookEventResponse,
    WebhookEventsListResponse,
    WebhookDeliveryResponse,
    WebhookDeliveriesListResponse,
)
from chatter.services.webhooks import WebhookManager
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_webhook_manager() -> WebhookManager:
    """Get webhook manager instance.
    
    Returns:
        WebhookManager instance
    """
    return WebhookManager()


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreateRequest,
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookResponse:
    """Create a new webhook endpoint.
    
    Args:
        webhook_data: Webhook creation data
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        Created webhook data
    """
    try:
        endpoint_id = await webhook_manager.register_endpoint(
            name=webhook_data.name,
            url=webhook_data.url,
            events=webhook_data.events,
            secret=webhook_data.secret,
            headers=webhook_data.headers,
            timeout=webhook_data.timeout,
            max_retries=webhook_data.max_retries,
            metadata=webhook_data.metadata,
        )
        
        endpoint = webhook_manager.endpoints.get(endpoint_id)
        if not endpoint:
            raise InternalServerProblem(detail="Failed to retrieve created webhook")
        
        return WebhookResponse(
            id=endpoint.id,
            name=endpoint.name,
            url=endpoint.url,
            events=endpoint.events,
            active=endpoint.active,
            timeout=endpoint.timeout,
            max_retries=endpoint.max_retries,
            total_deliveries=endpoint.total_deliveries,
            successful_deliveries=endpoint.successful_deliveries,
            failed_deliveries=endpoint.failed_deliveries,
            last_delivery_at=endpoint.last_delivery_at,
            last_success_at=endpoint.last_success_at,
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at,
            metadata=endpoint.metadata,
        )
        
    except Exception as e:
        logger.error("Failed to create webhook", error=str(e))
        raise InternalServerProblem(detail="Failed to create webhook") from e


@router.get("/", response_model=WebhookListResponse)
async def list_webhooks(
    request: WebhookListRequest = Depends(),
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookListResponse:
    """List webhook endpoints with optional filtering.
    
    Args:
        request: List request parameters
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        List of webhook endpoints
    """
    try:
        endpoints = list(webhook_manager.endpoints.values())
        
        # Apply filters
        if request.active is not None:
            endpoints = [e for e in endpoints if e.active == request.active]
        
        if request.event_type is not None:
            endpoints = [e for e in endpoints if request.event_type in e.events]
        
        webhook_responses = []
        for endpoint in endpoints:
            webhook_responses.append(WebhookResponse(
                id=endpoint.id,
                name=endpoint.name,
                url=endpoint.url,
                events=endpoint.events,
                active=endpoint.active,
                timeout=endpoint.timeout,
                max_retries=endpoint.max_retries,
                total_deliveries=endpoint.total_deliveries,
                successful_deliveries=endpoint.successful_deliveries,
                failed_deliveries=endpoint.failed_deliveries,
                last_delivery_at=endpoint.last_delivery_at,
                last_success_at=endpoint.last_success_at,
                created_at=endpoint.created_at,
                updated_at=endpoint.updated_at,
                metadata=endpoint.metadata,
            ))
        
        return WebhookListResponse(
            webhooks=webhook_responses,
            total=len(webhook_responses)
        )
        
    except Exception as e:
        logger.error("Failed to list webhooks", error=str(e))
        raise InternalServerProblem(detail="Failed to list webhooks") from e


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookResponse:
    """Get webhook endpoint by ID.
    
    Args:
        webhook_id: Webhook ID
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        Webhook endpoint data
    """
    try:
        endpoint = webhook_manager.endpoints.get(webhook_id)
        if not endpoint:
            raise NotFoundProblem(detail=f"Webhook {webhook_id} not found")
        
        return WebhookResponse(
            id=endpoint.id,
            name=endpoint.name,
            url=endpoint.url,
            events=endpoint.events,
            active=endpoint.active,
            timeout=endpoint.timeout,
            max_retries=endpoint.max_retries,
            total_deliveries=endpoint.total_deliveries,
            successful_deliveries=endpoint.successful_deliveries,
            failed_deliveries=endpoint.failed_deliveries,
            last_delivery_at=endpoint.last_delivery_at,
            last_success_at=endpoint.last_success_at,
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at,
            metadata=endpoint.metadata,
        )
        
    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to get webhook", webhook_id=webhook_id, error=str(e))
        raise InternalServerProblem(detail="Failed to get webhook") from e


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook_data: WebhookUpdateRequest,
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookResponse:
    """Update a webhook endpoint.
    
    Args:
        webhook_id: Webhook ID
        webhook_data: Webhook update data
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        Updated webhook data
    """
    try:
        endpoint = webhook_manager.endpoints.get(webhook_id)
        if not endpoint:
            raise NotFoundProblem(detail=f"Webhook {webhook_id} not found")
        
        # Update endpoint with provided data
        update_data = webhook_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(endpoint, field):
                setattr(endpoint, field, value)
        
        # Update timestamp
        from datetime import UTC, datetime
        endpoint.updated_at = datetime.now(UTC)
        
        return WebhookResponse(
            id=endpoint.id,
            name=endpoint.name,
            url=endpoint.url,
            events=endpoint.events,
            active=endpoint.active,
            timeout=endpoint.timeout,
            max_retries=endpoint.max_retries,
            total_deliveries=endpoint.total_deliveries,
            successful_deliveries=endpoint.successful_deliveries,
            failed_deliveries=endpoint.failed_deliveries,
            last_delivery_at=endpoint.last_delivery_at,
            last_success_at=endpoint.last_success_at,
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at,
            metadata=endpoint.metadata,
        )
        
    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to update webhook", webhook_id=webhook_id, error=str(e))
        raise InternalServerProblem(detail="Failed to update webhook") from e


@router.delete("/{webhook_id}", response_model=WebhookDeleteResponse)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookDeleteResponse:
    """Delete a webhook endpoint.
    
    Args:
        webhook_id: Webhook ID
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        Deletion result
    """
    try:
        if webhook_id not in webhook_manager.endpoints:
            raise NotFoundProblem(detail=f"Webhook {webhook_id} not found")
        
        # Remove from endpoints
        del webhook_manager.endpoints[webhook_id]
        
        return WebhookDeleteResponse(
            success=True,
            message=f"Webhook {webhook_id} deleted successfully"
        )
        
    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to delete webhook", webhook_id=webhook_id, error=str(e))
        raise InternalServerProblem(detail="Failed to delete webhook") from e


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookTestResponse:
    """Test a webhook endpoint by sending a test event.
    
    Args:
        webhook_id: Webhook ID
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        Test result
    """
    try:
        result = await webhook_manager.test_endpoint(webhook_id)
        
        return WebhookTestResponse(
            success=result["success"],
            status_code=result.get("status_code"),
            response_body=result.get("response_body"),
            response_time=result.get("response_time"),
            error=result.get("error"),
        )
        
    except Exception as e:
        logger.error("Failed to test webhook", webhook_id=webhook_id, error=str(e))
        return WebhookTestResponse(
            success=False,
            error=f"Failed to test webhook: {str(e)}"
        )


@router.get("/events/list", response_model=WebhookEventsListResponse)
async def list_webhook_events(
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookEventsListResponse:
    """List recent webhook events.
    
    Args:
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        List of recent webhook events
    """
    try:
        # This would need to be implemented in the webhook manager
        # For now, return a placeholder response
        events = []
        
        return WebhookEventsListResponse(
            events=events,
            total=len(events)
        )
        
    except Exception as e:
        logger.error("Failed to list webhook events", error=str(e))
        raise InternalServerProblem(detail="Failed to list webhook events") from e


@router.get("/deliveries/list", response_model=WebhookDeliveriesListResponse)
async def list_webhook_deliveries(
    webhook_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    webhook_manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookDeliveriesListResponse:
    """List webhook delivery attempts.
    
    Args:
        webhook_id: Optional webhook ID to filter by
        current_user: Current authenticated user
        webhook_manager: Webhook manager instance
        
    Returns:
        List of webhook deliveries
    """
    try:
        # This would need to be implemented in the webhook manager
        # For now, return a placeholder response
        deliveries = []
        
        return WebhookDeliveriesListResponse(
            deliveries=deliveries,
            total=len(deliveries)
        )
        
    except Exception as e:
        logger.error("Failed to list webhook deliveries", error=str(e))
        raise InternalServerProblem(detail="Failed to list webhook deliveries") from e