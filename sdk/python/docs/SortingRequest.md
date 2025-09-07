# SortingRequest

Common sorting request schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sort_by** | **str** | Sort field | [optional] [default to 'created_at']
**sort_order** | **str** | Sort order | [optional] [default to 'desc']

## Example

```python
from chatter_sdk.models.sorting_request import SortingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SortingRequest from a JSON string
sorting_request_instance = SortingRequest.from_json(json)
# print the JSON string representation of the object
print(SortingRequest.to_json())

# convert the object into a dict
sorting_request_dict = sorting_request_instance.to_dict()
# create an instance of SortingRequest from a dict
sorting_request_from_dict = SortingRequest.from_dict(sorting_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


