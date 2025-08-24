# WebhookDeliveryResponse

Response schema for webhook delivery data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Delivery ID | [default to undefined]
**webhook_endpoint_id** | **string** | Webhook endpoint ID | [default to undefined]
**event_id** | **string** | Event ID | [default to undefined]
**event_type** | [**WebhookEventType**](WebhookEventType.md) | Event type | [default to undefined]
**attempt_number** | **number** | Delivery attempt number | [default to undefined]
**status** | **string** | Delivery status | [default to undefined]
**response_status** | **number** |  | [optional] [default to undefined]
**response_body** | **string** |  | [optional] [default to undefined]
**response_time** | **number** |  | [optional] [default to undefined]
**error_message** | **string** |  | [optional] [default to undefined]
**attempted_at** | **string** | Delivery attempt timestamp | [default to undefined]
**completed_at** | **string** |  | [optional] [default to undefined]
**next_retry_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { WebhookDeliveryResponse } from 'chatter-sdk';

const instance: WebhookDeliveryResponse = {
    id,
    webhook_endpoint_id,
    event_id,
    event_type,
    attempt_number,
    status,
    response_status,
    response_body,
    response_time,
    error_message,
    attempted_at,
    completed_at,
    next_retry_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
