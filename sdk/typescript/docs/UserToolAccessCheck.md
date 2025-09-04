# UserToolAccessCheck

Schema for checking user tool access.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **string** | User ID | [default to undefined]
**tool_name** | **string** | Tool name | [default to undefined]
**server_name** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { UserToolAccessCheck } from 'chatter-sdk';

const instance: UserToolAccessCheck = {
    user_id,
    tool_name,
    server_name,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
