# TokenResponse

Schema for authentication token response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_token** | **string** | JWT access token | [default to undefined]
**refresh_token** | **string** | JWT refresh token | [default to undefined]
**token_type** | **string** | Token type | [optional] [default to 'bearer']
**expires_in** | **number** | Token expiration time in seconds | [default to undefined]
**user** | [**UserResponse**](UserResponse.md) | User information | [default to undefined]

## Example

```typescript
import { TokenResponse } from 'chatter-sdk';

const instance: TokenResponse = {
    access_token,
    refresh_token,
    token_type,
    expires_in,
    user,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
