# ProviderCreate

Schema for creating a provider.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Unique provider name | [default to undefined]
**provider_type** | [**ProviderType**](ProviderType.md) | Type of provider | [default to undefined]
**display_name** | **string** | Human-readable name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**api_key_required** | **boolean** | Whether API key is required | [optional] [default to true]
**base_url** | **string** |  | [optional] [default to undefined]
**default_config** | **{ [key: string]: any; }** | Default configuration | [optional] [default to undefined]
**is_active** | **boolean** | Whether provider is active | [optional] [default to true]
**is_default** | **boolean** | Whether this is the default provider | [optional] [default to false]

## Example

```typescript
import { ProviderCreate } from 'chatter-sdk';

const instance: ProviderCreate = {
    name,
    provider_type,
    display_name,
    description,
    api_key_required,
    base_url,
    default_config,
    is_active,
    is_default,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
