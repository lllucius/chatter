# EmbeddingSpaceUpdate

Schema for updating an embedding space.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**reduction_strategy** | [**ReductionStrategy**](ReductionStrategy.md) |  | [optional] 
**reducer_path** | **str** |  | [optional] 
**reducer_version** | **str** |  | [optional] 
**normalize_vectors** | **bool** |  | [optional] 
**distance_metric** | [**DistanceMetric**](DistanceMetric.md) |  | [optional] 
**index_type** | **str** |  | [optional] 
**index_config** | **Dict[str, object]** |  | [optional] 
**is_active** | **bool** |  | [optional] 
**is_default** | **bool** |  | [optional] 

## Example

```python
from chatter_sdk.models.embedding_space_update import EmbeddingSpaceUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingSpaceUpdate from a JSON string
embedding_space_update_instance = EmbeddingSpaceUpdate.from_json(json)
# print the JSON string representation of the object
print(EmbeddingSpaceUpdate.to_json())

# convert the object into a dict
embedding_space_update_dict = embedding_space_update_instance.to_dict()
# create an instance of EmbeddingSpaceUpdate from a dict
embedding_space_update_from_dict = EmbeddingSpaceUpdate.from_dict(embedding_space_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


