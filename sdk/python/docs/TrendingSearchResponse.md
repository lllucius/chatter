# TrendingSearchResponse

Schema for trending search response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**trending_queries** | **List[str]** | Trending search queries | 
**search_volume** | **Dict[str, int]** | Search volume by query | 
**time_period** | **str** | Time period for trending data | 
**categories** | **Dict[str, int]** | Search categories | 

## Example

```python
from chatter_sdk.models.trending_search_response import TrendingSearchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TrendingSearchResponse from a JSON string
trending_search_response_instance = TrendingSearchResponse.from_json(json)
# print the JSON string representation of the object
print(TrendingSearchResponse.to_json())

# convert the object into a dict
trending_search_response_dict = trending_search_response_instance.to_dict()
# create an instance of TrendingSearchResponse from a dict
trending_search_response_from_dict = TrendingSearchResponse.from_dict(trending_search_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


