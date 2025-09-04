# ModelDefUpdate

Schema for updating a model definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**model_name** | **string** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**context_length** | **number** |  | [optional] [default to undefined]
**dimensions** | **number** |  | [optional] [default to undefined]
**chunk_size** | **number** |  | [optional] [default to undefined]
**supports_batch** | **boolean** |  | [optional] [default to undefined]
**max_batch_size** | **number** |  | [optional] [default to undefined]
**default_config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**is_active** | **boolean** |  | [optional] [default to undefined]
**is_default** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { ModelDefUpdate } from 'chatter-sdk';

const instance: ModelDefUpdate = {
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
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
