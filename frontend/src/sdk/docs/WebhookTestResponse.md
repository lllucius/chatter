# WebhookTestResponse

Response schema for webhook endpoint testing.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** | Whether test was successful | [default to undefined]
**status_code** | **number** |  | [optional] [default to undefined]
**response_body** | **string** |  | [optional] [default to undefined]
**response_time** | **number** |  | [optional] [default to undefined]
**error** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { WebhookTestResponse } from 'chatter-sdk';

const instance: WebhookTestResponse = {
    success,
    status_code,
    response_body,
    response_time,
    error,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
