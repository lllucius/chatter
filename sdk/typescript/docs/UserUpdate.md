# UserUpdate

Schema for user profile updates.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **string** |  | [optional] [default to undefined]
**full_name** | **string** |  | [optional] [default to undefined]
**bio** | **string** |  | [optional] [default to undefined]
**avatar_url** | **string** |  | [optional] [default to undefined]
**phone_number** | **string** |  | [optional] [default to undefined]
**default_llm_provider** | **string** |  | [optional] [default to undefined]
**default_profile_id** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { UserUpdate } from 'chatter-sdk';

const instance: UserUpdate = {
    email,
    full_name,
    bio,
    avatar_url,
    phone_number,
    default_llm_provider,
    default_profile_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
