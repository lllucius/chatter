# UsageMetricsResponse

Schema for usage metrics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_prompt_tokens** | **int** | Total prompt tokens | 
**total_completion_tokens** | **int** | Total completion tokens | 
**total_tokens** | **int** | Total tokens used | 
**tokens_by_model** | **Dict[str, int]** | Token usage by model | 
**tokens_by_provider** | **Dict[str, int]** | Token usage by provider | 
**total_cost** | **float** | Total cost | 
**cost_by_model** | **Dict[str, float]** | Cost by model | 
**cost_by_provider** | **Dict[str, float]** | Cost by provider | 
**daily_usage** | **Dict[str, int]** | Daily token usage | 
**daily_cost** | **Dict[str, float]** | Daily cost | 
**avg_response_time** | **float** | Average response time | 
**response_times_by_model** | **Dict[str, float]** | Response times by model | 
**active_days** | **int** | Number of active days | 
**peak_usage_hour** | **int** | Peak usage hour | 
**conversations_per_day** | **float** | Average conversations per day | 

## Example

```python
from chatter_sdk.models.usage_metrics_response import UsageMetricsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UsageMetricsResponse from a JSON string
usage_metrics_response_instance = UsageMetricsResponse.from_json(json)
# print the JSON string representation of the object
print(UsageMetricsResponse.to_json())

# convert the object into a dict
usage_metrics_response_dict = usage_metrics_response_instance.to_dict()
# create an instance of UsageMetricsResponse from a dict
usage_metrics_response_from_dict = UsageMetricsResponse.from_dict(usage_metrics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


