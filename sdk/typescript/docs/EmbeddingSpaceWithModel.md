# EmbeddingSpaceWithModel

Embedding space with model and provider information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Unique space name | [default to undefined]
**display_name** | **string** | Human-readable name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**base_dimensions** | **number** | Original model dimensions | [default to undefined]
**effective_dimensions** | **number** | Effective dimensions after reduction | [default to undefined]
**reduction_strategy** | [**ReductionStrategy**](ReductionStrategy.md) | Reduction strategy | [optional] [default to undefined]
**reducer_path** | **string** |  | [optional] [default to undefined]
**reducer_version** | **string** |  | [optional] [default to undefined]
**normalize_vectors** | **boolean** | Whether to normalize vectors | [optional] [default to true]
**distance_metric** | [**DistanceMetric**](DistanceMetric.md) | Distance metric | [optional] [default to undefined]
**table_name** | **string** | Database table name | [default to undefined]
**index_type** | **string** | Index type | [optional] [default to 'hnsw']
**index_config** | **{ [key: string]: any; }** | Index configuration | [optional] [default to undefined]
**is_active** | **boolean** | Whether space is active | [optional] [default to true]
**is_default** | **boolean** | Whether this is the default space | [optional] [default to false]
**id** | **string** |  | [default to undefined]
**model_id** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**model** | [**ModelDefWithProvider**](ModelDefWithProvider.md) |  | [default to undefined]

## Example

```typescript
import { EmbeddingSpaceWithModel } from 'chatter-sdk';

const instance: EmbeddingSpaceWithModel = {
    name,
    display_name,
    description,
    base_dimensions,
    effective_dimensions,
    reduction_strategy,
    reducer_path,
    reducer_version,
    normalize_vectors,
    distance_metric,
    table_name,
    index_type,
    index_config,
    is_active,
    is_default,
    id,
    model_id,
    created_at,
    updated_at,
    model,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
