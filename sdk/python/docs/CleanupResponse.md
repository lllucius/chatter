# CleanupResponse

Schema for cleanup operation response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | **str** | Cleanup operation type | 
**items_cleaned** | **int** | Number of items cleaned | 
**storage_freed_mb** | **float** | Storage freed in MB | 
**duration_seconds** | **float** | Operation duration in seconds | 
**message** | **str** | Operation result message | 

## Example

```python
from chatter_sdk.models.cleanup_response import CleanupResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CleanupResponse from a JSON string
cleanup_response_instance = CleanupResponse.from_json(json)
# print the JSON string representation of the object
print(CleanupResponse.to_json())

# convert the object into a dict
cleanup_response_dict = cleanup_response_instance.to_dict()
# create an instance of CleanupResponse from a dict
cleanup_response_from_dict = CleanupResponse.from_dict(cleanup_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


