# ProfileTestRequest

Schema for profile test request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_message** | **string** | Test message | [default to undefined]
**include_retrieval** | **boolean** | Include retrieval in test | [optional] [default to false]
**include_tools** | **boolean** | Include tools in test | [optional] [default to false]

## Example

```typescript
import { ProfileTestRequest } from 'chatter-sdk';

const instance: ProfileTestRequest = {
    test_message,
    include_retrieval,
    include_tools,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
