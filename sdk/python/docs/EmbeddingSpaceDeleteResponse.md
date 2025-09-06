# EmbeddingSpaceDeleteResponse

Response schema for embedding space deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Deletion result message | 

## Example

```python
from chatter_sdk.models.embedding_space_delete_response import EmbeddingSpaceDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingSpaceDeleteResponse from a JSON string
embedding_space_delete_response_instance = EmbeddingSpaceDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(EmbeddingSpaceDeleteResponse.to_json())

# convert the object into a dict
embedding_space_delete_response_dict = embedding_space_delete_response_instance.to_dict()
# create an instance of EmbeddingSpaceDeleteResponse from a dict
embedding_space_delete_response_from_dict = EmbeddingSpaceDeleteResponse.from_dict(embedding_space_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


