# ModelDefCreate

Schema for creating a model definition.

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
**supports_batch** | **boolean** | Whether model supports batch operations | [optional] [default to false]
**max_batch_size** | **number** |  | [optional] [default to undefined]
**default_config** | **{ [key: string]: any; }** | Default configuration | [optional] [default to undefined]
**is_active** | **boolean** | Whether model is active | [optional] [default to true]
**is_default** | **boolean** | Whether this is the default model | [optional] [default to false]
**provider_id** | **string** | Provider ID | [default to undefined]

## Example

```typescript
import { ModelDefCreate } from 'chatter-sdk';

const instance: ModelDefCreate = {
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
    provider_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
