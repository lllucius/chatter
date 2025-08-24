# WebhookDeliveriesListResponse

Response schema for webhook deliveries list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deliveries** | [**Array&lt;WebhookDeliveryResponse&gt;**](WebhookDeliveryResponse.md) | List of webhook deliveries | [default to undefined]
**total** | **number** | Total number of deliveries | [default to undefined]

## Example

```typescript
import { WebhookDeliveriesListResponse } from 'chatter-sdk';

const instance: WebhookDeliveriesListResponse = {
    deliveries,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
