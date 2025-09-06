# EmbeddingSpaceList

List of embedding spaces with pagination.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spaces** | [**List[EmbeddingSpaceWithModel]**](EmbeddingSpaceWithModel.md) |  | 
**total** | **int** |  | 
**page** | **int** |  | 
**per_page** | **int** |  | 

## Example

```python
from chatter_sdk.models.embedding_space_list import EmbeddingSpaceList

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingSpaceList from a JSON string
embedding_space_list_instance = EmbeddingSpaceList.from_json(json)
# print the JSON string representation of the object
print(EmbeddingSpaceList.to_json())

# convert the object into a dict
embedding_space_list_dict = embedding_space_list_instance.to_dict()
# create an instance of EmbeddingSpaceList from a dict
embedding_space_list_from_dict = EmbeddingSpaceList.from_dict(embedding_space_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


