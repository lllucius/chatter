# UserCreate

Schema for user creation (alias for UserRegistration).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **string** | User email address | [default to undefined]
**username** | **string** | Username | [default to undefined]
**full_name** | **string** |  | [optional] [default to undefined]
**bio** | **string** |  | [optional] [default to undefined]
**avatar_url** | **string** |  | [optional] [default to undefined]
**phone_number** | **string** |  | [optional] [default to undefined]
**password** | **string** | Password | [default to undefined]

## Example

```typescript
import { UserCreate } from 'chatter-sdk';

const instance: UserCreate = {
    email,
    username,
    full_name,
    bio,
    avatar_url,
    phone_number,
    password,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
