# QueryAnalysisResponse

Schema for database query analysis response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_queries_analyzed** | **int** | Total queries analyzed | 
**slow_queries_count** | **int** | Number of slow queries | 
**optimization_suggestions** | **List[str]** | Optimization suggestions | 
**average_execution_time_ms** | **float** | Average execution time in milliseconds | 
**most_expensive_queries** | **List[Dict[str, object]]** | Most expensive queries | 
**index_recommendations** | **List[str]** | Index recommendations | 

## Example

```python
from chatter_sdk.models.query_analysis_response import QueryAnalysisResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryAnalysisResponse from a JSON string
query_analysis_response_instance = QueryAnalysisResponse.from_json(json)
# print the JSON string representation of the object
print(QueryAnalysisResponse.to_json())

# convert the object into a dict
query_analysis_response_dict = query_analysis_response_instance.to_dict()
# create an instance of QueryAnalysisResponse from a dict
query_analysis_response_from_dict = QueryAnalysisResponse.from_dict(query_analysis_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


