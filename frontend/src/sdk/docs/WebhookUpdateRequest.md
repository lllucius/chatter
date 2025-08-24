# WebhookUpdateRequest

Request schema for updating a webhook endpoint.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**url** | **string** |  | [optional] [default to undefined]
**events** | [**Array&lt;WebhookEventType&gt;**](WebhookEventType.md) |  | [optional] [default to undefined]
**active** | **boolean** |  | [optional] [default to undefined]
**secret** | **string** |  | [optional] [default to undefined]
**headers** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**timeout** | **number** |  | [optional] [default to undefined]
**max_retries** | **number** |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { WebhookUpdateRequest } from 'chatter-sdk';

const instance: WebhookUpdateRequest = {
    name,
    url,
    events,
    active,
    secret,
    headers,
    timeout,
    max_retries,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
