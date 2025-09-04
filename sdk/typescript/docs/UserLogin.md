# UserLogin

Schema for user login.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **string** |  | [optional] [default to undefined]
**username** | **string** |  | [optional] [default to undefined]
**password** | **string** | Password | [default to undefined]
**remember_me** | **boolean** | Remember login | [optional] [default to false]

## Example

```typescript
import { UserLogin } from 'chatter-sdk';

const instance: UserLogin = {
    email,
    username,
    password,
    remember_me,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
