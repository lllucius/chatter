# EmbeddingSpaceUpdate

Schema for updating an embedding space.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**reduction_strategy** | [**ReductionStrategy**](ReductionStrategy.md) |  | [optional] [default to undefined]
**reducer_path** | **string** |  | [optional] [default to undefined]
**reducer_version** | **string** |  | [optional] [default to undefined]
**normalize_vectors** | **boolean** |  | [optional] [default to undefined]
**distance_metric** | [**DistanceMetric**](DistanceMetric.md) |  | [optional] [default to undefined]
**index_type** | **string** |  | [optional] [default to undefined]
**index_config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**is_active** | **boolean** |  | [optional] [default to undefined]
**is_default** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { EmbeddingSpaceUpdate } from 'chatter-sdk';

const instance: EmbeddingSpaceUpdate = {
    display_name,
    description,
    reduction_strategy,
    reducer_path,
    reducer_version,
    normalize_vectors,
    distance_metric,
    index_type,
    index_config,
    is_active,
    is_default,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
