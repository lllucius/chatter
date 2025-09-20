# CacheStatusResponse

Schema for cache status response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cache_enabled** | **bool** | Cache enabled status | 
**cache_hits** | **int** | Cache hits | 
**cache_misses** | **int** | Cache misses | 
**cache_hit_rate** | **float** | Cache hit rate | 
**cached_items_count** | **int** | Number of cached items | 
**cache_size_mb** | **float** | Cache size in MB | 
**last_cleared** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.cache_status_response import CacheStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CacheStatusResponse from a JSON string
cache_status_response_instance = CacheStatusResponse.from_json(json)
# print the JSON string representation of the object
print(CacheStatusResponse.to_json())

# convert the object into a dict
cache_status_response_dict = cache_status_response_instance.to_dict()
# create an instance of CacheStatusResponse from a dict
cache_status_response_from_dict = CacheStatusResponse.from_dict(cache_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


