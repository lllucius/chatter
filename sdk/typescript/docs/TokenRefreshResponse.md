# TokenRefreshResponse

Schema for token refresh response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_token** | **string** | New access token | [default to undefined]
**refresh_token** | **string** | New refresh token | [default to undefined]
**token_type** | **string** | Token type | [optional] [default to 'bearer']
**expires_in** | **number** | Token expiration time in seconds | [default to undefined]

## Example

```typescript
import { TokenRefreshResponse } from 'chatter-sdk';

const instance: TokenRefreshResponse = {
    access_token,
    refresh_token,
    token_type,
    expires_in,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
