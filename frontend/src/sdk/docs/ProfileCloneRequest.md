# ProfileCloneRequest

Schema for profile clone request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | New profile name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**modifications** | [**ProfileUpdate**](ProfileUpdate.md) |  | [optional] [default to undefined]

## Example

```typescript
import { ProfileCloneRequest } from 'chatter-sdk';

const instance: ProfileCloneRequest = {
    name,
    description,
    modifications,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
