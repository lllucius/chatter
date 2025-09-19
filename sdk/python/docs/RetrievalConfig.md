# RetrievalConfig

Retrieval configuration for RAG workflows.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Enable retrieval | [optional] [default to True]
**max_documents** | **int** | Max documents to retrieve | [optional] [default to 5]
**similarity_threshold** | **float** | Similarity threshold | [optional] [default to 0.7]
**document_ids** | **List[str]** |  | [optional] 
**collections** | **List[str]** |  | [optional] 
**rerank** | **bool** | Enable reranking | [optional] [default to False]

## Example

```python
from chatter_sdk.models.retrieval_config import RetrievalConfig

# TODO update the JSON string below
json = "{}"
# create an instance of RetrievalConfig from a JSON string
retrieval_config_instance = RetrievalConfig.from_json(json)
# print the JSON string representation of the object
print(RetrievalConfig.to_json())

# convert the object into a dict
retrieval_config_dict = retrieval_config_instance.to_dict()
# create an instance of RetrievalConfig from a dict
retrieval_config_from_dict = RetrievalConfig.from_dict(retrieval_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


