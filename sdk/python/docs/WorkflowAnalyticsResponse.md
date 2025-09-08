# WorkflowAnalyticsResponse

Schema for workflow analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**complexity** | [**ComplexityMetrics**](ComplexityMetrics.md) |  | 
**bottlenecks** | [**List[BottleneckInfo]**](BottleneckInfo.md) | Identified bottlenecks | 
**optimization_suggestions** | [**List[OptimizationSuggestion]**](OptimizationSuggestion.md) | Optimization suggestions | 
**execution_paths** | **int** | Number of possible execution paths | 
**estimated_execution_time_ms** | **int** |  | [optional] 
**risk_factors** | **List[str]** | Identified risk factors | 
**total_execution_time_ms** | **int** | Total execution time | 
**error** | **str** |  | [optional] 
**started_at** | **datetime** | Execution start time | 
**completed_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_analytics_response import WorkflowAnalyticsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowAnalyticsResponse from a JSON string
workflow_analytics_response_instance = WorkflowAnalyticsResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowAnalyticsResponse.to_json())

# convert the object into a dict
workflow_analytics_response_dict = workflow_analytics_response_instance.to_dict()
# create an instance of WorkflowAnalyticsResponse from a dict
workflow_analytics_response_from_dict = WorkflowAnalyticsResponse.from_dict(workflow_analytics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


