# EmbeddingSpaceWithModel

Embedding space with model and provider information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Unique space name | 
**display_name** | **str** | Human-readable name | 
**description** | **str** |  | [optional] 
**base_dimensions** | **int** | Original model dimensions | 
**effective_dimensions** | **int** | Effective dimensions after reduction | 
**reduction_strategy** | [**ReductionStrategy**](ReductionStrategy.md) |  | [optional] 
**reducer_path** | **str** |  | [optional] 
**reducer_version** | **str** |  | [optional] 
**normalize_vectors** | **bool** | Whether to normalize vectors | [optional] [default to True]
**distance_metric** | [**DistanceMetric**](DistanceMetric.md) |  | [optional] 
**table_name** | **str** | Database table name | 
**index_type** | **str** | Index type | [optional] [default to 'hnsw']
**index_config** | **Dict[str, object]** | Index configuration | [optional] 
**is_active** | **bool** | Whether space is active | [optional] [default to True]
**is_default** | **bool** | Whether this is the default space | [optional] [default to False]
**id** | **str** |  | 
**model_id** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**model** | [**ModelDefWithProvider**](ModelDefWithProvider.md) |  | 

## Example

```python
from chatter_sdk.models.embedding_space_with_model import EmbeddingSpaceWithModel

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingSpaceWithModel from a JSON string
embedding_space_with_model_instance = EmbeddingSpaceWithModel.from_json(json)
# print the JSON string representation of the object
print(EmbeddingSpaceWithModel.to_json())

# convert the object into a dict
embedding_space_with_model_dict = embedding_space_with_model_instance.to_dict()
# create an instance of EmbeddingSpaceWithModel from a dict
embedding_space_with_model_from_dict = EmbeddingSpaceWithModel.from_dict(embedding_space_with_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


