# WebhookCreateRequest

Request schema for creating a webhook endpoint.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Webhook endpoint name | [default to undefined]
**url** | **string** | Webhook URL | [default to undefined]
**events** | [**Array&lt;WebhookEventType&gt;**](WebhookEventType.md) | Events to subscribe to | [default to undefined]
**secret** | **string** |  | [optional] [default to undefined]
**headers** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**timeout** | **number** | Request timeout in seconds | [optional] [default to 30]
**max_retries** | **number** | Maximum retry attempts | [optional] [default to 3]
**metadata** | **{ [key: string]: any; }** | Additional metadata | [optional] [default to undefined]

## Example

```typescript
import { WebhookCreateRequest } from 'chatter-sdk';

const instance: WebhookCreateRequest = {
    name,
    url,
    events,
    secret,
    headers,
    timeout,
    max_retries,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
