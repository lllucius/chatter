# WebhookEventResponse

Response schema for webhook event data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Event ID | [default to undefined]
**event_type** | [**WebhookEventType**](WebhookEventType.md) | Event type | [default to undefined]
**data** | **{ [key: string]: any; }** | Event data | [default to undefined]
**timestamp** | **string** | Event timestamp | [default to undefined]
**metadata** | **{ [key: string]: any; }** | Event metadata | [default to undefined]

## Example

```typescript
import { WebhookEventResponse } from 'chatter-sdk';

const instance: WebhookEventResponse = {
    id,
    event_type,
    data,
    timestamp,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
