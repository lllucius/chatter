# OAuthConfigSchema

OAuth configuration for remote servers.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **string** | OAuth client ID | [default to undefined]
**client_secret** | **string** | OAuth client secret | [default to undefined]
**token_url** | **string** | OAuth token endpoint URL | [default to undefined]
**scope** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { OAuthConfigSchema } from 'chatter-sdk';

const instance: OAuthConfigSchema = {
    client_id,
    client_secret,
    token_url,
    scope,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
