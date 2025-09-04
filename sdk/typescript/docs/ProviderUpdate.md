# ProviderUpdate

Schema for updating a provider.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**api_key_required** | **boolean** |  | [optional] [default to undefined]
**base_url** | **string** |  | [optional] [default to undefined]
**default_config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**is_active** | **boolean** |  | [optional] [default to undefined]
**is_default** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { ProviderUpdate } from 'chatter-sdk';

const instance: ProviderUpdate = {
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
