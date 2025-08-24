# WebhookListResponse

Response schema for webhook endpoint list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**webhooks** | [**Array&lt;WebhookResponse&gt;**](WebhookResponse.md) | List of webhook endpoints | [default to undefined]
**total** | **number** | Total number of webhooks | [default to undefined]

## Example

```typescript
import { WebhookListResponse } from 'chatter-sdk';

const instance: WebhookListResponse = {
    webhooks,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
