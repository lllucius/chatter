# ModelDefWithProvider

Model definition with provider information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Model name | [default to undefined]
**model_type** | [**ModelType**](ModelType.md) | Type of model | [default to undefined]
**display_name** | **string** | Human-readable name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**model_name** | **string** | Actual model name for API calls | [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**context_length** | **number** |  | [optional] [default to undefined]
**dimensions** | **number** |  | [optional] [default to undefined]
**chunk_size** | **number** |  | [optional] [default to undefined]
**supports_batch** | **boolean** | Supports batch processing | [optional] [default to true]
**max_batch_size** | **number** |  | [optional] [default to undefined]
**default_config** | **{ [key: string]: any; }** | Default configuration | [optional] [default to undefined]
**is_active** | **boolean** | Whether model is active | [optional] [default to true]
**is_default** | **boolean** | Whether this is the default model | [optional] [default to false]
**id** | **string** |  | [default to undefined]
**provider_id** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**provider** | [**Provider**](Provider.md) |  | [default to undefined]

## Example

```typescript
import { ModelDefWithProvider } from 'chatter-sdk';

const instance: ModelDefWithProvider = {
    name,
    model_type,
    display_name,
    description,
    model_name,
    max_tokens,
    context_length,
    dimensions,
    chunk_size,
    supports_batch,
    max_batch_size,
    default_config,
    is_active,
    is_default,
    id,
    provider_id,
    created_at,
    updated_at,
    provider,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
