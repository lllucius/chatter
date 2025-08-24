# WebhookResponse

Response schema for webhook endpoint data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Webhook endpoint ID | [default to undefined]
**name** | **string** | Webhook endpoint name | [default to undefined]
**url** | **string** | Webhook URL | [default to undefined]
**events** | [**Array&lt;WebhookEventType&gt;**](WebhookEventType.md) | Subscribed events | [default to undefined]
**active** | **boolean** | Whether webhook is active | [default to undefined]
**timeout** | **number** | Request timeout in seconds | [default to undefined]
**max_retries** | **number** | Maximum retry attempts | [default to undefined]
**total_deliveries** | **number** | Total delivery attempts | [optional] [default to 0]
**successful_deliveries** | **number** | Successful deliveries | [optional] [default to 0]
**failed_deliveries** | **number** | Failed deliveries | [optional] [default to 0]
**last_delivery_at** | **string** |  | [optional] [default to undefined]
**last_success_at** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]
**metadata** | **{ [key: string]: any; }** | Additional metadata | [default to undefined]

## Example

```typescript
import { WebhookResponse } from 'chatter-sdk';

const instance: WebhookResponse = {
    id,
    name,
    url,
    events,
    active,
    timeout,
    max_retries,
    total_deliveries,
    successful_deliveries,
    failed_deliveries,
    last_delivery_at,
    last_success_at,
    created_at,
    updated_at,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
