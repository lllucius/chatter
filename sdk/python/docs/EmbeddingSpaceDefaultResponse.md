# EmbeddingSpaceDefaultResponse

Response schema for setting default embedding space.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Operation result message | 

## Example

```python
from chatter_sdk.models.embedding_space_default_response import EmbeddingSpaceDefaultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingSpaceDefaultResponse from a JSON string
embedding_space_default_response_instance = EmbeddingSpaceDefaultResponse.from_json(json)
# print the JSON string representation of the object
print(EmbeddingSpaceDefaultResponse.to_json())

# convert the object into a dict
embedding_space_default_response_dict = embedding_space_default_response_instance.to_dict()
# create an instance of EmbeddingSpaceDefaultResponse from a dict
embedding_space_default_response_from_dict = EmbeddingSpaceDefaultResponse.from_dict(embedding_space_default_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


