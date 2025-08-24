# WebhookEventsListResponse

Response schema for webhook events list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**events** | [**Array&lt;WebhookEventResponse&gt;**](WebhookEventResponse.md) | List of webhook events | [default to undefined]
**total** | **number** | Total number of events | [default to undefined]

## Example

```typescript
import { WebhookEventsListResponse } from 'chatter-sdk';

const instance: WebhookEventsListResponse = {
    events,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
